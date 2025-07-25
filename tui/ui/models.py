"""
UI Models for MacSnap UI Components

This module contains shared data models used across UI components.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from utils.config_loader import ConfigItem


class ItemStatus(Enum):
    """Status of items for display."""
    UNKNOWN = "unknown"
    INSTALLED = "installed" 
    NOT_INSTALLED = "not_installed"
    SELECTED = "selected"
    INSTALLING = "installing"
    FAILED = "failed"


@dataclass
class UIItem:
    """UI representation of a configuration item."""
    config: ConfigItem
    status: ItemStatus
    selected: bool = False
    
    @property
    def status_emoji(self) -> str:
        """Get emoji for current status."""
        return {
            ItemStatus.INSTALLED: "✅",
            ItemStatus.NOT_INSTALLED: "⭕", 
            ItemStatus.SELECTED: "☑️",
            ItemStatus.INSTALLING: "⏳",
            ItemStatus.FAILED: "❌",
            ItemStatus.UNKNOWN: "❓"
        }.get(self.status, "❓")
    
    @property
    def status_color(self) -> str:
        """Get color for current status."""
        return {
            ItemStatus.INSTALLED: "green",
            ItemStatus.NOT_INSTALLED: "grey50",
            ItemStatus.SELECTED: "blue", 
            ItemStatus.INSTALLING: "yellow",
            ItemStatus.FAILED: "red",
            ItemStatus.UNKNOWN: "grey70"
        }.get(self.status, "grey70") 