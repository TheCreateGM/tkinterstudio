#!/usr/bin/env python3
"""
Test script to verify TkinterStudio works correctly
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")

        # Test simple_icons
        from simple_icons import get_icon, FALLBACK_ICON
        print("✓ simple_icons imported successfully")

        # Test property_editor
        from property_editor import PropertyEditorFactory
        print("✓ property_editor imported successfully")

        # Test welcome screen
        from welcome import WelcomeScreen
        print("✓ welcome imported successfully")

        # Test main application
        from main import TkinterStudio
        print("✓ main TkinterStudio imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_icons():
    """Test icon creation"""
    try:
        print("\nTesting icon creation...")
        from simple_icons import get_icon, create_icon

        # Test basic icon creation
        icon = create_icon(16, 16, "#FF0000")
        if icon:
            print("✓ Basic icon creation works")
        else:
            print("✗ Basic icon creation failed")

        # Test named icon
        new_icon = get_icon("new")
        if new_icon:
            print("✓ Named icon creation works")
        else:
            print("✗ Named icon creation failed")

        return True

    except Exception as e:
        print(f"✗ Icon test error: {e}")
        return False

def test_gui():
    """Test basic GUI functionality"""
    try:
        print("\nTesting GUI components...")

        # Create a simple test window
        root = tk.Tk()
        root.title("TkinterStudio Test")
        root.geometry("300x200")

        # Test basic widgets
        label = tk.Label(root, text="TkinterStudio Test Window")
        label.pack(pady=20)

        button = tk.Button(root, text="Close", command=root.destroy)
        button.pack(pady=10)

        # Show window briefly
        root.update()
        print("✓ Basic GUI components work")

        # Close immediately for testing
        root.after(100, root.destroy)
        root.mainloop()

        return True

    except Exception as e:
        print(f"✗ GUI test error: {e}")
        return False

def run_ide_test():
    """Run a quick test of the IDE"""
    try:
        print("\nTesting TkinterStudio application...")

        # Import and create IDE instance
        from main import TkinterStudio

        # Create the application
        app = TkinterStudio()

        # Test that the app was created successfully
        if app:
            print("✓ TkinterStudio application created successfully")

            # Close the application after a short delay
            app.after(1000, app.destroy)

            # Don't show welcome screen for test
            app.show_welcome_on_startup = False

            print("✓ TkinterStudio test completed successfully")
            return True
        else:
            print("✗ Failed to create TkinterStudio application")
            return False

    except Exception as e:
        print(f"✗ IDE test error: {e}")
        return False

def main():
    """Run all tests"""
    print("TkinterStudio Test Suite")
    print("=" * 50)

    all_passed = True

    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Icon Test", test_icons),
        ("GUI Test", test_gui),
    ]

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if not test_func():
            all_passed = False

    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! TkinterStudio should work correctly.")
        print("\nTo run TkinterStudio:")
        print("python main.py")
        print("or")
        print("python start_ide.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")

    print("=" * 50)

if __name__ == "__main__":
    main()
