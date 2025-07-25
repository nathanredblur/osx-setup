#!/usr/bin/env python3

"""
Constants and Configuration for MacSnap Setup Application

This module contains all the centralized constants and configuration values
used throughout the MacSnap Setup application. This allows for easy maintenance
and configuration management across the entire application.

Usage:
    from constants import APP_NAME, APP_VERSION, CONFIGS_DIR
"""

from pathlib import Path
from typing import Tuple

# =============================================================================
# Application Metadata
# =============================================================================

APP_NAME = "MacSnap Setup"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Interactive terminal application for macOS system setup and software installation"

# =============================================================================
# System Requirements
# =============================================================================

# Minimum macOS version required (major, minor)
REQUIRED_MACOS_VERSION: Tuple[int, int] = (10, 15)  # macOS 10.15 Catalina

# Minimum Python version required (major, minor)
REQUIRED_PYTHON_VERSION: Tuple[int, int] = (3, 8)

# =============================================================================
# Directory and File Paths
# =============================================================================

# Configuration directory (relative to the project root)
# Since the app is now in tui/, configs are in ../configs
CONFIGS_DIR = "../configs"

# Special configuration file name
SPECIAL_CONFIGS_FILE = "_configs.yml"

# =============================================================================
# Installation Configuration
# =============================================================================

# Default timeout for installation scripts (in seconds)
DEFAULT_SCRIPT_TIMEOUT = 300  # 5 minutes

# =============================================================================
# Helper Functions
# =============================================================================

def get_configs_path() -> Path:
    """
    Get the absolute path to the configs directory.
    
    Returns:
        Path object pointing to the configs directory
    """
    return Path(__file__).parent / CONFIGS_DIR

def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    
    Returns:
        Path object pointing to the project root
    """
    return Path(__file__).parent.parent 