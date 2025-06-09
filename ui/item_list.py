"""
Item List Component for MacSnap UI
"""

from typing import List, Optional
from textual.widgets import ListView, ListItem, Static
from textual.message import Message
from textual import events

from utils.config_loader import ConfigItem
from .models import UIItem, ItemStatus


class ItemSelected(Message):
    """Message sent when an item is selected."""
    
    def __init__(self, item: UIItem):
        self.item = item
        super().__init__()


class ItemToggled(Message):
    """Message sent when an item selection is toggled."""
    
    def __init__(self, item_id: str, selected: bool):
        self.item_id = item_id
        self.selected = selected
        super().__init__()


class FocusCategoryList(Message):
    """Message to focus the category list."""
    pass


class ItemButtonList(ListView):
    """ListView for displaying and managing software items."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """
    /* Item button list structure */
    ItemButtonList {
        scrollbar-size: 1 1;
    }
    
    /* ListView structure */
    ListView > ListItem {
        padding: 0;
        margin: 0;
        height: 3;
        border: round;
    }
    
    ListView > ListItem.--highlight Static {
        text-style: bold;
    }
    
    .item-button {
        background: transparent;
        border: none;
    }
    
    .item-button-with-category {
        padding-right: 2;
    }
    
    .empty-message {
        text-align: center;
        padding: 2;
        text-style: italic;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_items: List[UIItem] = []
        self.focus_index = 0
    
    async def add_items(self, items: List[UIItem], show_category: bool = False):
        """Add items to the list."""
        self.ui_items = items
        
        # Properly await the clear operation to complete
        try:
            await self.clear()
        except Exception:
            # If clear fails, try manual cleanup as fallback
            self._debug_forced_cleanup()
        
        if not items:
            empty_item = ListItem(
                Static("No items available", classes="empty-message"),
                id="empty-list-message"
            )
            await self.mount(empty_item)
            return
        
        # Create all items at once using mount instead of append
        list_items = []
        for i, item in enumerate(items):
            item_text = self._create_item_text(item)
            if show_category:
                item_text += f" ({item.config.category})"
            
            classes = self._get_item_classes(item)
            # Simple unique IDs - no complex timestamp needed
            unique_id = f"item-{item.config.id}-{i}"
            list_item = ListItem(
                Static(item_text, classes=classes),
                id=unique_id
            )
            list_item.item_data = item  # Store reference to UIItem
            list_items.append(list_item)
        
        # Mount all items at once
        if list_items:
            await self.mount(*list_items)
    
    def _debug_forced_cleanup(self):
        """
        Manual cleanup fallback for cases where await clear() fails.
        """
        try:
            # Manual removal of children
            children_to_remove = list(self.children)
            for child in children_to_remove:
                try:
                    child.remove()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _create_item_text(self, item: UIItem) -> str:
        """Create display text for an item."""
        type_icon = self._get_type_icon(item.config.type)
        status_emoji = self._get_status_emoji(item.status)
        selection_checkbox = "☑️" if item.selected else "☐"
        
        return f"{type_icon} {status_emoji} {selection_checkbox} {item.config.name}"
    
    def _get_item_classes(self, item: UIItem) -> str:
        """Get CSS classes for an item based on its state."""
        classes = ["item-button"]
        
        if item.selected:
            classes.append("item-button-selected")
        
        # Add status class
        classes.append(f"status-{item.status.value.replace('_', '-')}")
        
        return " ".join(classes)
    
    def _get_type_icon(self, item_type: str) -> str:
        """Get icon for item type."""
        type_icons = {
            "app": "📦",
            "cask": "📦", 
            "mas": "🏪",
            "tap": "🔗",
            "file": "📄",
            "script": "📜",
            "setting": "⚙️",
            "config": "🔧"
        }
        return type_icons.get(item_type.lower(), "📦")
    
    def _get_status_emoji(self, status) -> str:
        """Get emoji for status."""
        # Handle both enum and string status
        if hasattr(status, 'value'):
            status_value = status.value
        else:
            status_value = str(status)
            
        status_emojis = {
            "installed": "✅",
            "not_installed": "⭕",
            "selected": "☑️", 
            "installing": "⏳",
            "failed": "❌",
            "unknown": "❓"
        }
        return status_emojis.get(status_value, "❓")
    
    async def refresh_display(self):
        """Refresh the display with current items."""
        await self.add_items(self.ui_items)
    
    async def _update_list_item(self, updated_item: UIItem):
        """Update a specific list item."""
        # Find and update the specific item
        for i, item in enumerate(self.ui_items):
            if item.config.id == updated_item.config.id:
                self.ui_items[i] = updated_item
                # Could update just this item in the UI if needed
                break
        await self.refresh_display()
    
    async def toggle_selection(self, item_id: str):
        """Toggle selection state of an item."""
        for item in self.ui_items:
            if item.config.id == item_id:
                item.selected = not item.selected
                self.post_message(ItemToggled(item_id, item.selected))
                await self.refresh_display()
                break
    
    def get_highlighted_item(self) -> Optional[UIItem]:
        """Get the currently highlighted item."""
        if hasattr(self, 'highlighted') and self.highlighted is not None:
            index = self.highlighted
            if 0 <= index < len(self.ui_items):
                return self.ui_items[index]
        return None
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle item highlighting."""
        if event.item and hasattr(event.item, 'id'):
            # Extract the index from the ID (format: item-{config_id}-{index})
            try:
                parts = event.item.id.split('-')
                if len(parts) >= 2:
                    index = int(parts[-1])  # Last part is the index
                    if 0 <= index < len(self.ui_items):
                        item = self.ui_items[index]
                        self.post_message(ItemSelected(item))
            except (ValueError, IndexError):
                # If parsing fails, try to find by item_data directly
                if hasattr(event.item, 'item_data'):
                    self.post_message(ItemSelected(event.item.item_data))
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key == "space":
            # Toggle selection with spacebar
            highlighted_item = self.get_highlighted_item()
            if highlighted_item:
                self.toggle_selection(highlighted_item.config.id)
        elif event.key == "enter":
            # Show details or toggle
            highlighted_item = self.get_highlighted_item()
            if highlighted_item:
                self.post_message(ItemSelected(highlighted_item))
        elif event.key == "left" or event.key == "escape":
            # Navigate back to categories
            self.post_message(FocusCategoryList()) 