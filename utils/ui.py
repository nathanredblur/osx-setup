"""
Modern User Interface for MacSnap Setup using Textual.

This module provides:
- Rich, modern terminal interface using Textual
- Two-column layout with interactive widgets
- Real-time status updates and progress tracking
- Beautiful styling and animations
- Mouse and keyboard support
- Responsive design
"""

import asyncio
import platform
import os
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.widgets import (
    Header, Footer, Button, Static, DataTable, ProgressBar, 
    Label, Checkbox, Tree, Tabs, Tab, Collapsible, Pretty,
    Select, Input, TextArea, RadioSet, RadioButton, Switch,
    ListView, ListItem
)
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.coordinate import Coordinate
from textual import events
from textual.color import Color
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown

from .config_loader import ConfigItem, ConfigLoader
from .installer import InstallationEngine, ExecutionResult, OperationResult
from .logger import MacSnapLogger, get_logger

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
    
    @property
    def status_emoji(self) -> str:
        """Get emoji for current status."""
        return {
            ItemStatus.INSTALLED: "✅",
            ItemStatus.NOT_INSTALLED: "⭕", 
            ItemStatus.SELECTED: "☑️",
            ItemStatus.INSTALLING: "⏳",
            ItemStatus.FAILED: "❌",
            ItemStatus.UNKNOWN: "❓"
        }.get(self.status, "❓")
    
    @property
    def status_color(self) -> str:
        """Get color for current status."""
        return {
            ItemStatus.INSTALLED: "green",
            ItemStatus.NOT_INSTALLED: "grey50",
            ItemStatus.SELECTED: "blue", 
            ItemStatus.INSTALLING: "yellow",
            ItemStatus.FAILED: "red",
            ItemStatus.UNKNOWN: "grey70"
        }.get(self.status, "grey70")

class CategoryList(Vertical):
    """Widget for displaying category list in sidebar."""
    
    # Make widget focusable
    can_focus = True
    
    def __init__(self, categories: List[str], ui_items: Dict[str, List[UIItem]]):
        super().__init__()
        self.categories = categories
        self.ui_items = ui_items
        self.selected_category = categories[0] if categories else ""
        self.focus_index = 0  # Track which category has focus
    
    def compose(self) -> ComposeResult:
        """Create the category list."""
        yield Static("📁 Categories", id="category-title")
        
        for i, category in enumerate(self.categories):
            item_count = len(self.ui_items.get(category, []))
            is_selected = category == self.selected_category
            
            # Create category item
            category_text = f"{'▶ ' if is_selected else '  '}{category} ({item_count})"
            
            category_classes = "category-item"
            if is_selected:
                category_classes += " category-item-selected"
            
            category_widget = Static(
                category_text,
                classes=category_classes,
                id=f"cat-{category.lower().replace(' ', '-')}"
            )
            yield category_widget
    
    def set_selected_category(self, category: str):
        """Update selected category without recomposing."""
        if category in self.categories:
            old_category = self.selected_category
            self.selected_category = category
            self.focus_index = self.categories.index(category)
            
            # Update the display of old and new selected items
            self._update_category_display(old_category, False)
            self._update_category_display(category, True)
    
    def _update_category_display(self, category: str, selected: bool):
        """Update display of a specific category."""
        category_id = f"cat-{category.lower().replace(' ', '-')}"
        try:
            category_widget = self.query_one(f"#{category_id}", Static)
            item_count = len(self.ui_items.get(category, []))
            
            # Update text and classes
            category_text = f"{'▶ ' if selected else '  '}{category} ({item_count})"
            category_widget.update(category_text)
            
            if selected:
                category_widget.add_class("category-item-selected")
            else:
                category_widget.remove_class("category-item-selected")
        except:
            pass  # Widget not found, ignore
    
    def on_click(self, event) -> None:
        """Handle category clicks."""
        # Prevent event bubbling
        event.stop()
        
        # Find which category was clicked
        for i, category in enumerate(self.categories):
            category_id = f"cat-{category.lower().replace(' ', '-')}"
            if hasattr(event.widget, 'id') and event.widget.id == category_id:
                self.focus_index = i
                self.post_message(CategorySelected(category))
                break
    
    def on_key(self, event) -> None:
        """Handle keyboard navigation when focused."""
        if event.key == "up":
            self.focus_index = (self.focus_index - 1) % len(self.categories)
            new_category = self.categories[self.focus_index]
            self.post_message(CategorySelected(new_category))
            event.prevent_default()
        elif event.key == "down":
            self.focus_index = (self.focus_index + 1) % len(self.categories)
            new_category = self.categories[self.focus_index]
            self.post_message(CategorySelected(new_category))
            event.prevent_default()
        elif event.key == "enter" or event.key == "space":
            # Select current category and move focus to items table
            current_category = self.categories[self.focus_index]
            self.post_message(CategorySelected(current_category))
            
            # Send message to move focus to items table
            self.post_message(FocusItemTable())
            event.prevent_default()

