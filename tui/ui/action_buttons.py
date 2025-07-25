"""
Action Buttons Component for MacSnap UI
"""

from textual.widgets import Button
from textual.containers import Container, Horizontal as HorizontalContainer
from textual.app import ComposeResult


class ActionButtons(Container):
    """Container for action buttons (Refresh, Install, etc.)."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """
    /* Action buttons layout */
    #action-buttons {
        layout: horizontal;
        align: center middle;
        background: transparent;
        height: 3;
        width: 100%;
    }

    ActionButtons {
        padding: 0;
    }

    /* Button sizing */
    .button {
        margin: 0 1;
        text-style: bold;
        min-width: 10;
        padding: 0 1;
        height: 3;
    }
    
    Button:hover {
        text-style: bold;
        opacity: 0.8;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        """Compose the action buttons."""
        with HorizontalContainer(id="action-buttons"):
            yield Button("Refresh", id="refresh-btn", variant="default", classes="button")
            yield Button("Install", id="install-btn", variant="primary", classes="button")
            yield Button("Remove", id="uninstall-btn", variant="error", classes="button")
            yield Button("Select All", id="select-all-btn", variant="default", classes="button")
            yield Button("Deselect", id="deselect-all-btn", variant="default", classes="button") 