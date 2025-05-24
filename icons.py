# icons.py - Simple color-based icons for the IDE
import tkinter as tk
from tkinter import PhotoImage

# Dictionary to store loaded PhotoImage objects
_icon_cache = {}

def get_icon(name):
    """Get a PhotoImage icon by name"""
    if name in _icon_cache:
        return _icon_cache[name]
    
    # Define icon colors based on name
    colors = {
        "new": "#4CAF50",       # Green
        "open": "#2196F3",      # Blue
        "save": "#FFC107",      # Yellow
        "run": "#FF5722",       # Orange
        "design": "#9C27B0",    # Purple
        "code": "#3F51B5",      # Indigo
        "properties": "#795548", # Brown
        "toolbox": "#607D8B",   # Blue Grey
        "grid": "#BDBDBD",      # Grey
        "align_left": "#F44336",   # Red
        "align_right": "#F44336",  # Red
        "align_top": "#F44336",    # Red
        "align_bottom": "#F44336", # Red
        "align_center": "#F44336", # Red
        "align_middle": "#F44336", # Red
        "same_size": "#009688",   # Teal
        "solution": "#673AB7",    # Deep Purple
        "common_controls": "#8BC34A", # Light Green
        "containers": "#00BCD4",   # Cyan
        "data": "#FFEB3B",        # Yellow
        "dialogs": "#FF9800",     # Orange
        "components": "#9E9E9E",  # Grey
        "printing": "#607D8B",    # Blue Grey
        "layout": "#3F51B5",      # Indigo
        "menustrip": "#FF5722",   # Deep Orange
        "output": "#4CAF50"       # Green
    }
    
    # Create the icon with the appropriate color
    color = colors.get(name, "#CCCCCC")  # Default grey
    try:
        img = PhotoImage(width=16, height=16)
        img.put(color, to=(0, 0, 16, 16))
        _icon_cache[name] = img
        return img
    except Exception as e:
        print(f"Error creating icon {name}: {e}")
        return None

# Create a fallback icon
FALLBACK_ICON = get_icon("toolbox")  # Use toolbox icon as fallback