class CategorySelected(Message):
    """Message sent when a category is selected."""
    
    def __init__(self, category: str):
        super().__init__()
        self.category = category

class FocusItemTable(Message):
    """Message sent to focus the items table."""
    pass

class FocusCategoryList(Message):
    """Message sent to focus the category list."""
    pass

class ItemButtonList(ListView):
    """Simple list widget displaying items as navigable buttons with icons."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_items: List[UIItem] = []
        self.show_category = False
    
    def add_items(self, items: List[UIItem], show_category: bool = False):
        """Add items to the ListView."""
        self.ui_items = items
        self.show_category = show_category
        
        # Clear existing items
        self.clear()
        
        if not items:
            # Add empty message as a ListItem
            empty_item = ListItem(Static("No items in this category", classes="empty-message"))
            self.append(empty_item)
            return
        
        # Add items as ListItems
        list_items = []
        for item in items:
            button_text = self._create_item_text(item)
            button_widget = Static(button_text, classes=self._get_item_classes(item))
            list_item = ListItem(button_widget)
            list_item.item_data = item  # Store reference to UIItem
            list_items.append(list_item)
        
        # Add all items at once
        self.extend(list_items)
    
    def _create_item_text(self, item: UIItem) -> str:
        """Create text for an item with icons."""
        # Get type icon
        type_icon = self._get_type_icon(item.config.type)
        
        # Get status icon 
        status_icon = item.status_emoji
        
        # Get selection icon
        selection_icon = "☑︎" if item.selected else "☐"
        
        # Build button text with optional category
        if self.show_category:
            # Show category in parentheses for "All" view
            # Truncate category name if too long to keep button readable
            category_name = item.config.category
            if len(category_name) > 12:
                category_name = category_name[:9] + "..."
            return f"{type_icon} {status_icon} {selection_icon} {item.config.name} ({category_name})"
        else:
            return f"{type_icon} {status_icon} {selection_icon} {item.config.name}"
    
    def _get_item_classes(self, item: UIItem) -> str:
        """Get CSS classes for an item."""
        classes = "item-button"
        if item.selected:
            classes += " item-button-selected"
        if self.show_category:
            classes += " item-button-with-category"
        return classes
    
    def _get_type_icon(self, item_type: str) -> str:
        """Get icon for item type."""
        type_icons = {
            "brew": "🍺",
            "brew_cask": "📦",
            "mas": "🏪", 
            "direct_download_dmg": "💿",
            "direct_download_pkg": "📦",
            "proto_tool": "🔧",
            "system_config": "⚙️",
            "launch_agent": "🚀",
            "shell_script": "📜"
        }
        return type_icons.get(item_type, "📄")
    
    def refresh_display(self):
        """Refresh the display of all items."""
        # Clear and rebuild the list with updated data
        self.add_items(self.ui_items, self.show_category)
    
    def _update_list_item(self, updated_item: UIItem):
        """Update a specific ListItem without rebuilding the entire list."""
        try:
            # Find the ListItem that corresponds to this UIItem
            for list_item in self.children:
                if (hasattr(list_item, 'item_data') and 
                    list_item.item_data.config.id == updated_item.config.id):
                    
                    # Update the Static widget inside the ListItem
                    static_widget = list_item.children[0]  # First child should be our Static
                    if isinstance(static_widget, Static):
                        # Update text and classes
                        new_text = self._create_item_text(updated_item)
                        new_classes = self._get_item_classes(updated_item)
                        
                        static_widget.update(new_text)
                        static_widget.set_classes(new_classes)
                    
                    # Update the stored item data
                    list_item.item_data = updated_item
                    break
        except Exception:
            # If update fails, fall back to full refresh
            self.refresh_display()
    
    def toggle_selection(self, item_id: str):
        """Toggle selection of an item."""
        # Find and update the item
        updated_item = None
        for item in self.ui_items:
            if item.config.id == item_id:
                item.selected = not item.selected
                updated_item = item
                # Send message to parent to handle cross-category updates
                self.post_message(ItemToggled(item_id, item.selected))
                break
        
        # Update only the specific ListItem without losing focus
        if updated_item:
            self._update_list_item(updated_item)
    
    def get_highlighted_item(self) -> Optional[UIItem]:
        """Get currently highlighted item."""
        if self.highlighted_child and hasattr(self.highlighted_child, 'item_data'):
            return self.highlighted_child.item_data
        return None
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle item highlighting."""
        if hasattr(event.item, 'item_data'):
            item = event.item.item_data
            self.post_message(ItemSelected(item))
    
    def on_key(self, event) -> None:
        """Handle custom key bindings."""
        if event.key == "space":
            # Toggle selection of highlighted item
            highlighted_item = self.get_highlighted_item()
            if highlighted_item:
                self.toggle_selection(highlighted_item.config.id)
            event.prevent_default()
            
        elif event.key == "escape" or event.key == "backspace":
            # Return focus to category list
            self.post_message(FocusCategoryList())
            event.prevent_default()
        # For other keys (up, down, enter), let ListView handle them automatically

