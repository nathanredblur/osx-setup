"""
MacSnap UI Components Module

This module contains all the UI components for the MacSnap application,
organized into separate, reusable components.
"""

# Import all UI components
from .styles import TOKYO_NIGHT_CSS
from .category_list import CategoryList, CategorySelected, FocusItemTable
from .item_list import ItemButtonList, ItemSelected, ItemToggled, FocusCategoryList
from .item_detail import ItemDetailPanel
from .action_buttons import ActionButtons

# Import shared data classes
from .category_list import UIItem

# Re-export everything for easy importing
__all__ = [
    # Styles
    "TOKYO_NIGHT_CSS",
    
    # Components
    "CategoryList",
    "ItemButtonList", 
    "ItemDetailPanel",
    "ActionButtons",
    
    # Messages
    "CategorySelected",
    "FocusItemTable",
    "ItemSelected",
    "ItemToggled", 
    "FocusCategoryList",
    
    # Data classes
    "UIItem"
] 