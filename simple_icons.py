import tkinter as tk

# Simple module for creating icons in Tkinter applications
# Uses solid colors instead of images to avoid dependency issues

def create_icon(width=16, height=16, color="#CCCCCC"):
    """Create a simple solid color icon"""
    try:
        # Check if we have a root window
        if not tk._default_root:
            return None
        img = tk.PhotoImage(width=width, height=height)
        img.put(color, to=(0, 0, width, height))
        return img
    except Exception as e:
        # Silently fail during startup
        return None

# Icon cache to store created icons
icon_cache = {}

def get_icon(name):
    """Get an icon by name, creating it if it doesn't exist"""
    # Return None if no root window exists yet
    if not tk._default_root:
        return None
        
    if name in icon_cache:
        return icon_cache[name]
    
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
    icon = create_icon(16, 16, color)
    
    # Cache the icon
    if icon:
        icon_cache[name] = icon
    
    return icon

# Create a fallback icon (will be None if no root window exists yet)
FALLBACK_ICON = None

def get_fallback_icon():
    """Get or create fallback icon"""
    global FALLBACK_ICON
    if FALLBACK_ICON is None:
        FALLBACK_ICON = create_icon(16, 16, "#CCCCCC")
    return FALLBACK_ICON

def create_button_icon(text, width=16, height=16, fg="#000000", bg="#F0F0F0"):
    """Create a button icon with text"""
    return create_icon(width, height, bg)

def create_color_icon(color, width=16, height=16):
    """Create a color square icon"""
    return create_icon(width, height, color)