"""
Category List Component for MacSnap UI
"""

from typing import List, Dict
from textual.widgets import ListView, ListItem, Static
from textual.message import Message
from textual import events

from utils.config_loader import ConfigItem


class UIItem:
    """UI representation of a configuration item."""
    def __init__(self, config: ConfigItem, status: str, selected: bool = False):
        self.config = config
        self.status = status
        self.selected = selected


class CategorySelected(Message):
    """Message sent when a category is selected."""
    
    def __init__(self, category: str):
        self.category = category
        super().__init__()


class FocusItemTable(Message):
    """Message to focus the item table."""
    pass


class CategoryList(ListView):
    """ListView for displaying and selecting categories."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """
    /* Category list structure */
    CategoryList {
        scrollbar-size: 1 1;
    }
    
    CategoryList > ListItem {
        padding: 0;
        margin: 0 0 1 0;
        height: 3;
        border: round;
    }
    
    CategoryList > ListItem.--highlight Static {
        text-style: bold;
    }
    
    .category-item {
        background: transparent;
        border: none;
    }
    
    /* Category sidebar container */
    #category-sidebar {
        dock: left;
        width: 25%;
        padding: 1;
        border: round;
        margin-right: 1;
    }
    """
    
    def __init__(self, categories: List[str], ui_items: Dict[str, List[UIItem]]):
        super().__init__()
        self.categories = categories
        self.ui_items = ui_items
        self.current_category = categories[0] if categories else ""
    
    def compose(self):
        """Compose the category list items."""
        list_items = []
        for category in self.categories:
            item_count = len(self.ui_items.get(category, []))
            
            if category == "All":
                # For "All", count all items across categories (excluding duplicates)
                all_items = set()
                for items in self.ui_items.values():
                    for item in items:
                        if hasattr(item, 'config') and hasattr(item.config, 'id'):
                            all_items.add(item.config.id)
                item_count = len(all_items)
            
            category_text = f"{category} ({item_count})"
            list_item = ListItem(
                Static(category_text, classes="category-item"),
                id=f"category-{category.lower().replace(' ', '-')}"
            )
            list_item.category_name = category  # Store category reference
            list_items.append(list_item)
        
        for item in list_items:
            yield item
    
    def set_selected_category(self, category: str):
        """Set the currently selected category."""
        self.current_category = category
        # Update highlighting could be added here if needed
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle category selection."""
        if event.item and hasattr(event.item, 'id'):
            # Extract category name from item id
            category_id = event.item.id.replace('category-', '').replace('-', ' ')
            
            # Find matching category (case insensitive)
            for category in self.categories:
                if category.lower().replace(' ', '-') == category_id:
                    self.current_category = category
                    self.post_message(CategorySelected(category))
                    break
    
    def on_key(self, event) -> None:
        """Handle keyboard navigation."""
        if event.key == "enter":
            # Navigate to item table when Enter is pressed
            self.post_message(FocusItemTable())
        elif event.key == "right":
            # Also allow right arrow to navigate to items
            self.post_message(FocusItemTable()) 