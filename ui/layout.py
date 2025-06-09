"""
Main Layout Component for MacSnap UI
"""

from typing import Dict, List, Set
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.binding import Binding

from utils.config_loader import ConfigLoader
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
        # Set native Tokyo Night theme
        self.theme = "tokyo-night"
        
        # Load initial data for the first category
        if self.categories:
            await self._load_category_data(self.current_category)
    
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
            
            self._update_selection_count()
            self.logger.debug(f"Item {event.item_id} {'selected' if event.selected else 'deselected'}")
        except Exception as e:
            self.logger.error(f"Failed to handle item toggle: {e}")
    
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
        # TODO: Implement refresh functionality
        self.notify("Refresh functionality not yet implemented")
    
    def action_install(self) -> None:
        """Install selected items."""
        if not self.selected_items:
            self.notify("No items selected for installation", severity="warning")
            return
        # TODO: Implement installation functionality
        self.notify("Installation functionality not yet implemented")
    
    def action_select_all(self) -> None:
        """Select all items in current category."""
        # TODO: Implement select all functionality
        self.notify("Select all functionality not yet implemented")
    
    def action_deselect_all(self) -> None:
        """Deselect all items."""
        # TODO: Implement deselect all functionality
        self.notify("Deselect all functionality not yet implemented")
    
    def action_focus_categories(self) -> None:
        """Focus the category list."""
        try:
            category_list = self.query_one(CategoryList)
            category_list.focus()
        except Exception as e:
            self.logger.debug(f"Could not focus categories: {e}")


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