import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import platform

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def launch_ide():
    """Launch the TkinterStudio application"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_script):
        messagebox.showerror("Error", "main.py not found. Please make sure it's in the same directory.")
        return

    try:
        # Use pythonw on Windows to prevent console window
        if platform.system() == "Windows":
            subprocess.Popen(["pythonw", main_script])
        else:
            subprocess.Popen(["python3", main_script])
        print("IDE launched successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch IDE: {e}")

if __name__ == "__main__":
    if not check_dependencies():
        print("Error: Tkinter is not installed. Please install Tkinter to run this application.")
        sys.exit(1)

    launch_ide()
