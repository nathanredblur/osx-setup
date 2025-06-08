#!/usr/bin/env python3
"""
Simple test script for the new ItemButtonList UI component.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader
from utils.ui import run_macsnap_ui

def main():
    """Test the UI with a simple configuration."""
    print("Testing MacSnap UI with ItemButtonList...")
    
    # Initialize config loader
    config_loader = ConfigLoader("configs")
    
    try:
        # Load configurations
        config_loader.load_configurations()
        print(f"Loaded {len(config_loader.configurations)} configurations")
        
        # Run UI
        success = run_macsnap_ui(verbose=True)
        
        if success:
            print("UI test completed successfully!")
        else:
            print("UI test failed or was cancelled.")
            
    except Exception as e:
        print(f"Error during UI test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 