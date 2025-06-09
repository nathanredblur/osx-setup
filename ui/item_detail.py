"""
Item Detail Panel Component for MacSnap UI
"""

from typing import Optional
from textual.widgets import Static
from textual.reactive import reactive
import textwrap

from utils.config_loader import ConfigItem


class UIItem:
    """UI representation of a configuration item."""
    def __init__(self, config: ConfigItem, status: str, selected: bool = False):
        self.config = config
        self.status = status
        self.selected = selected


class ItemDetailPanel(Static):
    """Panel showing detailed information about selected item."""
    
    # Component-specific CSS
    DEFAULT_CSS = """
    /* Item detail panel styling */
    #item-detail {
        height: 1fr;
        border: round #3b4261;
        padding: 1;
        background: #16161e;
        color: #c0caf5;
    }
    
    ItemDetailPanel {
        padding: 1;
        background: #16161e;
        color: #c0caf5;
        border: round #3b4261;
    }
    
    /* Rich text styling for item details */
    ItemDetailPanel .item-name {
        text-style: bold;
        color: #c0caf5;
    }
    
    ItemDetailPanel .item-status {
        color: #7aa2f7;
    }
    
    ItemDetailPanel .item-description {
        color: #9aa5ce;
        margin-top: 1;
    }
    """
    
    item: reactive[Optional[UIItem]] = reactive(None)
    
    def watch_item(self, item: Optional[UIItem]) -> None:
        """Update display when item changes."""
        if item is None:
            self.update("Select an item to view details")
            return
        
        # Get type icon and format type display
        type_icon = self._get_type_icon(item.config.type)
        status_display = self._get_status_display(item.status)
        
        # Create compact display
        header = f"{type_icon} [bold]{item.config.name}[/bold]"
        status_line = f"{status_display} • {item.config.type}"
        
        # Format description with word wrapping
        description = item.config.description or "No description available"
        wrapped_description = textwrap.fill(
            description, 
            width=70, 
            initial_indent="", 
            subsequent_indent=""
        )
        
        # Combine all parts
        content_parts = [
            header,
            status_line,
            "",  # Empty line for spacing
            wrapped_description
        ]
        
        content = "\n".join(content_parts)
        self.update(content)
    
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
            "config": "🔧",
            "brew_cask": "📦"
        }
        return type_icons.get(item_type.lower(), "📦")
    
    def _get_status_display(self, status: str) -> str:
        """Get formatted status display."""
        status_displays = {
            "installed": "[green]✅ Installed[/green]",
            "not_installed": "[red]⭕ Not Installed[/red]",
            "selected": "[blue]☑️ Selected[/blue]",
            "installing": "[yellow]⏳ Installing[/yellow]",
            "failed": "[red]❌ Failed[/red]",
            "unknown": "[dim]❓ Unknown[/dim]"
        }
        return status_displays.get(status, "[dim]❓ Unknown[/dim]") 