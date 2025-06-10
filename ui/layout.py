"""
Main Layout Component for MacSnap UI
"""

import sys
from typing import Dict, List, Set
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.binding import Binding

from utils.config_loader import ConfigLoader, ConfigItem
from utils.installer import InstallationEngine
from utils.logger import get_logger

# Import UI components
from .styles import LAYOUT_CSS
from .category_list import CategoryList, CategorySelected, FocusItemTable
from .item_list import ItemButtonList, ItemSelected, ItemToggled, FocusCategoryList
from .item_detail import ItemDetailPanel
from .action_buttons import ActionButtons


# Import shared UI models
from .models import UIItem, ItemStatus


class MacSnapApp(App):
    """
    Main MacSnap Setup application using Textual.
    
    A modern, rich terminal interface for macOS software installation.
    """
    
    # Use native Tokyo Night theme instead of custom CSS
    DARK = True
    CSS = LAYOUT_CSS  # Only structural layout, theme handles colors
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("i", "install", "Install Selected"),
        Binding("space", "toggle_item_selection", "Toggle Selection", show=False),
        Binding("ctrl+a", "select_all", "Select All"),
        Binding("ctrl+d", "deselect_all", "Deselect All"),
        Binding("tab", "focus_next", "Focus Next"),
        Binding("shift+tab", "focus_previous", "Focus Previous"),
        Binding("escape", "focus_categories", "Focus Categories"),
        Binding("backspace", "focus_categories", "Focus Categories"),
    ]
    
    def __init__(self, config_loader: ConfigLoader, verbose: bool = False):
        super().__init__()
        self.config_loader = config_loader
        self.verbose = verbose
        self.logger = get_logger(verbose=verbose)
        self.engine = InstallationEngine(verbose=verbose)
        
        # UI state
        regular_categories = sorted(config_loader.categories)
        self.categories = ["All"] + regular_categories
        self.ui_items: Dict[str, List[UIItem]] = {}
        self.current_category = self.categories[0] if self.categories else ""
        self.selected_items: Set[str] = set()
        
        # Pending operations (executed after UI closes)
        self._pending_installation = None
        self._pending_uninstallation = None
        
        # Initialize UI items
        self._initialize_ui_items()
    
    def _initialize_ui_items(self):
        """Initialize UI items grouped by category."""
        # First initialize regular categories
        for category in self.categories:
            if category == "All":
                continue  # Skip "All" for now, handle it separately
                
            # Use the config_loader's method to get items by category (already sorted)
            category_configs = self.config_loader.get_items_by_category(category)
            
            ui_items = []
            for config in category_configs:
                ui_item = UIItem(
                    config=config,
                    status=ItemStatus.UNKNOWN,
                    selected=config.selected_by_default
                )
                ui_items.append(ui_item)
                
                if config.selected_by_default:
                    self.selected_items.add(config.id)
            
            self.ui_items[category] = ui_items
        
        # Create "All" category with all items
        self._create_all_category()
    
    def _create_all_category(self):
        """Create the 'All' category with all items sorted by category then name."""
        all_items = []
        seen_ids = set()
        
        # Collect all items from all categories, avoiding duplicates
        for category in self.categories:
            if category == "All":
                continue
            
            for ui_item in self.ui_items[category]:
                # Only add if we haven't seen this item ID before
                if ui_item.config.id not in seen_ids:
                    all_items.append(ui_item)
                    seen_ids.add(ui_item.config.id)
        
        # Sort first by category, then by name
        all_items.sort(key=lambda x: (x.config.category, x.config.name))
        
        self.ui_items["All"] = all_items
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # Left sidebar with categories
            with Container(id="category-sidebar"):
                yield CategoryList(self.categories, self.ui_items)
            
            # Main content area
            with Vertical(id="content-area"):
                # Item table
                yield ItemButtonList(id="item-table")
                
                # Item detail panel
                yield ItemDetailPanel("Select an item to view details", id="item-detail")
        
        # Control panel
        with Container(id="control-panel"):
            yield ActionButtons()
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app after mounting."""
        try:
            # Set native Tokyo Night theme
            self.theme = "tokyo-night"
            
            # Load initial data for the first category
            if self.categories:
                await self._load_category_data(self.current_category)
            
            # Check initial installation status
            self.run_worker(self._check_initial_status())
        except Exception as e:
            error_msg = f"Failed to initialize app: {e}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self.notify(error_msg, severity="error")
    
    async def on_category_selected(self, event: CategorySelected) -> None:
        """Handle category selection from sidebar."""
        await self._switch_category(event.category)
    
    def on_focus_item_table(self, event: FocusItemTable) -> None:
        """Handle focus request for items table."""
        try:
            item_table = self.query_one("#item-table", ItemButtonList)
            item_table.focus()
            self.logger.debug("Focus moved to items table")
        except Exception as e:
            self.logger.debug(f"Could not focus items table: {e}")
    
    def on_focus_category_list(self, event: FocusCategoryList) -> None:
        """Handle focus request for category list."""
        try:
            category_list = self.query_one(CategoryList)
            category_list.focus()
            self.logger.debug("Focus moved to category list")
        except Exception as e:
            self.logger.debug(f"Could not focus category list: {e}")
    
    def on_item_selected(self, event: ItemSelected) -> None:
        """Handle item selection/focus event."""
        try:
            detail_panel = self.query_one("#item-detail", ItemDetailPanel)
            detail_panel.item = event.item
            self.logger.debug(f"Item selected: {event.item.config.name}")
        except Exception as e:
            self.logger.error(f"Failed to update item detail: {e}")
    
    def on_item_toggled(self, event: ItemToggled) -> None:
        """Handle item selection toggle."""
        try:
            # Update global selected items
            if event.selected:
                self.selected_items.add(event.item_id)
            else:
                self.selected_items.discard(event.item_id)
            
            # CRITICAL: Update the actual UIItem objects in our data store
            for category_items in self.ui_items.values():
                for ui_item in category_items:
                    if ui_item.config.id == event.item_id:
                        ui_item.selected = event.selected
            
            self._update_selection_count()
            self.logger.debug(f"Item {event.item_id} {'selected' if event.selected else 'deselected'}")
        except Exception as e:
            self.logger.error(f"Failed to handle item toggle: {e}")
    
    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        try:
            if event.button.id == "refresh-btn":
                self.action_refresh()
            elif event.button.id == "install-btn":
                self.action_install()
            elif event.button.id == "uninstall-btn":
                self.action_remove()
            elif event.button.id == "select-all-btn":
                self.run_worker(self.action_select_all())
            elif event.button.id == "deselect-all-btn":
                self.run_worker(self.action_deselect_all())
        except Exception as e:
            error_msg = f"Button press error: {e}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self.notify(error_msg, severity="error")
    
    async def _load_category_data(self, category: str):
        """Load data for a specific category."""
        items = self.ui_items.get(category, [])
        item_table = self.query_one("#item-table", ItemButtonList)
        
        # Show category names when in "All" view
        show_category = (category == "All")
        await item_table.add_items(items, show_category=show_category)
        
        # Show details for first item if available
        if items:
            detail_panel = self.query_one("#item-detail", ItemDetailPanel)
            detail_panel.item = items[0]
        
        # Update selected items count
        self._update_selection_count()
    
    def _update_selection_count(self):
        """Update the selection count display."""
        selected_count = len(self.selected_items)
        self.logger.debug(f"Selected items: {selected_count}")
    
    async def _switch_category(self, category: str):
        """Switch to a different category."""
        if category in self.categories:
            self.current_category = category
            await self._load_category_data(category)
            
            # Update category list selection
            try:
                category_list = self.query_one(CategoryList)
                category_list.set_selected_category(category)
            except Exception as e:
                self.logger.debug(f"Could not update category selection: {e}")
    
    # Placeholder action methods (will be moved to a separate controller)
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_refresh(self) -> None:
        """Refresh installation status."""
        self.run_worker(self._check_initial_status())
    
    def action_install(self) -> None:
        """Install selected items."""
        if not self.selected_items:
            self.notify("No items selected for installation", severity="warning")
            return
        
        # Show confirmation and run installation
        selected_count = len(self.selected_items)
        self.notify(f"Starting installation of {selected_count} items...", severity="information")
        self.run_worker(self._run_installation())
    
    def action_remove(self) -> None:
        """Remove/uninstall selected items."""
        if not self.selected_items:
            self.notify("No items selected for removal", severity="warning")
            return
        
        # Show confirmation and run removal
        selected_count = len(self.selected_items)
        self.notify(f"Starting removal of {selected_count} items...", severity="information")
        self.run_worker(self._run_uninstallation())
    
    async def action_select_all(self) -> None:
        """Select all items in current category."""
        items = self.ui_items.get(self.current_category, [])
        if not items:
            self.notify("No items in current category", severity="warning")
            return
            
        selected_count = 0
        for item in items:
            if not item.selected:
                item.selected = True
                self.selected_items.add(item.config.id)
                selected_count += 1
                
                # If we're in "All" view, also update the item in its original category
                if self.current_category == "All":
                    self._update_item_in_original_category(item.config.id, selected=True)
        
        # Regenerate "All" category if needed
        if self.current_category == "All":
            self._create_all_category()
        
        # Refresh current category display
        await self._load_category_data(self.current_category)
        self.notify(f"Selected {selected_count} items in {self.current_category}", severity="information")
    
    async def action_deselect_all(self) -> None:
        """Deselect all items."""
        deselected_count = 0
        
        # Deselect all items across all categories
        for category_items in self.ui_items.values():
            for item in category_items:
                if item.selected:
                    item.selected = False
                    deselected_count += 1
        
        # Clear global selected items
        self.selected_items.clear()
        
        # Regenerate "All" category
        self._create_all_category()
        
        # Refresh current category display
        await self._load_category_data(self.current_category)
        self.notify(f"Deselected {deselected_count} items", severity="information")
    
    def action_focus_categories(self) -> None:
        """Focus the category list."""
        try:
            category_list = self.query_one(CategoryList)
            category_list.focus()
        except Exception as e:
            self.logger.debug(f"Could not focus categories: {e}")
    
    def action_toggle_item_selection(self) -> None:
        """Toggle selection of the currently highlighted item."""
        try:
            # Check if the item table has focus
            item_table = self.query_one("#item-table", ItemButtonList)
            if item_table.has_focus:
                item_table.action_toggle_selection()
        except Exception as e:
            self.logger.debug(f"Could not toggle item selection: {e}")
    
    async def _check_initial_status(self) -> None:
        """Check initial installation status for all items."""
        self.notify("Checking installation status...")
        
        total_items = sum(len(items) for items in self.ui_items.values() if items)
        checked = 0
        
        for category in self.categories:
            if category == "All":
                continue  # Skip "All" category to avoid duplicates
                
            for ui_item in self.ui_items.get(category, []):
                try:
                    result = self.engine.check_install_status(ui_item.config)
                    ui_item.status = (ItemStatus.INSTALLED if result.result.name == "SUCCESS" 
                                    else ItemStatus.NOT_INSTALLED)
                    checked += 1
                    
                    # Update UI periodically
                    if checked % 5 == 0:
                        progress = (checked / total_items) * 100 if total_items > 0 else 0
                        self.notify(f"Checking status... {checked}/{total_items} ({progress:.0f}%)")
                        
                except Exception as e:
                    self.logger.debug(f"Failed to check status for {ui_item.config.name}: {e}")
                    ui_item.status = ItemStatus.UNKNOWN
                    checked += 1
        
        # Regenerate "All" category to reflect status changes
        self._create_all_category()
        
        # Refresh current category to show updated status
        await self._load_category_data(self.current_category)
        self.notify("Status check completed", severity="information")
    
    def _run_installation(self) -> None:
        """Run installation process by exiting UI and running in terminal."""
        try:
            # Get configurations for selected items
            configs_to_install = {}
            selected_names = []
            for item_id in self.selected_items:
                config = self.config_loader.configurations.get(item_id)
                if config:
                    configs_to_install[item_id] = config
                    selected_names.append(config.name)
            
            if not configs_to_install:
                self.notify("No valid configurations found for selected items", severity="error")
                return
            
            # Store configs for execution after UI closes
            self._pending_installation = configs_to_install
            
            # Close the UI - execution will happen in the exit callback
            self.app.exit()
            
        except Exception as e:
            error_msg = f"Installation failed: {e}"
            self.notify(error_msg, severity="error")
            self.logger.error(f"Installation error: {e}")
            # Also print to stderr for debugging
            print(f"ERROR: {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    def _run_uninstallation(self) -> None:
        """Run uninstallation process by exiting UI and running in terminal."""
        try:
            # Get configurations for selected items
            configs_to_uninstall = {}
            selected_names = []
            for item_id in self.selected_items:
                config = self.config_loader.configurations.get(item_id)
                if config:
                    configs_to_uninstall[item_id] = config
                    selected_names.append(config.name)
            
            if not configs_to_uninstall:
                self.notify("No valid configurations found for selected items", severity="error")
                return
            
            # Store configs for execution after UI closes
            self._pending_uninstallation = configs_to_uninstall
            
            # Close the UI - execution will happen in the exit callback
            self.app.exit()
            
        except Exception as e:
            error_msg = f"Uninstallation failed: {e}"
            self.notify(error_msg, severity="error")
            self.logger.error(f"Uninstallation error: {e}")
            # Also print to stderr for debugging
            print(f"ERROR: {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    

    
    def _update_item_status(self, item_id: str, status: ItemStatus) -> None:
        """Update the status of an item across all categories."""
        for category_items in self.ui_items.values():
            for ui_item in category_items:
                if ui_item.config.id == item_id:
                    ui_item.status = status
    
    def _deselect_item(self, item_id: str) -> None:
        """Deselect an item across all categories."""
        for category_items in self.ui_items.values():
            for ui_item in category_items:
                if ui_item.config.id == item_id:
                    ui_item.selected = False
        self.selected_items.discard(item_id)
    
    def _update_item_in_original_category(self, item_id: str, selected: bool = None) -> None:
        """Update an item in its original category when modifying it from 'All' view."""
        for category, items in self.ui_items.items():
            if category == "All":
                continue
            for ui_item in items:
                if ui_item.config.id == item_id:
                    if selected is not None:
                        ui_item.selected = selected
                    return

    def _execute_terminal_installation(self, configs: Dict[str, ConfigItem]) -> None:
        """Execute installation process directly in terminal."""
        print("\n" + "="*60)
        print("🚀 MacSnap Installation Process")
        print("="*60)
        print(f"Installing {len(configs)} selected items...\n")
        
        successful_items = []
        failed_items = []
        
        for idx, (item_id, config) in enumerate(configs.items(), 1):
            print(f"[{idx}/{len(configs)}] Installing: {config.name}")
            print("-" * 40)
            
            if not config.install_script:
                print(f"⚠️  Skipping {config.name}: No install script defined")
                continue
            
            try:
                # Execute the installation script
                success = self._run_script_in_terminal(config.install_script, config.name)
                
                if success:
                    print(f"✅ {config.name} installed successfully!")
                    successful_items.append(config.name)
                else:
                    print(f"❌ {config.name} installation failed!")
                    failed_items.append(config.name)
                    
            except Exception as e:
                print(f"❌ Error installing {config.name}: {e}")
                failed_items.append(config.name)
            
            print()  # Add spacing between items
        
        # Print summary
        print("="*60)
        print("📊 Installation Summary")
        print("="*60)
        
        if successful_items:
            print(f"✅ Successfully installed ({len(successful_items)}):")
            for item in successful_items:
                print(f"   • {item}")
        
        if failed_items:
            print(f"\n❌ Failed to install ({len(failed_items)}):")
            for item in failed_items:
                print(f"   • {item}")
        
        print(f"\nProcess completed: {len(successful_items)} successful, {len(failed_items)} failed")
    
    def _execute_terminal_uninstallation(self, configs: Dict[str, ConfigItem]) -> None:
        """Execute uninstallation process directly in terminal."""
        print("\n" + "="*60)
        print("🗑️  MacSnap Uninstallation Process")
        print("="*60)
        print(f"Uninstalling {len(configs)} selected items...\n")
        
        successful_items = []
        failed_items = []
        
        for idx, (item_id, config) in enumerate(configs.items(), 1):
            print(f"[{idx}/{len(configs)}] Uninstalling: {config.name}")
            print("-" * 40)
            
            if not config.uninstall_script:
                print(f"⚠️  Skipping {config.name}: No uninstall script defined")
                continue
            
            try:
                # Execute the uninstallation script
                success = self._run_script_in_terminal(config.uninstall_script, config.name)
                
                if success:
                    print(f"✅ {config.name} uninstalled successfully!")
                    successful_items.append(config.name)
                else:
                    print(f"❌ {config.name} uninstallation failed!")
                    failed_items.append(config.name)
                    
            except Exception as e:
                print(f"❌ Error uninstalling {config.name}: {e}")
                failed_items.append(config.name)
            
            print()  # Add spacing between items
        
        # Print summary
        print("="*60)
        print("📊 Uninstallation Summary")
        print("="*60)
        
        if successful_items:
            print(f"✅ Successfully uninstalled ({len(successful_items)}):")
            for item in successful_items:
                print(f"   • {item}")
        
        if failed_items:
            print(f"\n❌ Failed to uninstall ({len(failed_items)}):")
            for item in failed_items:
                print(f"   • {item}")
        
        print(f"\nProcess completed: {len(successful_items)} successful, {len(failed_items)} failed")

    def _run_script_in_terminal(self, script_content: str, item_name: str) -> bool:
        """Execute a script content in terminal and show real-time output."""
        import subprocess
        import os
        import tempfile
        
        if not script_content or not script_content.strip():
            print(f"⚠️  No script content provided for {item_name}")
            return False
        
        # Create temporary script file
        temp_script = None
        try:
            # Create temporary file with .sh extension
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                # Add shebang and script content
                f.write('#!/bin/bash\n')
                f.write('set -e\n')  # Exit on any error
                f.write('\n')
                f.write(script_content)
                temp_script = f.name
            
            # Make script executable
            os.chmod(temp_script, 0o755)
            
            # Execute the script with bash
            process = subprocess.Popen(
                ['/bin/bash', temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())
            
            # Wait for completion
            process.wait()
            
            return process.returncode == 0
            
        except Exception as e:
            print(f"❌ Error executing script for {item_name}: {e}")
            return False
        finally:
            # Clean up temporary file
            if temp_script and os.path.exists(temp_script):
                try:
                    os.unlink(temp_script)
                except Exception as e:
                    print(f"Warning: Could not clean up temporary script: {e}")


def run_macsnap_ui(verbose: bool = False) -> bool:
    """
    Run the MacSnap UI with loaded configurations.
    
    Args:
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from utils.config_loader import load_configs
        import time
        import sys
        
        # Load configurations
        loader = load_configs('configs')
        
        if not loader.configurations:
            print("No configurations found. Please check the configs/ directory.")
            return False
        
        # Create and run the Textual app
        app = MacSnapApp(loader, verbose=verbose)
        app.run()
        
        # After UI closes, check for pending operations
        # Small delay to ensure terminal is ready
        time.sleep(0.1)
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Execute pending operations
        if hasattr(app, '_pending_installation') and app._pending_installation:
            print("\n" + "="*60)
            print("🚀 Executing pending installation...")
            print("="*60)
            app._execute_terminal_installation(app._pending_installation)
            
        elif hasattr(app, '_pending_uninstallation') and app._pending_uninstallation:
            print("\n" + "="*60)
            print("🗑️  Executing pending uninstallation...")
            print("="*60)
            app._execute_terminal_uninstallation(app._pending_uninstallation)
        
        return True
        
    except Exception as e:
        print(f"Failed to start MacSnap UI: {e}")
        import traceback
        traceback.print_exc()
        return False 