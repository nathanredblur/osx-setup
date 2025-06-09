#!/usr/bin/env python3

"""
MacSnap Setup - Main Application Entry Point

This is the primary entry point for the MacSnap Setup application.
It coordinates all the backend modules and provides the main application flow.

Usage:
    python macsnap.py [--verbose] [--help]

Arguments:
    --verbose, -v    Enable verbose logging and debug output
    --help, -h       Show help message and exit
    --version        Show version information and exit
"""

import sys
import os
import argparse
import signal
import platform
from pathlib import Path
from typing import Optional, NoReturn

# Utils imports work fine without path modification

from utils.config_loader import load_configs, ConfigLoader
from utils.validators import ConfigValidator
from utils.installer import InstallationEngine
from utils.logger import MacSnapLogger, get_logger, close_logger
from ui.layout import run_macsnap_ui

# Application metadata
APP_NAME = "MacSnap Setup"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Interactive terminal application for macOS system setup and software installation"
REQUIRED_MACOS_VERSION = (10, 15)  # macOS 10.15 Catalina minimum
CONFIGS_DIR = "configs"

class MacSnapApp:
    """
    Main MacSnap Setup application.
    
    Coordinates all the backend modules and provides the main application flow.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the MacSnap application.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.logger: Optional[MacSnapLogger] = None
        self.config_loader: Optional[ConfigLoader] = None
        self.validator: Optional[ConfigValidator] = None
        self.engine: Optional[InstallationEngine] = None
        # UI will be handled by the run_macsnap_ui function
        
        # Setup signal handlers for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame) -> NoReturn:
        """Handle interrupt signals gracefully."""
        if self.logger:
            self.logger.info("\nReceived interrupt signal. Exiting gracefully...")
            self.logger.close()
        else:
            print("\nReceived interrupt signal. Exiting gracefully...")
        
        close_logger()
        sys.exit(0)
    
    def run(self) -> int:
        """
        Run the MacSnap application.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Initialize logging
            self._initialize_logging()
            
            # Validate system requirements
            if not self._check_system_requirements():
                return 1
            
            # Load and validate configurations
            if not self._load_configurations():
                return 1
            
            # Validate configurations
            if not self._validate_configurations():
                return 1
            
            # Initialize components
            self._initialize_components()
            
            # Run the main UI
            return self._run_main_interface()
            
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Application interrupted by user")
            else:
                print("Application interrupted by user")
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            if self.logger:
                self.logger.error(f"Application error: {e}")
            else:
                print(f"Application error: {e}")
            return 1
        finally:
            self._cleanup()
    
    def _initialize_logging(self):
        """Initialize the logging system."""
        self.logger = get_logger(verbose=self.verbose)
        self.logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        self.logger.debug(f"Python version: {sys.version}")
        self.logger.debug(f"Platform: {platform.platform()}")
        self.logger.debug(f"Working directory: {os.getcwd()}")
    
    def _check_system_requirements(self) -> bool:
        """
        Check system requirements.
        
        Returns:
            True if requirements are met, False otherwise
        """
        self.logger.info("Checking system requirements...")
        
        # Check macOS version
        if platform.system() != "Darwin":
            self.logger.error("MacSnap Setup requires macOS")
            return False
        
        try:
            macos_version = platform.mac_ver()[0]
            version_parts = [int(x) for x in macos_version.split('.')]
            current_version = tuple(version_parts[:2])
            
            if current_version < REQUIRED_MACOS_VERSION:
                self.logger.error(f"MacSnap Setup requires macOS {'.'.join(map(str, REQUIRED_MACOS_VERSION))} or later")
                self.logger.error(f"Current version: {macos_version}")
                return False
            
            self.logger.info(f"macOS version: {macos_version} ✅")
            
        except Exception as e:
            self.logger.warning(f"Could not determine macOS version: {e}")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.logger.error("MacSnap Setup requires Python 3.8 or later")
            self.logger.error(f"Current version: {sys.version}")
            return False
        
        self.logger.info(f"Python version: {sys.version.split()[0]} ✅")
        
        # Check configs directory
        configs_path = Path(CONFIGS_DIR)
        if not configs_path.exists():
            self.logger.error(f"Configuration directory '{CONFIGS_DIR}' not found")
            self.logger.error("Please ensure the configs directory exists and contains YAML configuration files")
            return False
        
        if not any(configs_path.glob("*.yml")):
            # Check subdirectories too
            yaml_files = list(configs_path.rglob("*.yml"))
            if not yaml_files:
                self.logger.error(f"No YAML configuration files found in '{CONFIGS_DIR}'")
                return False
        
        self.logger.info(f"Configuration directory: {configs_path.absolute()} ✅")
        
        # Check terminal capabilities
        try:
            import curses
            # Test if we can initialize curses (this doesn't actually start it)
            self.logger.debug("Terminal curses support: Available")
        except ImportError:
            self.logger.error("Terminal interface not supported (curses module not available)")
            return False
        
        # Check if we're running in a proper terminal
        if not sys.stdout.isatty():
            self.logger.warning("Not running in an interactive terminal")
            self.logger.warning("Some features may not work properly")
        
        self.logger.success("System requirements check passed")
        return True
    
    def _load_configurations(self) -> bool:
        """
        Load configuration files.
        
        Returns:
            True if configurations loaded successfully, False otherwise
        """
        self.logger.info("Loading configuration files...")
        
        try:
            self.config_loader = load_configs(CONFIGS_DIR)
            
            if not self.config_loader.configurations:
                self.logger.error("No valid configurations found")
                return False
            
            config_count = len(self.config_loader.configurations)
            category_count = len(self.config_loader.categories)
            
            self.logger.success(f"Loaded {config_count} configurations across {category_count} categories")
            
            # Log categories
            categories = sorted(self.config_loader.categories)
            self.logger.info(f"Categories: {', '.join(categories)}")
            
            # Log some statistics
            for category in categories:
                items_in_category = sum(1 for config in self.config_loader.configurations.values() 
                                      if config.category == category)
                self.logger.debug(f"  {category}: {items_in_category} items")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return False
    
    def _validate_configurations(self) -> bool:
        """
        Validate loaded configurations.
        
        Returns:
            True if validation passed, False if critical errors found
        """
        self.logger.info("Validating configurations...")
        
        try:
            self.validator = ConfigValidator()
            errors, warnings = self.validator.validate_all(self.config_loader.configurations)
            
            # Log warnings
            if warnings:
                self.logger.warning(f"Found {len(warnings)} configuration warnings:")
                for warning in warnings[:10]:  # Show first 10 warnings
                    self.logger.warning(f"  {warning.item_id}.{warning.field}: {warning.message}")
                
                if len(warnings) > 10:
                    self.logger.warning(f"  ... and {len(warnings) - 10} more warnings")
            
            # Check for critical errors
            if errors:
                self.logger.error(f"Found {len(errors)} critical configuration errors:")
                for error in errors:
                    self.logger.error(f"  {error.item_id}.{error.field}: {error.message}")
                
                self.logger.error("Cannot continue with critical configuration errors")
                return False
            
            # Test dependency resolution
            try:
                dependency_order = self.validator.get_dependency_order(self.config_loader.configurations)
                self.logger.debug(f"Dependency resolution successful: {len(dependency_order)} items ordered")
            except ValueError as e:
                self.logger.error(f"Dependency resolution failed: {e}")
                return False
            
            self.logger.success("Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def _initialize_components(self):
        """Initialize application components."""
        self.logger.info("Initializing application components...")
        
        # Initialize installation engine
        self.engine = InstallationEngine(verbose=self.verbose)
        self.logger.debug("Installation engine initialized")
        
        self.logger.success("Application components initialized")
    
    def _run_main_interface(self) -> int:
        """
        Run the main user interface.
        
        Returns:
            Exit code
        """
        self.logger.info("🚀 Starting modern Textual user interface...")
        
        try:
            # Show welcome message
            self._show_welcome_message()
            
            # Run the UI with Textual
            success = run_macsnap_ui(verbose=self.verbose)
            
            if success:
                self.logger.success("Application completed successfully")
                return 0
            else:
                self.logger.warning("Application completed with issues")
                return 1
                
        except Exception as e:
            self.logger.error(f"User interface error: {e}")
            return 1
    
    def _show_welcome_message(self):
        """Show welcome message and basic information."""
        self.logger.info("✨ Welcome to MacSnap Setup with Textual UI!")
        self.logger.info(f"🎯 Version: {APP_VERSION}")
        self.logger.info(f"📦 Loaded {len(self.config_loader.configurations)} software configurations")
        self.logger.info("🖱️  Use mouse and keyboard navigation")
        self.logger.info("⌨️  Keyboard shortcuts: Space=Toggle, Enter=Install, Q=Quit")
        self.logger.info("🎨 Rich interface with real-time updates")
        self.logger.separator()
    
    def _cleanup(self):
        """Clean up resources and close connections."""
        if self.logger:
            self.logger.debug("Cleaning up application resources...")
        
        # Close logger
        close_logger()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="macsnap",
        description=APP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python macsnap.py                 Run with default settings
    python macsnap.py --verbose       Run with verbose logging
    python macsnap.py --version       Show version information

For more information, visit: https://github.com/your-repo/macsnap-setup
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging and debug output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the MacSnap Setup application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Print basic info for non-verbose mode
    if not args.verbose:
        print(f"{APP_NAME} v{APP_VERSION}")
        print("Starting macOS setup and software installation...")
        print()
    
    # Create and run the application
    app = MacSnapApp(verbose=args.verbose)
    return app.run()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 