"""
Item List Component for MacSnap UI
"""

import time
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
        self.show_category = show_category
        
        # Force clear all children first
        await self._force_clear_all_children()
        
        if not items:
            timestamp = int(time.time() * 1000)  # Milliseconds timestamp
            empty_item = ListItem(
                Static("No items available", classes="empty-message"),
                id=f"empty-list-message-{timestamp}"
            )
            await self.mount(empty_item)
            return
        
        # Create all items at once using mount instead of append
        list_items = []
        timestamp = int(time.time() * 1000)  # Milliseconds timestamp
        for i, item in enumerate(items):
            item_text = self._create_item_text(item)
            if show_category:
                item_text += f" ({item.config.category})"
            
            classes = self._get_item_classes(item)
            # Create truly unique IDs using timestamp to avoid any possibility of duplicates
            unique_id = f"item-{item.config.id}-{timestamp}-{i}"
            list_item = ListItem(
                Static(item_text, classes=classes),
                id=unique_id
            )
            list_item.item_data = item  # Store reference to UIItem
            list_items.append(list_item)
        
        # Mount all items at once
        if list_items:
            await self.mount(*list_items)
    
    async def _force_clear_all_children(self):
        """
        Force clear all children from the ListView.
        """
        try:
            # First try the standard clear method
            await self.clear()
        except Exception:
            pass
            
        # Always do a manual check and cleanup as well
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if not self.children:
                    break  # No more children to remove
                    
                children_to_remove = list(self.children)
                for child in children_to_remove:
                    try:
                        child.remove()
                    except Exception:
                        pass
                        
                # Small delay between attempts
                if attempt < max_attempts - 1:
                    await self.app.sleep(0.01)
            except Exception:
                pass
    
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
        license_icon = "💰" if getattr(item.config, 'requires_license', False) else ""
        
        # Add license icon if required
        license_part = f" {license_icon}" if license_icon else ""
        
        return f"{type_icon} {status_emoji} {selection_checkbox} {item.config.name}{license_part}"
    
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
            "brew": "🍺",
            "brew_cask": "📦",
            "mas": "🏪",
            "system_config": "⚙️ ",
            "app": "📱",
            "file": "📄",
            "script": "📜",
            "config": "🔧",
            "tap": "🔗"
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
        """Refresh the display with current items while preserving selection."""
        # Save current index to restore after refresh
        current_index = self.index
        
        await self.add_items(self.ui_items)
        
        # Restore the index if it was valid
        if current_index is not None and 0 <= current_index < len(self.ui_items):
            self.index = current_index
    
    def _update_specific_list_item(self, updated_item: UIItem):
        """Update a specific ListItem without rebuilding the entire list."""
        try:
            # Find the ListItem that corresponds to this UIItem
            for list_item in self.children:
                if (hasattr(list_item, 'item_data') and 
                    list_item.item_data.config.id == updated_item.config.id):
                    
                    # Update the Static widget inside the ListItem
                    static_widget = list_item.children[0]  # First child should be our Static
                    if isinstance(static_widget, Static):
                        # Update text and classes (with category if needed)
                        new_text = self._create_item_text(updated_item)
                        if hasattr(self, 'show_category') and getattr(self, 'show_category', False):
                            new_text += f" ({updated_item.config.category})"
                        
                        new_classes = self._get_item_classes(updated_item)
                        
                        static_widget.update(new_text)
                        static_widget.set_classes(new_classes)
                    
                    # Update the stored item data
                    list_item.item_data = updated_item
                    return  # Successfully updated, exit
            
            # If we get here, item wasn't found - force refresh
            self.call_later(self.refresh_display)
            
        except Exception:
            # If update fails, fall back to full refresh  
            self.call_later(self.refresh_display)
    
    async def _update_list_item(self, updated_item: UIItem):
        """Update a specific list item."""
        # Find and update the specific item
        for i, item in enumerate(self.ui_items):
            if item.config.id == updated_item.config.id:
                self.ui_items[i] = updated_item
                # Could update just this item in the UI if needed
                break
        await self.refresh_display()
    
    def toggle_selection(self, item_id: str):
        """Toggle selection state of an item."""
        # Save current index to restore after refresh
        current_index = self.index
        
        # Find and update the item
        for item in self.ui_items:
            if item.config.id == item_id:
                item.selected = not item.selected
                # Send message to parent to handle cross-category updates
                self.post_message(ItemToggled(item_id, item.selected))
                break
        
        # Force refresh but restore focus immediately
        self.call_later(self._refresh_and_restore_focus, current_index)
    
    async def _refresh_and_restore_focus(self, saved_index: int) -> None:
        """Refresh the display and restore the focus to the saved index."""
        await self.add_items(self.ui_items, self.show_category)
        
        # Restore focus
        if saved_index is not None and 0 <= saved_index < len(self.ui_items):
            self.index = saved_index
    
    def get_highlighted_item(self) -> Optional[UIItem]:
        """Get the currently highlighted item."""
        if self.index is not None and 0 <= self.index < len(self.ui_items):
            return self.ui_items[self.index]
        return None
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle item highlighting."""
        if event.item and hasattr(event.item, 'id'):
            # Try to use the stored item_data first
            if hasattr(event.item, 'item_data') and event.item.item_data:
                self.post_message(ItemSelected(event.item.item_data))
                return
            
            # Fallback: Extract the index from the ID (format: item-{config_id}-{timestamp}-{index})
            try:
                parts = event.item.id.split('-')
                if len(parts) >= 3:
                    index = int(parts[-1])  # Last part is the index
                    if 0 <= index < len(self.ui_items):
                        item = self.ui_items[index]
                        self.post_message(ItemSelected(item))
            except (ValueError, IndexError):
                # If all else fails, try to find by searching
                pass
    
    def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key == "space":
            # Toggle selection with spacebar
            highlighted_item = self.get_highlighted_item()
            if highlighted_item:
                self.toggle_selection(highlighted_item.config.id)
                event.prevent_default()  # Prevent default space behavior
        elif event.key == "enter":
            # Show details or toggle
            highlighted_item = self.get_highlighted_item()
            if highlighted_item:
                self.post_message(ItemSelected(highlighted_item))
        elif event.key == "left" or event.key == "escape":
            # Navigate back to categories
            self.post_message(FocusCategoryList())
    
    def action_toggle_selection(self) -> None:
        """Action to toggle selection of highlighted item."""
        highlighted_item = self.get_highlighted_item()
        if highlighted_item:
            self.toggle_selection(highlighted_item.config.id) 