"""
Action Buttons Component for MacSnap UI
"""

from textual.widgets import Button, Horizontal, Container
from textual.containers import Horizontal as HorizontalContainer


class ActionButtons(Container):
    """Container for action buttons (Refresh, Install, etc.)."""
    
    # Component-specific CSS
    DEFAULT_CSS = """
    /* Control panel and action buttons styling */
    #control-panel {
        height: 7;
        background: #16161e;
        border: round #3b4261;
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
        background: #16161e;
        border: round #3b4261;
        padding: 1;
    }
    
    /* Button styling */
    Button {
        margin: 0 1;
        text-style: bold;
        min-width: 10;
        height: 3;
    }
    
    Button.-primary {
        background: #7aa2f7;
        color: #1a1b26;
        border: round #7aa2f7;
    }
    
    Button.-error {
        background: #f7768e;
        color: #1a1b26;
        border: round #f7768e;
    }
    
    Button.-default {
        background: #3b4261;
        color: #c0caf5;
        border: round #3b4261;
    }
    
    Button:hover {
        text-style: bold;
        opacity: 0.8;
    }
    
    Button:focus {
        border: thick #7aa2f7;
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