class ItemSelected(Message):
    """Message sent when an item is selected/focused."""
    
    def __init__(self, item: UIItem):
        super().__init__()
        self.item = item

class ItemToggled(Message):
    """Message sent when an item's selection is toggled."""
    
    def __init__(self, item_id: str, selected: bool):
        super().__init__()
        self.item_id = item_id
        self.selected = selected

class ItemTable(DataTable):
    """Custom data table for items with enhanced functionality."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_items: List[UIItem] = []
        self.selected_items: Set[str] = set()
        self.last_cursor_position = 0  # Remember cursor position
    
    def add_items(self, items: List[UIItem]):
        """Add items to the table."""
        # Save current cursor position
        old_cursor_row = getattr(self, 'cursor_row', 0) or 0
        
        self.ui_items = items
        self.clear()
        
        # Add columns
        self.add_column("Status", width=8)
        self.add_column("Name", width=30) 
        self.add_column("Type", width=12)
        self.add_column("Selected", width=10)
        
        # Add rows
        for item in items:
            selected_text = "☑️ Yes" if item.selected else "☐ No"
            self.add_row(
                item.status_emoji,
                item.config.name,
                item.config.type,
                selected_text,
                key=item.config.id
            )
        
        # Restore cursor position if possible
        if len(items) > 0:
            self.last_cursor_position = min(old_cursor_row, len(items) - 1)
            # Use call_later to ensure the table is fully rendered before setting cursor
            self.call_later(self._restore_cursor_position)
    
    def _restore_cursor_position(self):
        """Restore cursor to saved position."""
        try:
            if self.last_cursor_position < self.row_count:
                self.cursor_row = self.last_cursor_position
        except Exception:
            pass  # Ignore if table not ready
    
    def toggle_selection(self, item_id: str):
        """Toggle selection of an item."""
        # Save current cursor position
        current_cursor = getattr(self, 'cursor_row', 0) or 0
        
        for item in self.ui_items:
            if item.config.id == item_id:
                item.selected = not item.selected
                break
        
        # Refresh the table while preserving cursor position
        self.last_cursor_position = current_cursor
        self.add_items(self.ui_items)
    
    def on_key(self, event) -> None:
        """Handle keyboard navigation in items table."""
        if event.key == "escape" or event.key == "backspace":
            # Return focus to category list
            self.post_message(FocusCategoryList())
            event.prevent_default()

class ItemDetailPanel(Static):
    """Panel showing detailed information about selected item."""
    
    item: reactive[Optional[UIItem]] = reactive(None)
    
    def watch_item(self, item: Optional[UIItem]) -> None:
        """Update display when item changes."""
        if item is None:
            self.update("📋 Select an item to view details")
            return
        
        # Create rich content with Tokyo Night colors
        content_lines = []
        
        # Title with emoji
        title_line = f"📦 {item.config.name}"
        content_lines.append(title_line)
        content_lines.append("─" * len(title_line))
        content_lines.append("")
        
        # Status with color
        status_display = item.status.value.replace("_", " ").title()
        status_line = f"Status: {item.status_emoji} {status_display}"
        content_lines.append(status_line)
        
        # Basic info
        content_lines.append(f"Type: {item.config.type}")
        content_lines.append(f"Category: {item.config.category}")
        
        if item.selected:
            content_lines.append("Selection: ☑️ Selected for installation")
        else:
            content_lines.append("Selection: ☐ Not selected")
        
        content_lines.append("")
        
        # Description
        if item.config.description:
            content_lines.append("📝 Description:")
            # Word wrap description
            desc_words = item.config.description.split()
            current_line = ""
            for word in desc_words:
                if len(current_line + " " + word) <= 60:  # Wrap at 60 chars
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        content_lines.append(f"   {current_line}")
                    current_line = word
            if current_line:
                content_lines.append(f"   {current_line}")
            content_lines.append("")
        
        # Dependencies
        if item.config.dependencies:
            content_lines.append("🔗 Dependencies:")
            for dep in item.config.dependencies:
                content_lines.append(f"   • {dep}")
            content_lines.append("")
        
        # Scripts info
        scripts = []
        if item.config.install_script:
            scripts.append("install")
        if item.config.validate_script:
            scripts.append("validate")
        if item.config.configure_script:
            scripts.append("configure")
        if item.config.uninstall_script:
            scripts.append("uninstall")
        
        if scripts:
            content_lines.append("⚙️ Available scripts:")
            content_lines.append(f"   {', '.join(scripts)}")
        
        # Join content and update
        content_text = "\n".join(content_lines)
        self.update(content_text)

class ProgressScreen(ModalScreen):
    """Modal screen for showing installation progress."""
    
    def __init__(self, selected_items: List[str]):
        super().__init__()
        self.selected_items = selected_items
        self.progress_log: List[str] = []
    
    def compose(self) -> ComposeResult:
        with Container(id="progress-container"):
            yield Label("Installing Selected Items", id="progress-title")
            yield ProgressBar(id="progress-bar")
            yield Label("Preparing...", id="progress-status")
            yield ScrollableContainer(
                Static("", id="progress-log"),
                id="progress-log-container"
            )
            with Horizontal(id="progress-buttons"):
                yield Button("Cancel", variant="error", id="cancel-btn")
    
    def add_log_entry(self, message: str):
        """Add a log entry to the progress display."""
        self.progress_log.append(message)
        log_widget = self.query_one("#progress-log", Static)
        log_widget.update("\n".join(self.progress_log))
        
        # Scroll to bottom
        container = self.query_one("#progress-log-container", ScrollableContainer)
        container.scroll_end()
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        status_label = self.query_one("#progress-status", Label)
        
        progress_bar.update(progress=current / total * 100)
        status_label.update(f"{message} ({current}/{total})")

class ResultsScreen(ModalScreen):
    """Modal screen for showing installation results."""
    
    def __init__(self, results: List[ExecutionResult]):
        super().__init__()
        self.results = results
    
    def compose(self) -> ComposeResult:
        with Container(id="results-container"):
            yield Label("Installation Complete", id="results-title")
            yield self._create_results_table()
            with Horizontal(id="results-buttons"):
                yield Button("Close", variant="primary", id="close-btn")
    
    def _create_results_table(self) -> DataTable:
        """Create results table."""
        table = DataTable(id="results-table")
        table.add_column("Item", width=25)
        table.add_column("Operation", width=15)
        table.add_column("Result", width=15)
        table.add_column("Duration", width=10)
        
        for result in self.results:
            result_emoji = {
                OperationResult.SUCCESS: "✅",
                OperationResult.ALREADY_INSTALLED: "✅",
                OperationResult.FAILED: "❌",
                OperationResult.SKIPPED: "⏭️"
            }.get(result.result, "❓")
            
            table.add_row(
                result.item_id,
                result.operation,
                f"{result_emoji} {result.result.value}",
                f"{result.duration:.1f}s"
            )
        
        return table

class MacSnapApp(App):
    """
    Main MacSnap Setup application using Textual.
    
    A modern, rich terminal interface for macOS software installation.
    """
    
    # Set Tokyo Night theme as default
    DARK = True
    
    CSS = """
    /* Tokyo Night theme colors */
    Screen {
        background: #1a1b26;
        color: #c0caf5;
    }
    
    #main-container {
        background: #1a1b26;
    }
    
    /* Left sidebar for categories */
    #category-sidebar {
        dock: left;
        width: 25%;
        background: #16161e;
        border-right: solid #3b4261;
        padding: 1;
    }
    
    CategoryList:focus {
        border: solid #7aa2f7;
    }
    
    #category-title {
        text-style: bold;
        color: #7aa2f7;
        margin-bottom: 1;
    }
    
    #category-list {
        height: 100%;
    }
    
    /* Main content area */
    #content-area {
        background: #1a1b26;
        padding: 1;
    }
    
    #item-table {
        height: 2fr;
        border: solid #3b4261;
        margin-bottom: 1;
        background: #1a1b26;
        scrollbar-background: #16161e;
        scrollbar-color: #7aa2f7;
    }
    
    #item-detail {
        height: 1fr;
        border: solid #3b4261;
        padding: 1;
        background: #16161e;
        color: #c0caf5;
    }
    
    /* Control panel */
    #control-panel {
        dock: bottom;
        height: 5;
        background: #16161e;
        border-top: solid #3b4261;
        padding: 1;
    }
    
    #action-buttons {
        align: center middle;
    }
    
    Button {
        margin: 0 1;
        min-width: 16;
    }
    
    Button.-primary {
        background: #7aa2f7;
        color: #1a1b26;
    }
    
    Button.-error {
        background: #f7768e;
        color: #1a1b26;
    }
    
    Button.-default {
        background: #3b4261;
        color: #c0caf5;
    }
    
    /* Category list styling */
    .category-item {
        padding: 0 1;
        margin-bottom: 1;
        color: #c0caf5;
        width: 100%;
    }
    
    .category-item:hover {
        background: #3b4261;
        color: #7aa2f7;
    }
    
    .category-item-selected {
        background: #7aa2f7;
        color: #1a1b26;
        text-style: bold;
    }
    
    .category-item-selected:hover {
        background: #9ece6a;
        color: #1a1b26;
    }
    
    .category-item-count {
        color: #565f89;
    }
    
    /* Status colors with Tokyo Night palette */
    .status-installed {
        color: #9ece6a;
    }
    
    .status-failed {
        color: #f7768e;
    }
    
    .status-installing {
        color: #e0af68;
    }
    
    .status-selected {
        color: #7aa2f7;
    }
    
    /* Modal screens */
    #progress-container, #results-container {
        width: 80%;
        height: 80%;
        margin: 2;
        background: #16161e;
        border: solid #7aa2f7;
    }
    
    #progress-title, #results-title {
        text-style: bold;
        text-align: center;
        margin: 1;
        color: #7aa2f7;
    }
    
    #progress-log-container {
        height: 60%;
        border: solid #3b4261;
        margin: 1;
        background: #1a1b26;
    }
    
    #progress-log {
        padding: 1;
        color: #c0caf5;
    }
    
    /* Item button list styling */
    ItemButtonList {
        scrollbar-background: #16161e;
        scrollbar-color: #7aa2f7;
        scrollbar-size: 1 1;
    }
    
    /* ListView highlighting - uses different CSS structure */
    ListView > ListItem {
        padding: 0;
        margin: 0;
        background: #1a1b26;
        height: 3;
        border: round #3b4261;
    }
    
    ListView > ListItem.--highlight {
        background: #7aa2f7 !important;
        border: round #7aa2f7 !important;
    }
    
    ListView > ListItem.--highlight Static {
        color: #1a1b26 !important;
        text-style: bold;
    }
    
    ListView > ListItem:hover {
        background: #3b4261;
        border: round #7aa2f7;
    }
    
    ListView > ListItem:hover Static {
        color: #7aa2f7;
    }
    
    .item-button {
        color: #c0caf5;
        background: transparent;
        border: none;
    }
    
    .item-button-selected {
        color: #9ece6a;
    }
    
    .item-button-with-category {
        padding-right: 2;
    }
    
    .empty-message {
        color: #565f89;
        text-align: center;
        padding: 2;
        text-style: italic;
    }
    
    /* Data table styling (kept for backward compatibility) */
    DataTable {
        background: #1a1b26;
        color: #c0caf5;
    }
    
    DataTable > .datatable--header {
        background: #16161e;
        color: #7aa2f7;
        text-style: bold;
    }
    
    DataTable > .datatable--cursor {
        background: #7aa2f7;
        color: #1a1b26;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("i", "install", "Install Selected"),
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
        
        # Initialize UI items
        self._initialize_ui_items()
    
    def _initialize_ui_items(self):
        """Initialize UI items grouped by category."""
        # First initialize regular categories
        for category in self.categories:
            if category == "All":
                continue  # Skip "All" for now, handle it separately
                
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
            
            # Sort items alphabetically
            self.ui_items[category].sort(key=lambda x: x.config.name)
        
        # Now create the "All" category with all items
        self._create_all_category()
    
    def _create_all_category(self):
        """Create the 'All' category with all items sorted by category then name."""
        all_items = []
        
        # Collect all items from all categories
        for category in self.categories:
            if category == "All":
                continue
            
            for ui_item in self.ui_items[category]:
                all_items.append(ui_item)
        
        # Sort first by category, then by name
        all_items.sort(key=lambda x: (x.config.category, x.config.name))
        
        self.ui_items["All"] = all_items
    
    def _update_item_in_original_category(self, item_id: str, selected: bool):
        """Update an item's selection status in its original category."""
        for category in self.categories:
            if category == "All":
                continue
            
            for ui_item in self.ui_items[category]:
                if ui_item.config.id == item_id:
                    ui_item.selected = selected
                    return
    
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
            with Horizontal(id="action-buttons"):
                yield Button("Refresh Status", id="refresh-btn", variant="default")
                yield Button("Install Selected", id="install-btn", variant="primary")
                yield Button("Uninstall Selected", id="uninstall-btn", variant="error")
                yield Button("Select All", id="select-all-btn", variant="default")
                yield Button("Deselect All", id="deselect-all-btn", variant="default")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the app after mounting."""
        # Load initial data for the first category
        if self.categories:
            self._load_category_data(self.current_category)
        
        # Check initial status
        self.run_worker(self._check_initial_status())
    
    def on_category_selected(self, event: CategorySelected) -> None:
        """Handle category selection from sidebar."""
        self._switch_category(event.category)
    
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
            
            # If we're in "All" view, update the item in its original category
            if self.current_category == "All":
                self._update_item_in_original_category(event.item_id, event.selected)
            
            self._update_selection_count()
            self.logger.debug(f"Item {event.item_id} {'selected' if event.selected else 'deselected'}")
        except Exception as e:
            self.logger.error(f"Failed to handle item toggle: {e}")
    
    def _load_category_data(self, category: str):
        """Load data for a specific category."""
        items = self.ui_items.get(category, [])
        item_table = self.query_one("#item-table", ItemButtonList)
        
        # Show category names when in "All" view
        show_category = (category == "All")
        item_table.add_items(items, show_category=show_category)
        
        # Show details for first item if available
        if items:
            detail_panel = self.query_one("#item-detail", ItemDetailPanel)
            detail_panel.item = items[0]
        
        # Update selected items count
        self._update_selection_count()
    
    def _update_selection_count(self):
        """Update the selection count display."""
        # This could be displayed in the footer or header
        selected_count = len(self.selected_items)
        # For now, we'll just log it
        self.logger.debug(f"Selected items: {selected_count}")
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the data table."""
        if event.row_key:
            item_id = str(event.row_key)
            # Find the item and show details
            current_items = self.ui_items.get(self.current_category, [])
            for ui_item in current_items:
                if ui_item.config.id == item_id:
                    detail_panel = self.query_one("#item-detail", ItemDetailPanel)
                    detail_panel.item = ui_item
                    self.logger.debug(f"Selected item: {ui_item.config.name}")
                    return
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-btn":
            self.action_refresh()
        elif event.button.id == "install-btn":
            self.action_install()
        elif event.button.id == "uninstall-btn":
            self.action_uninstall()
        elif event.button.id == "select-all-btn":
            self.action_select_all()
        elif event.button.id == "deselect-all-btn":
            self.action_deselect_all()
    
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
        
        self.run_worker(self._run_installation())
    
    def action_uninstall(self) -> None:
        """Uninstall selected items."""
        if not self.selected_items:
            self.notify("No items selected for uninstallation", severity="warning")
            return
        
        self.run_worker(self._run_uninstallation())
    
    def action_select_all(self) -> None:
        """Select all items in current category."""
        items = self.ui_items.get(self.current_category, [])
        for item in items:
            item.selected = True
            self.selected_items.add(item.config.id)
            
            # If we're in "All" view, also update the item in its original category
            if self.current_category == "All":
                self._update_item_in_original_category(item.config.id, selected=True)
        
        # Regenerate "All" category if needed
        if self.current_category == "All":
            self._create_all_category()
        
        self._load_category_data(self.current_category)
        self.notify(f"Selected all items in {self.current_category}")
    
    def action_deselect_all(self) -> None:
        """Deselect all items."""
        for category_items in self.ui_items.values():
            for item in category_items:
                item.selected = False
        
        self.selected_items.clear()
        self._load_category_data(self.current_category)
        self.notify("Deselected all items")
    
    def action_toggle_selection(self) -> None:
        """Toggle selection of current item."""
        table = self.query_one("#item-table", ItemButtonList)
        if table.focus_index is not None and table.focus_index < len(table.ui_items):
            ui_item = table.ui_items[table.focus_index]
            table.toggle_selection(ui_item.config.id)
            
            # Update global selected items
            if ui_item.selected:
                self.selected_items.add(ui_item.config.id)
            else:
                self.selected_items.discard(ui_item.config.id)
            
            self._update_selection_count()
    
    def action_focus_categories(self) -> None:
        """Focus the category list (from Esc/Backspace)."""
        try:
            category_list = self.query_one(CategoryList)
            category_list.focus()
            self.logger.debug("Focus moved to category list via action")
        except Exception as e:
            self.logger.debug(f"Could not focus category list via action: {e}")
    
    def _switch_category(self, category: str):
        """Switch to a specific category."""
        self.current_category = category
        self._load_category_data(self.current_category)
        
        # Update category list selection
        category_list = self.query_one(CategoryList)
        category_list.set_selected_category(self.current_category)
        
        self.logger.debug(f"Switched to category: {self.current_category}")
    
    async def _check_initial_status(self) -> None:
        """Check initial installation status for all items."""
        self.notify("Checking installation status...")
        
        total_items = sum(len(items) for items in self.ui_items.values())
        checked = 0
        
        for category in self.categories:
            for ui_item in self.ui_items[category]:
                result = self.engine.check_install_status(ui_item.config)
                ui_item.status = (ItemStatus.INSTALLED if result.result == OperationResult.SUCCESS 
                                else ItemStatus.NOT_INSTALLED)
                checked += 1
                
                # Update UI periodically
                if checked % 3 == 0:
                    progress = (checked / total_items) * 100
                    self.notify(f"Checking status... {checked}/{total_items} ({progress:.0f}%)")
        
        # Regenerate "All" category to reflect status changes
        self._create_all_category()
        
        # Refresh current category
        self._load_category_data(self.current_category)
        self.notify("Status check completed", severity="information")
    
    async def _run_installation(self) -> None:
        """Run installation process."""
        # Show progress screen
        progress_screen = ProgressScreen(list(self.selected_items))
        self.push_screen(progress_screen)
        
        try:
            # Run batch installation
            results = self.engine.batch_process(
                self.config_loader.configurations,
                list(self.selected_items),
                "install"
            )
            
            # Update UI item statuses
            for result in results:
                for category_items in self.ui_items.values():
                    for ui_item in category_items:
                        if ui_item.config.id == result.item_id:
                            if result.result in [OperationResult.SUCCESS, OperationResult.ALREADY_INSTALLED]:
                                ui_item.status = ItemStatus.INSTALLED
                            else:
                                ui_item.status = ItemStatus.FAILED
            
            # Close progress screen and show results
            self.pop_screen()
            results_screen = ResultsScreen(results)
            self.push_screen(results_screen)
            
            # Refresh display
            self._load_category_data(self.current_category)
            
        except Exception as e:
            self.pop_screen()
            self.notify(f"Installation failed: {e}", severity="error")
    
    async def _run_uninstallation(self) -> None:
        """Run uninstallation process."""
        # Similar to installation but for uninstall
        try:
            results = self.engine.batch_process(
                self.config_loader.configurations,
                list(self.selected_items),
                "uninstall"
            )
            
            # Update statuses
            for result in results:
                for category_items in self.ui_items.values():
                    for ui_item in category_items:
                        if ui_item.config.id == result.item_id:
                            if result.result == OperationResult.SUCCESS:
                                ui_item.status = ItemStatus.NOT_INSTALLED
                            else:
                                ui_item.status = ItemStatus.FAILED
            
            # Show results
            results_screen = ResultsScreen(results)
            self.push_screen(results_screen)
            
            # Refresh display
            self._load_category_data(self.current_category)
            
        except Exception as e:
            self.notify(f"Uninstallation failed: {e}", severity="error")


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
        
        # Create and run the Textual app
        app = MacSnapApp(loader, verbose=verbose)
        app.run()
        return True
        
    except Exception as e:
        print(f"Failed to start MacSnap UI: {e}")
        return False 