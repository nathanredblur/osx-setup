"""
Search Bar Component for MacSnap UI
"""

from textual.widgets import Input
from textual.message import Message
from textual.reactive import reactive


class SearchChanged(Message):
    """Message sent when search query changes."""
    
    def __init__(self, query: str):
        self.query = query
        super().__init__()


class SearchBar(Input):
    """Input field for searching items by name or tags."""
    
    # Component-specific CSS - structure only, theme handles colors
    DEFAULT_CSS = """
    SearchBar {
        margin: 0 0 1 0;
        height: 3;
        border: round;
    }
    """
    
    query: reactive[str] = reactive("")
    
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="Search by name or tags...",
            **kwargs
        )
        
    def watch_query(self, query: str) -> None:
        """React to query changes."""
        self.post_message(SearchChanged(query))
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        self.query = event.value
        
    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            if self.value:
                # Clear search if there's a query
                self.clear_search()
            else:
                # Focus categories if search is empty - send a custom message
                from .category_list import FocusItemTable
                self.post_message(FocusItemTable())
        
    def clear_search(self) -> None:
        """Clear the search query."""
        self.value = ""
        self.query = "" 