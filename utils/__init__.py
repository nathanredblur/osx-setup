"""
MacSnap Setup - Utility modules for macOS software installation and configuration.

This package contains the core modules for:
- Configuration loading and validation
- Installation engine with multiple handlers
- User interface with two-column layout
- Logging system with verbose mode support
"""

__version__ = "1.0.0"
__author__ = "MacSnap Team"

# Make key classes available at package level
# Only import what exists for now
from .config_loader import ConfigLoader
from .validators import ConfigValidator
from .installer import InstallationEngine

__all__ = [
    "ConfigLoader",
    "ConfigValidator",
    "InstallationEngine"
]

# TODO: Add imports as modules are created:
# from .logger import Logger
# from .ui import UserInterface 