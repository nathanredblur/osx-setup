"""
User Interface for MacSnap Setup.

This module provides:
- Two-column layout: left sidebar (categories) and main content area (items)
- Category navigation with alphabetical sorting
- Item display with status indicators and descriptions
- Multi-selection support for batch operations
- Action buttons and progress display
- Error handling and recovery suggestions
"""

import curses
import sys
import os
import platform
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .config_loader import ConfigItem, ConfigLoader
from .installer import InstallationEngine, ExecutionResult, OperationResult
from .logger import MacSnapLogger, get_logger

class UIState(Enum):
    """States of the user interface."""
    CATEGORY_SELECTION = "category_selection"
    ITEM_SELECTION = "item_selection"
    CONFIRMATION = "confirmation"
    INSTALLATION = "installation"
    RESULTS = "results"
    ERROR = "error"

class ItemStatus(Enum):
    """Status of items for display."""
    UNKNOWN = "unknown"
    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    SELECTED = "selected"
    INSTALLING = "installing"
    FAILED = "failed"

@dataclass
class UIItem:
    """UI representation of a configuration item."""
    config: ConfigItem
    status: ItemStatus
    selected: bool = False
    description_lines: List[str] = None
    
    def __post_init__(self):
        if self.description_lines is None:
            self.description_lines = self._wrap_description()
    
    def _wrap_description(self, width: int = 50) -> List[str]:
        """Wrap description text to fit in the display area."""
        if not self.config.description:
            return ["No description available."]
        
        words = self.config.description.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines or ["No description available."]

