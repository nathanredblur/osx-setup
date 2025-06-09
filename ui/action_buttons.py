"""
Action Buttons Component for MacSnap UI
"""

from textual.widgets import Button
from textual.containers import Container, Horizontal as HorizontalContainer


class ActionButtons(Container):
    """Container for action buttons (Refresh, Install, etc.)."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """
    /* Control panel and action buttons structure */
    #control-panel {
        height: 7;
        border: round;
        margin-top: 1;
    }
    
    #action-buttons {
        layout: horizontal;
        align: center middle;
        background: transparent;
        height: 5;
        width: 100%;
    }
    
    ActionButtons {
        border: round;
        padding: 1;
    }
    
    /* Button structure */
    Button {
        margin: 0 1;
        text-style: bold;
        min-width: 10;
        height: 3;
        border: round;
    }
    
    Button:hover {
        text-style: bold;
        opacity: 0.8;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def compose(self):
        """Compose the action buttons."""
        with HorizontalContainer(id="action-buttons"):
            yield Button("Refresh", id="refresh-btn", variant="default")
            yield Button("Install", id="install-btn", variant="primary")
            yield Button("Remove", id="uninstall-btn", variant="error")
            yield Button("Select All", id="select-all-btn", variant="default")
            yield Button("Deselect", id="deselect-all-btn", variant="default") 