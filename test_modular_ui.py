#!/usr/bin/env python3
"""
Test script for the modular MacSnap UI components
"""

if __name__ == "__main__":
    try:
        # Test importing from the new modular UI
        from ui.layout import run_macsnap_ui
        
        print("✅ Successfully imported modular UI components")
        print("🚀 Starting MacSnap UI...")
        
        # Run the application
        success = run_macsnap_ui(verbose=True)
        
        if success:
            print("✅ MacSnap UI ran successfully")
        else:
            print("❌ MacSnap UI encountered an error")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the project root directory")
    except Exception as e:
        print(f"❌ Error: {e}") 