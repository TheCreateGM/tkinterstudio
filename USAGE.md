# TkinterStudio Usage Guide

## Quick Start

The easiest way to run TkinterStudio is to use the robust launcher:

```bash
python robust_launcher.py
```

This launcher will automatically try different startup methods if there are any issues.

## Alternative Launch Methods

### Method 1: Full IDE (Recommended)
```bash
python main.py
```

### Method 2: Minimal IDE (Lightweight)
```bash
python minimal_start.py
```

### Method 3: Test First
```bash
python test_run.py
```

## System Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- Operating System: Windows, macOS, or Linux

## Installation

1. Download or clone the TkinterStudio files
2. Open a terminal/command prompt
3. Navigate to the TkinterStudio directory
4. Run: `python robust_launcher.py`

## Features Overview

### Main Interface
- **Menu Bar**: File, Edit, View, Build, Format, Help
- **Toolbar**: Quick access buttons with icons
- **Solution Explorer**: File management panel
- **Toolbox**: Drag-and-drop widget library
- **Code Editor**: Syntax-highlighted Python editor
- **Form Designer**: Visual GUI designer
- **Properties Panel**: Widget property editor
- **Output Panel**: Code execution results

### Key Functions

#### File Operations
- **New** (Ctrl+N): Create new file
- **Open** (Ctrl+O): Open existing file
- **Save** (Ctrl+S): Save current file
- **Save As** (Ctrl+Shift+S): Save with new name

#### Code Operations
- **Run** (F5): Execute current Python code
- **Cut/Copy/Paste** (Ctrl+X/C/V): Text editing
- **Undo/Redo** (Ctrl+Z/Y): Edit history

#### Design Operations
- **Design View** (F8): Switch to form designer
- **Code View** (F7): Switch to code editor
- **Snap to Grid**: Align widgets to grid
- **Align Tools**: Align selected widgets
- **Same Size**: Make widgets same size

### Using the Form Designer

1. Click "Design" button or press F8
2. Drag widgets from Toolbox to form
3. Select widgets to edit properties
4. Use alignment tools to arrange widgets
5. Switch to Code view to see generated code
6. Run the generated code to test your GUI

### Widget Categories

- **Common Controls**: Button, Label, Entry, Text, etc.
- **Containers**: Frame, LabelFrame, Panel, etc.
- **Data**: Listbox, Treeview, DataGridView, etc.
- **Menus & Toolbars**: MenuStrip, ToolStrip, etc.
- **Dialogs**: File dialogs, color choosers, etc.

## Troubleshooting

### Common Issues

**Error: "No module named 'tkinter'"**
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- Use Python from python.org (Windows/macOS)

**Error: Import failures**
- Use `python robust_launcher.py` for automatic fallbacks
- Try `python minimal_start.py` for basic functionality

**Error: Icon loading issues**
- Icons are optional - the IDE will work without them
- Use text-only mode if icon errors persist

**Performance Issues**
- Close unused tabs
- Use minimal_start.py for better performance
- Disable snap-to-grid if slow

### Getting Help

1. Check error messages in terminal
2. Try different launch methods
3. Run `python test_run.py` to diagnose issues
4. Use minimal_start.py as backup

## Tips and Tricks

### Productivity Tips
- Use Ctrl+N for quick new files
- F5 to quickly run code
- F7/F8 to switch between code and design
- Double-click properties to edit them
- Use search in Toolbox to find widgets quickly

### Design Tips
- Start with a Frame or Panel as container
- Use snap-to-grid for alignment
- Group related widgets in containers
- Test your design frequently with F5
- Save your work regularly with Ctrl+S

### Code Tips
- Generated code is fully editable
- Add your own functions and logic
- Use the Output panel to debug
- Save before running to avoid losing changes

## Examples

The IDE includes several example files:
- `examples/hello_world.py`: Basic Tkinter example
- `examples/winforms_style.py`: Windows Forms style app
- `examples/toolbox_demo.py`: Toolbox demonstration

## File Structure

```
Tkinter IDE/
├── main.py              # Main IDE application
├── robust_launcher.py   # Recommended launcher
├── minimal_start.py     # Lightweight version
├── simple_icons.py      # Icon system
├── property_editor.py   # Property editor
├── welcome.py           # Welcome screen
├── examples/            # Example projects
├── preferences/         # User settings
└── screenshots/         # Documentation images
```

## Version Information

- Version: 1.0
- Style: Visual Studio 2010 Windows Forms
- License: Open Source
- Platform: Cross-platform (Windows, macOS, Linux)

For more detailed information, see README.md in the project directory.
