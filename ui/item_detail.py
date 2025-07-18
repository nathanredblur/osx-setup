"""
Item Detail Panel Component for MacSnap UI
"""

from typing import Optional
from textual.widgets import Static
from textual.reactive import reactive
import textwrap

from utils.config_loader import ConfigItem
from .models import UIItem, ItemStatus


class ItemDetailPanel(Static):
    """Panel showing detailed information about selected item."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """    
    ItemDetailPanel {
        padding: 1;
        border: round;
    }
    
    /* Rich text styling for item details */
    ItemDetailPanel .item-name {
        text-style: bold;
    }
    
    ItemDetailPanel .item-description {
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
        
        # Create header with license indicator
        license_indicator = " 💰" if getattr(item.config, 'requires_license', False) else ""
        header = f"{type_icon} [bold]{item.config.name}[/bold]{license_indicator}"
        
        # Status and type line
        status_line = f"{status_display} • {item.config.type}"
        
        # Format description with word wrapping
        description = item.config.description or "No description available"
        wrapped_description = textwrap.fill(
            description, 
            width=70, 
            initial_indent="", 
            subsequent_indent=""
        )
        
        # Build content parts
        content_parts = [
            header,
            status_line,
            "",  # Empty line for spacing
            wrapped_description
        ]
        
        # Add tags if available
        if hasattr(item.config, 'tags') and item.config.tags:
            tags_text = " ".join([f"#{tag}" for tag in item.config.tags])
            content_parts.extend([
                "",
                f"[dim]Tags:[/dim] {tags_text}"
            ])
        
        # Add URL if available
        if hasattr(item.config, 'url') and item.config.url:
            content_parts.extend([
                "",
                f"[dim]URL:[/dim] {item.config.url}"
            ])
        
        # Add notes if available
        if hasattr(item.config, 'notes') and item.config.notes:
            content_parts.extend([
                "",
                "[dim]Notes:[/dim]"
            ])
            
            # Format notes with proper indentation
            notes_lines = item.config.notes.strip().split('\n')
            for line in notes_lines:
                if line.strip():  # Skip empty lines
                    wrapped_line = textwrap.fill(
                        line.strip(), 
                        width=68, 
                        initial_indent="  ", 
                        subsequent_indent="  "
                    )
                    content_parts.append(wrapped_line)
        
        # Add license requirement notice
        if getattr(item.config, 'requires_license', False):
            content_parts.extend([
                "",
                "[yellow]⚠️  This software requires a license purchase[/yellow]"
            ])
        
        content = "\n".join(content_parts)
        self.update(content)
    
    def _get_type_icon(self, item_type: str) -> str:
        """Get icon for item type."""
        type_icons = {
            "brew": "🍺",
            "brew_cask": "📦",
            "mas": "🏪",
            "system_config": "⚙️",
            "app": "📱",
            "file": "📄",
            "script": "📜",
            "config": "🔧",
            "tap": "🔗"
        }
        return type_icons.get(item_type.lower(), "📦")
    
    def _get_status_display(self, status) -> str:
        """Get formatted status display."""
        if hasattr(status, 'value'):
            status_value = status.value
        else:
            status_value = str(status).lower()
            
        status_displays = {
            "installed": "[green]✅ Installed[/green]",
            "not_installed": "[red]⭕ Not Installed[/red]",
            "selected": "[blue]☑️ Selected[/blue]",
            "installing": "[yellow]⏳ Installing[/yellow]",
            "failed": "[red]❌ Failed[/red]",
            "unknown": "[dim]❓ Unknown[/dim]"
        }
        return status_displays.get(status_value, "[dim]❓ Unknown[/dim]") 