class MacSnapUI:
    """
    Terminal user interface for MacSnap Setup.
    
    Features:
    - Two-column layout with category sidebar and item content area
    - Interactive navigation with keyboard controls
    - Real-time status checking and progress display
    - Multi-selection support for batch operations
    - Colored output and status indicators
    """
    
    def __init__(self, config_loader: ConfigLoader, verbose: bool = False):
        """
        Initialize the MacSnap UI.
        
        Args:
            config_loader: Loaded configuration data
            verbose: Enable verbose logging
        """
        self.config_loader = config_loader
        self.verbose = verbose
        self.logger = get_logger(verbose=verbose)
        self.engine = InstallationEngine(verbose=verbose)
        
        # UI state
        self.state = UIState.CATEGORY_SELECTION
        self.categories = sorted(config_loader.categories)
        self.current_category_index = 0
        self.current_item_index = 0
        self.selected_items: Set[str] = set()
        
        # UI items by category
        self.ui_items: Dict[str, List[UIItem]] = {}
        self._initialize_ui_items()
        
        # Screen dimensions and layout
        self.screen = None
        self.height = 0
        self.width = 0
        self.sidebar_width = 20
        self.header_height = 3
        
        # Colors
        self.colors_initialized = False
        
        # Progress tracking
        self.installation_progress: List[str] = []
        self.current_operation = ""
    
    def _initialize_ui_items(self):
        """Initialize UI items grouped by category."""
        for category in self.categories:
            self.ui_items[category] = []
            
            for config in self.config_loader.configurations.values():
                if config.category == category:
                    ui_item = UIItem(
                        config=config,
                        status=ItemStatus.UNKNOWN,
                        selected=config.selected_by_default
                    )
                    self.ui_items[category].append(ui_item)
                    
                    if config.selected_by_default:
                        self.selected_items.add(config.id)
            
            # Sort items alphabetically within each category
            self.ui_items[category].sort(key=lambda x: x.config.name)
    
    def _init_colors(self):
        """Initialize color pairs for the UI."""
        if not self.colors_initialized and curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            
            # Define color pairs
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Header
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected
            curses.init_pair(3, curses.COLOR_GREEN, -1)                   # Installed
            curses.init_pair(4, curses.COLOR_RED, -1)                     # Failed
            curses.init_pair(5, curses.COLOR_YELLOW, -1)                  # Warning
            curses.init_pair(6, curses.COLOR_CYAN, -1)                    # Info
            curses.init_pair(7, curses.COLOR_MAGENTA, -1)                 # Selected item
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_RED)     # Error
            
            self.colors_initialized = True
    
    def run(self) -> bool:
        """
        Run the MacSnap UI.
        
        Returns:
            True if operations completed successfully, False otherwise
        """
        try:
            return curses.wrapper(self._main_loop)
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return False
        except Exception as e:
            self.logger.error(f"UI error: {e}")
            return False
    
    def _main_loop(self, stdscr) -> bool:
        """Main UI loop."""
        self.screen = stdscr
        self._init_colors()
        curses.curs_set(0)  # Hide cursor
        
        # Initial setup
        self._update_screen_size()
        self._check_initial_status()
        
        while True:
            self._draw_screen()
            self._handle_input()
            
            if self.state == UIState.RESULTS:
                # Show results and ask if user wants to continue
                self._draw_screen()
                self.screen.getch()  # Wait for any key
                break
        
        return True
    
    def _update_screen_size(self):
        """Update screen dimensions."""
        self.height, self.width = self.screen.getmaxyx()
        
        # Adjust sidebar width based on screen size
        if self.width < 80:
            self.sidebar_width = max(15, self.width // 4)
        else:
            self.sidebar_width = 20
    
    def _check_initial_status(self):
        """Check initial installation status for all items."""
        self.logger.debug("Checking initial installation status...")
        
        total_items = sum(len(items) for items in self.ui_items.values())
        checked = 0
        
        for category in self.categories:
            for ui_item in self.ui_items[category]:
                result = self.engine.check_install_status(ui_item.config)
                ui_item.status = (ItemStatus.INSTALLED if result.result == OperationResult.SUCCESS 
                                else ItemStatus.NOT_INSTALLED)
                checked += 1
                
                # Update progress (could show a progress bar here)
                if checked % 3 == 0:  # Update every 3 items to avoid too much redrawing
                    self._draw_loading_screen(f"Checking status... {checked}/{total_items}")
        
        self.logger.debug(f"Status check completed for {total_items} items")
    
    def _draw_screen(self):
        """Draw the entire screen based on current state."""
        self.screen.clear()
        
        if self.state == UIState.INSTALLATION:
            self._draw_installation_screen()
        elif self.state == UIState.RESULTS:
            self._draw_results_screen()
        elif self.state == UIState.ERROR:
            self._draw_error_screen()
        else:
            self._draw_main_screen()
        
        self.screen.refresh()
    
    def _draw_main_screen(self):
        """Draw the main two-column interface."""
        # Draw header
        self._draw_header()
        
        # Draw vertical separator
        for y in range(self.header_height, self.height - 1):
            self.screen.addch(y, self.sidebar_width, '│')
        
        # Draw sidebar (categories)
        self._draw_sidebar()
        
        # Draw main content area (items)
        self._draw_content_area()
        
        # Draw footer with instructions
        self._draw_footer()
    
    def _draw_header(self):
        """Draw the header section."""
        if self.height < 10 or self.width < 50:
            return  # Skip header if screen too small
        
        # Title
        title = "MacSnap Setup v1.0"
        user_info = f"macOS {platform.mac_ver()[0]} | User: {os.getenv('USER', 'unknown')}"
        
        if self.colors_initialized:
            self.screen.attron(curses.color_pair(1) | curses.A_BOLD)
        
        # Center title
        title_x = max(0, (self.width - len(title)) // 2)
        self.screen.addstr(0, title_x, title)
        
        # Right-align user info
        user_x = max(0, self.width - len(user_info) - 1)
        self.screen.addstr(1, user_x, user_info)
        
        if self.colors_initialized:
            self.screen.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # Horizontal separator
        self.screen.addstr(2, 0, "─" * self.width)
    
    def _draw_sidebar(self):
        """Draw the categories sidebar."""
        if not self.categories:
            return
        
        start_y = self.header_height + 1
        max_visible = self.height - self.header_height - 3
        
        # Title
        self.screen.addstr(start_y, 2, "Categories", curses.A_BOLD)
        
        # Categories list
        for i, category in enumerate(self.categories):
            if i >= max_visible - 2:
                break
            
            y = start_y + 2 + i
            x = 2
            
            # Truncate category name if too long
            display_name = category
            max_name_width = self.sidebar_width - 4
            if len(display_name) > max_name_width:
                display_name = display_name[:max_name_width-3] + "..."
            
            # Highlight current category
            if i == self.current_category_index:
                if self.colors_initialized:
                    self.screen.attron(curses.color_pair(2))
                self.screen.addstr(y, x, f"> {display_name}")
                if self.colors_initialized:
                    self.screen.attroff(curses.color_pair(2))
            else:
                self.screen.addstr(y, x, f"  {display_name}")
        
        # Show selection count
        selected_count = len(self.selected_items)
        if selected_count > 0:
            count_text = f"Selected: {selected_count}"
            count_y = self.height - 2
            self.screen.addstr(count_y, 2, count_text)
    
    def _draw_content_area(self):
        """Draw the main content area with items."""
        if not self.categories:
            return
        
        current_category = self.categories[self.current_category_index]
        items = self.ui_items.get(current_category, [])
        
        start_x = self.sidebar_width + 2
        start_y = self.header_height + 1
        content_width = self.width - start_x - 2
        max_visible = self.height - self.header_height - 3
        
        # Category title
        self.screen.addstr(start_y, start_x, f"{current_category} ({len(items)} items)", curses.A_BOLD)
        
        if not items:
            self.screen.addstr(start_y + 2, start_x, "No items in this category.")
            return
        
        # Calculate scroll offset
        scroll_offset = max(0, self.current_item_index - max_visible + 4)
        
        # Draw items
        for i, ui_item in enumerate(items[scroll_offset:scroll_offset + max_visible - 3]):
            actual_index = i + scroll_offset
            item = ui_item.config
            
            y = start_y + 2 + i
            
            # Status indicator
            status_char = self._get_status_char(ui_item)
            status_color = self._get_status_color(ui_item)
            
            # Selection indicator
            selection_char = "☑" if ui_item.selected else "☐"
            
            if self.colors_initialized and status_color:
                self.screen.attron(status_color)
            
            # Highlight current item
            is_current = actual_index == self.current_item_index
            if is_current and self.colors_initialized:
                self.screen.attron(curses.color_pair(2))
            
            # Item name (truncated if necessary)
            max_name_width = content_width - 10
            display_name = item.name
            if len(display_name) > max_name_width:
                display_name = display_name[:max_name_width-3] + "..."
            
            item_text = f"{selection_char} {status_char} {display_name}"
            self.screen.addstr(y, start_x, item_text)
            
            if is_current and self.colors_initialized:
                self.screen.attroff(curses.color_pair(2))
            
            if self.colors_initialized and status_color:
                self.screen.attroff(status_color)
        
        # Draw description for current item
        if items and 0 <= self.current_item_index < len(items):
            current_item = items[self.current_item_index]
            self._draw_item_description(current_item, start_x, start_y + max_visible)
    
    def _draw_item_description(self, ui_item: UIItem, start_x: int, start_y: int):
        """Draw the description for the current item."""
        if start_y >= self.height - 2:
            return
        
        # Description box
        desc_lines = ui_item.description_lines
        box_height = min(len(desc_lines) + 2, self.height - start_y - 1)
        content_width = self.width - start_x - 2
        
        # Draw description title
        title = f"Description: {ui_item.config.name}"
        if len(title) > content_width:
            title = title[:content_width-3] + "..."
        
        self.screen.addstr(start_y, start_x, title, curses.A_BOLD)
        
        # Draw description lines
        for i, line in enumerate(desc_lines[:box_height-2]):
            if start_y + 1 + i >= self.height:
                break
            
            # Truncate line if too long
            if len(line) > content_width:
                line = line[:content_width-3] + "..."
            
            self.screen.addstr(start_y + 1 + i, start_x, line)
    
    def _draw_footer(self):
        """Draw footer with instructions."""
        if self.height < 5:
            return
        
        footer_y = self.height - 1
        
        if self.state == UIState.CATEGORY_SELECTION:
            instructions = "↑↓: Navigate  Tab: Switch to items  Space: Select  Enter: Install  Q: Quit"
        elif self.state == UIState.ITEM_SELECTION:
            instructions = "↑↓: Navigate  Tab: Categories  Space: Toggle  Enter: Install  Q: Quit"
        else:
            instructions = "Q: Quit"
        
        # Truncate if too long
        if len(instructions) > self.width:
            instructions = instructions[:self.width-3] + "..."
        
        self.screen.addstr(footer_y, 0, instructions)
    
    def _get_status_char(self, ui_item: UIItem) -> str:
        """Get status character for an item."""
        if ui_item.status == ItemStatus.INSTALLED:
            return "✓"
        elif ui_item.status == ItemStatus.FAILED:
            return "✗"
        elif ui_item.status == ItemStatus.INSTALLING:
            return "⏳"
        elif ui_item.status == ItemStatus.NOT_INSTALLED:
            return "○"
        else:
            return "?"
    
    def _get_status_color(self, ui_item: UIItem) -> Optional[int]:
        """Get color for item status."""
        if not self.colors_initialized:
            return None
        
        if ui_item.status == ItemStatus.INSTALLED:
            return curses.color_pair(3)  # Green
        elif ui_item.status == ItemStatus.FAILED:
            return curses.color_pair(4)  # Red
        elif ui_item.status == ItemStatus.INSTALLING:
            return curses.color_pair(5)  # Yellow
        elif ui_item.selected:
            return curses.color_pair(7)  # Magenta
        
        return None
    
    def _draw_loading_screen(self, message: str):
        """Draw a loading screen with message."""
        self.screen.clear()
        
        center_y = self.height // 2
        center_x = max(0, (self.width - len(message)) // 2)
        
        self.screen.addstr(center_y, center_x, message)
        self.screen.refresh()
    
    def _draw_installation_screen(self):
        """Draw installation progress screen."""
        self.screen.clear()
        
        # Title
        title = "Installing Selected Items"
        title_x = max(0, (self.width - len(title)) // 2)
        self.screen.addstr(2, title_x, title, curses.A_BOLD)
        
        # Current operation
        if self.current_operation:
            op_y = 4
            op_x = max(0, (self.width - len(self.current_operation)) // 2)
            self.screen.addstr(op_y, op_x, self.current_operation)
        
        # Progress log
        start_y = 6
        max_lines = self.height - start_y - 3
        
        for i, line in enumerate(self.installation_progress[-max_lines:]):
            if start_y + i < self.height - 2:
                # Truncate long lines
                if len(line) > self.width - 2:
                    line = line[:self.width-5] + "..."
                self.screen.addstr(start_y + i, 1, line)
        
        # Instructions
        instructions = "Installation in progress... Please wait."
        instr_y = self.height - 1
        self.screen.addstr(instr_y, 1, instructions)
    
    def _draw_results_screen(self):
        """Draw installation results screen."""
        self.screen.clear()
        
        # Title
        title = "Installation Complete"
        title_x = max(0, (self.width - len(title)) // 2)
        if self.colors_initialized:
            self.screen.attron(curses.color_pair(1) | curses.A_BOLD)
        self.screen.addstr(2, title_x, title)
        if self.colors_initialized:
            self.screen.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # Summary
        summary = self.engine.get_installation_summary()
        start_y = 4
        
        lines = [
            f"Total operations: {summary['total_operations']}",
            f"Successful: {summary.get('installed_items', 0)}",
            f"Failed: {summary.get('failed_items', 0)}",
            f"Skipped: {summary.get('skipped_items', 0)}",
            f"Duration: {summary.get('total_duration', 0):.1f}s"
        ]
        
        for i, line in enumerate(lines):
            if start_y + i < self.height - 3:
                line_x = max(0, (self.width - len(line)) // 2)
                self.screen.addstr(start_y + i, line_x, line)
        
        # Failed items
        failed_items = summary.get('failed_item_ids', [])
        if failed_items:
            fail_y = start_y + len(lines) + 2
            self.screen.addstr(fail_y, 2, "Failed items:", curses.A_BOLD)
            for i, item_id in enumerate(failed_items[:5]):  # Show max 5
                if fail_y + 1 + i < self.height - 2:
                    self.screen.addstr(fail_y + 1 + i, 4, f"- {item_id}")
        
        # Instructions
        instructions = "Press any key to exit..."
        instr_y = self.height - 1
        instr_x = max(0, (self.width - len(instructions)) // 2)
        self.screen.addstr(instr_y, instr_x, instructions)
    
    def _draw_error_screen(self):
        """Draw error screen."""
        self.screen.clear()
        
        title = "Error"
        title_x = max(0, (self.width - len(title)) // 2)
        if self.colors_initialized:
            self.screen.attron(curses.color_pair(8) | curses.A_BOLD)
        self.screen.addstr(2, title_x, title)
        if self.colors_initialized:
            self.screen.attroff(curses.color_pair(8) | curses.A_BOLD)
        
        error_msg = "An error occurred during installation."
        error_x = max(0, (self.width - len(error_msg)) // 2)
        self.screen.addstr(4, error_x, error_msg)
        
        instructions = "Press any key to continue..."
        instr_y = self.height - 1
        instr_x = max(0, (self.width - len(instructions)) // 2)
        self.screen.addstr(instr_y, instr_x, instructions)
    
    def _handle_input(self):
        """Handle keyboard input."""
        try:
            key = self.screen.getch()
        except:
            return
        
        if key == ord('q') or key == ord('Q'):
            sys.exit(0)
        elif key == curses.KEY_UP:
            self._handle_up()
        elif key == curses.KEY_DOWN:
            self._handle_down()
        elif key == ord('\t'):  # Tab
            self._handle_tab()
        elif key == ord(' '):  # Space
            self._handle_space()
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10 or key == 13:
            self._handle_enter()
    
    def _handle_up(self):
        """Handle up arrow key."""
        if self.state == UIState.CATEGORY_SELECTION:
            self.current_category_index = max(0, self.current_category_index - 1)
            self.current_item_index = 0
        elif self.state == UIState.ITEM_SELECTION:
            current_category = self.categories[self.current_category_index]
            items = self.ui_items.get(current_category, [])
            if items:
                self.current_item_index = max(0, self.current_item_index - 1)
    
    def _handle_down(self):
        """Handle down arrow key."""
        if self.state == UIState.CATEGORY_SELECTION:
            self.current_category_index = min(len(self.categories) - 1, 
                                            self.current_category_index + 1)
            self.current_item_index = 0
        elif self.state == UIState.ITEM_SELECTION:
            current_category = self.categories[self.current_category_index]
            items = self.ui_items.get(current_category, [])
            if items:
                self.current_item_index = min(len(items) - 1, self.current_item_index + 1)
    
    def _handle_tab(self):
        """Handle tab key to switch between categories and items."""
        if self.state == UIState.CATEGORY_SELECTION:
            self.state = UIState.ITEM_SELECTION
        elif self.state == UIState.ITEM_SELECTION:
            self.state = UIState.CATEGORY_SELECTION
    
    def _handle_space(self):
        """Handle space key for selection."""
        if self.state == UIState.ITEM_SELECTION:
            current_category = self.categories[self.current_category_index]
            items = self.ui_items.get(current_category, [])
            
            if items and 0 <= self.current_item_index < len(items):
                ui_item = items[self.current_item_index]
                ui_item.selected = not ui_item.selected
                
                if ui_item.selected:
                    self.selected_items.add(ui_item.config.id)
                else:
                    self.selected_items.discard(ui_item.config.id)
    
    def _handle_enter(self):
        """Handle enter key for installation."""
        if not self.selected_items:
            return
        
        self.state = UIState.INSTALLATION
        self._run_installation()
    
    def _run_installation(self):
        """Run the installation process."""
        self.installation_progress.clear()
        self.current_operation = "Preparing installation..."
        
        try:
            # Get selected configurations
            selected_configs = {
                item_id: self.config_loader.configurations[item_id]
                for item_id in self.selected_items
                if item_id in self.config_loader.configurations
            }
            
            self.installation_progress.append(f"Installing {len(selected_configs)} items...")
            self._draw_screen()
            
            # Run batch installation
            results = self.engine.batch_process(
                self.config_loader.configurations,
                list(self.selected_items),
                "install"
            )
            
            # Update UI item statuses based on results
            for result in results:
                for category_items in self.ui_items.values():
                    for ui_item in category_items:
                        if ui_item.config.id == result.item_id:
                            if result.result == OperationResult.SUCCESS:
                                ui_item.status = ItemStatus.INSTALLED
                            elif result.result == OperationResult.ALREADY_INSTALLED:
                                ui_item.status = ItemStatus.INSTALLED
                            else:
                                ui_item.status = ItemStatus.FAILED
            
            self.state = UIState.RESULTS
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self.installation_progress.append(f"ERROR: {e}")
            self.state = UIState.ERROR


# Convenience function for running the UI
def run_macsnap_ui(verbose: bool = False) -> bool:
    """
    Run the MacSnap UI with loaded configurations.
    
    Args:
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from .config_loader import load_configs
        
        # Load configurations
        loader = load_configs('configs')
        
        if not loader.configurations:
            print("No configurations found. Please check the configs/ directory.")
            return False
        
        # Create and run UI
        ui = MacSnapUI(loader, verbose=verbose)
        return ui.run()
        
    except Exception as e:
        print(f"Failed to start MacSnap UI: {e}")
        return False 