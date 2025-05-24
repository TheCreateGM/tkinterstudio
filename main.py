import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
import re
import subprocess
import tempfile
import threading
import ctypes
import json
from functools import partial
from typing import List, Dict, Any, Optional, Tuple
from property_editor import PropertyEditorFactory
from simple_icons import get_icon, get_fallback_icon

# Try to import welcome screen, fall back if not available
try:
    from welcome import WelcomeScreen
    WELCOME_AVAILABLE = True
except ImportError as e:
    print(f"Welcome screen not available: {e}")
    WELCOME_AVAILABLE = False
    WelcomeScreen = None

class DragDropListbox(tk.Listbox):
    """Listbox with drag and drop functionality"""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind('<ButtonPress-1>', self.on_start)
        self.bind('<B1-Motion>', self.on_motion)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.drag_data = {'item': None, 'index': None, 'x': 0, 'y': 0}

    def on_start(self, event):
        # Record the item and current position
        self.drag_data['item'] = self.get(tk.ACTIVE)
        self.drag_data['index'] = self.nearest(event.y)
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def on_motion(self, event):
        # Compute how far mouse has moved
        offset_y = event.y - self.drag_data['y']
        # Move the item
        if self.drag_data['item']:
            self.selection_clear(0, tk.END)
            new_index = self.nearest(event.y)
            if new_index != self.drag_data['index']:
                self.delete(self.drag_data['index'])
                self.insert(new_index, self.drag_data['item'])
                self.drag_data['index'] = new_index
                self.selection_set(new_index)

    def on_release(self, event):
        # Reset the drag information
        self.drag_data = {'item': None, 'index': None, 'x': 0, 'y': 0}

class FileTab(ttk.Frame):
    """Tab containing a file editor"""

    def __init__(self, parent, filepath=None, content=None):
        super().__init__(parent)
        self.parent = parent
        self.filepath = filepath
        self.modified = False

        # Configure style
        self.editor = ScrolledText(self, wrap=tk.NONE, undo=True,
                                  background="#FFFFFF", foreground="#000000",
                                  insertbackground="#000000",
                                  selectbackground="#3399FF", selectforeground="#FFFFFF")

        # Set monospace font
        editor_font = font.Font(family="Consolas", size=10)
        self.editor.configure(font=editor_font)

        # Line numbers
        self.line_numbers = tk.Text(self, width=4, padx=5, takefocus=0,
                                    border=0, background='#F0F0F0',
                                    foreground='#808080', state='disabled')
        self.line_numbers.configure(font=editor_font)

        # Scrollbars
        h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.editor.xview)
        v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.on_scroll_both)
        self.editor.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Layout
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.editor.grid(row=0, column=1, sticky="nsew")
        v_scroll.grid(row=0, column=2, sticky="ns")
        h_scroll.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Set initial content
        if content is not None:
            self.editor.insert("1.0", content)

        # Set up events
        self.editor.bind("<<Modified>>", self.on_text_modified)
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        self.editor.bind("<KeyRelease>", self.update_line_numbers, add="+")
        self.update_line_numbers()

        # Python keywords for syntax highlighting
        self.python_keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is", "lambda",
            "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
        ]

        # Built-in functions
        self.python_builtins = [
            "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable",
            "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir", "divmod",
            "enumerate", "eval", "exec", "filter", "float", "format", "frozenset", "getattr",
            "globals", "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
            "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview", "min",
            "next", "object", "oct", "open", "ord", "pow", "print", "property", "range", "repr",
            "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod", "str",
            "sum", "super", "tuple", "type", "vars", "zip", "__import__"
        ]

    def on_scroll_both(self, *args):
        # Scroll both the editor and line numbers
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def on_text_modified(self, event=None):
        # Track modifications
        if not self.modified:
            self.modified = True
            idx = self.parent.index(self)
            self.parent.tab(idx, text=self.parent.tab(idx, "text") + " *")
        self.editor.edit_modified(False)  # Reset the flag

    def update_line_numbers(self, event=None):
        # Update line numbers in the editor
        line_count = self.editor.get("1.0", tk.END).count("\n")

        # Enable editing of line numbers
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        # Add line numbers
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, "{}\n".format(i))

        # Disable editing of line numbers
        self.line_numbers.config(state=tk.DISABLED)

    def highlight_syntax(self, event=None):
        # Clear previous highlighting
        content = self.editor.get("1.0", tk.END)
        self.editor.tag_remove("keyword", "1.0", tk.END)
        self.editor.tag_remove("string", "1.0", tk.END)
        self.editor.tag_remove("comment", "1.0", tk.END)
        self.editor.tag_remove("function", "1.0", tk.END)
        self.editor.tag_remove("builtin", "1.0", tk.END)

        # Configure tags
        self.editor.tag_configure("keyword", foreground="#0000FF")
        self.editor.tag_configure("string", foreground="#008000")
        self.editor.tag_configure("comment", foreground="#808080")
        self.editor.tag_configure("function", foreground="#800080")
        self.editor.tag_configure("builtin", foreground="#FF00FF")

        # Highlight keywords
        for keyword in self.python_keywords:
            start_pos = "1.0"
            pattern = r'\b' + keyword + r'\b'
            while True:
                start_pos = self.editor.search(pattern, start_pos, tk.END, regexp=True)
                if not start_pos:
                    break
                end_pos = "{}+{}c".format(start_pos, len(keyword))
                self.editor.tag_add("keyword", start_pos, end_pos)
                start_pos = end_pos

        # Highlight builtins
        for builtin in self.python_builtins:
            start_pos = "1.0"
            pattern = r'\b' + builtin + r'\b'
            while True:
                start_pos = self.editor.search(pattern, start_pos, tk.END, regexp=True)
                if not start_pos:
                    break
                end_pos = "{}+{}c".format(start_pos, len(builtin))
                self.editor.tag_add("builtin", start_pos, end_pos)
                start_pos = end_pos

        # Highlight strings
        string_pattern = r'(\".*?\"|\'.*?\')'
        start_pos = "1.0"
        while True:
            start_pos = self.editor.search(string_pattern, start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            match_text = self.editor.get(start_pos, self.editor.index(f"{start_pos} lineend"))
            match = re.search(string_pattern, match_text)
            if match:
                end_pos = "{}+{}c".format(start_pos, len(match.group(0)))
                self.editor.tag_add("string", start_pos, end_pos)
                start_pos = end_pos
            else:
                break

        # Highlight comments
        comment_pattern = r'#.*$'
        start_pos = "1.0"
        while True:
            start_pos = self.editor.search(comment_pattern, start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            end_pos = self.editor.index(f"{start_pos} lineend")
            self.editor.tag_add("comment", start_pos, end_pos)
            start_pos = f"{start_pos}+1l"

        # Highlight function definitions
        func_pattern = r'def\s+(\w+)\s*\('
        start_pos = "1.0"
        while True:
            start_pos = self.editor.search(func_pattern, start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            match_text = self.editor.get(start_pos, self.editor.index(f"{start_pos} lineend"))
            match = re.search(func_pattern, match_text)
            if match:
                func_name_start = "{}+{}c".format(start_pos, match.start(1) - match.start(0))
                func_name_end = "{}+{}c".format(start_pos, match.end(1) - match.start(0))
                self.editor.tag_add("function", func_name_start, func_name_end)
            start_pos = self.editor.index(f"{start_pos}+1l")

class DropFrame(ttk.Frame):
    """Frame that accepts drag and drop from files"""

    def __init__(self, master, callback, **kw):
        super().__init__(master, **kw)
        self.callback = callback

        if sys.platform == 'win32':
            # Register for drag and drop (Windows only)
            self.register_drop_target()
        else:
            # Fallback method for other platforms
            # This is a simplified implementation
            self.bind("<ButtonRelease-1>", self.on_drop)

    def register_drop_target(self):
        """Register as a drop target on Windows"""
        try:
            # Windows-specific OLE drag and drop
            self.drop_target = DropTarget(self, self.callback)
            self.bind("<Map>", lambda event: self.drop_target.register())
            self.bind("<Unmap>", lambda event: self.drop_target.unregister())
        except Exception as e:
            print(f"Could not register drop target: {e}")

    def on_drop(self, event):
        """Simple drag and drop implementation for non-Windows platforms"""
        try:
            # This is a fallback and won't catch real file drops from the OS
            # It's just here to show the UI interaction
            files = filedialog.askopenfilenames(
                parent=self,
                title="Select files to open",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            if files:
                for file in files:
                    self.callback(file)
        except Exception as e:
            print(f"Error during drop: {e}")

class DropTarget:
    """Windows-specific drag and drop handler"""

    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback

        # Placeholder for Windows-specific implementation
        # In a real implementation, you would use ctypes to interface with the Windows API
        # and handle the WM_DROPFILES message
        self.hwnd = None

    def register(self):
        """Register as a drop target with Windows"""
        if sys.platform == 'win32':
            try:
                # Get the handle to the Tkinter window
                self.hwnd = self.widget.winfo_id()

                # In a real implementation:
                # 1. Use DragAcceptFiles from the Windows API
                # 2. Set up a message handler for WM_DROPFILES
                # Here we're just showing the structure
                print(f"Registered window {self.hwnd} for drag and drop")
            except Exception as e:
                print(f"Failed to register drop target: {e}")

    def unregister(self):
        """Unregister as a drop target"""
        if self.hwnd:
            # In a real implementation, unregister from Windows drag and drop
            self.hwnd = None

class TkinterStudio(tk.Tk):
    """Main IDE application class"""

    def __init__(self):
        super().__init__()

        # Configure the window
        self.title("TkinterStudio - Visual Studio 2010 Windows Forms Designer")
        self.geometry("1200x800")
        self.minsize(900, 700)

        # Make window resizable
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Show welcome screen on startup
        self.show_welcome_on_startup = True

        # Set application icon (for Windows)
        if sys.platform == 'win32':
            self.iconbitmap(default='python.ico')

        # Set VS2010-like theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use the 'clam' theme as a base

        # Configure colors to match VS2010 with modern touches
        self.style.configure('TFrame', background='#F0F0F0')
        self.style.configure('TNotebook', background='#F0F0F0')
        self.style.configure('TNotebook.Tab', background='#E3E3E5', padding=[10, 2])
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#FFFFFF'), ('active', '#DCDCDC')],
                       foreground=[('selected', '#000000'), ('active', '#333333')])
        self.style.configure('Toolbutton', background='#F0F0F0')
        self.style.configure('TLabel', background='#F0F0F0')
        self.style.configure('PropertyGrid.TFrame', background='#F5F5F5')
        self.style.configure('Designer.TFrame', background='#FFFFFF')
        self.style.configure('Toolbar.TFrame', background='#E6E6E6')
        self.style.configure('Statusbar.TFrame', background='#CCCCCC')
        self.style.configure('Modern.TButton', padding=4)
        self.style.configure('Primary.TButton', background='#0078D7', foreground='white')
        self.style.map('Primary.TButton', background=[('active', '#005A9E')])

        # Tkinter widgets for toolbox (Windows Forms style)
        self.tkinter_widgets = {
            "Common Controls": [
                "Button", "Label", "LinkLabel", "Entry", "TextBox",
                "Checkbutton", "Radiobutton", "GroupBox", "PictureBox"
            ],
            "Containers": [
                "Frame", "Panel", "GroupBox", "TabControl", "SplitContainer"
            ],
            "Menus & Toolbars": [
                "MenuStrip", "ToolStrip", "StatusStrip", "ContextMenuStrip"
            ],
            "Data": [
                "DataGridView", "Listbox", "ListView", "TreeView", "ComboBox"
            ],
            "Components": [
                "Timer", "FileSystemWatcher", "EventLog", "DirectoryEntry"
            ],
            "Printing": [
                "PrintDocument", "PrintDialog", "PageSetupDialog"
            ],
            "Dialogs": [
                "OpenFileDialog", "SaveFileDialog", "ColorDialog", "FontDialog"
            ],
            "Tkinter Widgets": [
                "Frame", "LabelFrame", "Text", "Canvas", "Scale",
                "Scrollbar", "Spinbox", "PanedWindow", "Progressbar"
            ]
        }

        # Keep track of design grid
        self.grid_size = 8  # Grid size in pixels
        self.snap_to_grid = True

        # Track designer widgets
        self.design_widgets = {}
        self.selected_widget = None

        # Configure the main UI
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_status_bar()

        # Track open files
        self.open_files = {}
        self.current_file = None

        # Initialize toolbox
        self.populate_toolbox()

        # Show welcome screen
        self.after(500, self.show_welcome_screen)

        # Set up drag and drop
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set up file types
        self.file_types = [
            ("Python files", "*.py"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

    def create_menu(self):
        """Create the menu bar"""
        self.menu_bar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Solution Explorer", command=self.toggle_solution_explorer)
        view_menu.add_command(label="Toolbox", command=self.toggle_toolbox)
        view_menu.add_command(label="Properties", command=self.toggle_properties)
        view_menu.add_separator()
        view_menu.add_command(label="Code", command=self.view_code)
        view_menu.add_command(label="Designer", command=self.view_designer)
        view_menu.add_separator()
        view_menu.add_command(label="Output", command=self.toggle_output)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Build menu
        build_menu = tk.Menu(self.menu_bar, tearoff=0)
        build_menu.add_command(label="Run", accelerator="F5", command=self.run_code)
        build_menu.add_command(label="Generate Code from Design", command=self.generate_code_from_design)
        self.menu_bar.add_cascade(label="Build", menu=build_menu)

        # Format menu
        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        format_menu.add_command(label="Align Left", command=lambda: self.align_widgets("left"))
        format_menu.add_command(label="Align Right", command=lambda: self.align_widgets("right"))
        format_menu.add_command(label="Align Top", command=lambda: self.align_widgets("top"))
        format_menu.add_command(label="Align Bottom", command=lambda: self.align_widgets("bottom"))
        format_menu.add_separator()
        format_menu.add_command(label="Make Same Size", command=self.make_same_size)
        self.menu_bar.add_cascade(label="Format", menu=format_menu)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        # Set the menu bar
        self.config(menu=self.menu_bar)

        # Bind keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind("<F5>", lambda e: self.run_code())
        self.bind("<F7>", lambda e: self.view_code())
        self.bind("<F8>", lambda e: self.view_designer())

    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar = ttk.Frame(self, relief=tk.RAISED, style='Toolbar.TFrame')

        # Create buttons with icons
        btn_new = ttk.Button(self.toolbar, text="New", command=self.new_file)
        btn_open = ttk.Button(self.toolbar, text="Open", command=self.open_file)
        btn_save = ttk.Button(self.toolbar, text="Save", command=self.save_file)
        btn_run = ttk.Button(self.toolbar, text="Run", command=self.run_code, style="Primary.TButton")

        # Add icons if available (after main window is created)
        self.after(100, lambda: self.setup_toolbar_icons(btn_new, btn_open, btn_save, btn_run))

        # Add design mode toolbar buttons
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)

        # Design mode buttons
        self.btn_designer = ttk.Button(self.toolbar, text="Design", command=self.view_designer)
        self.btn_code = ttk.Button(self.toolbar, text="Code", command=self.view_code)
        self.btn_snap_grid = ttk.Checkbutton(self.toolbar, text="Snap to Grid", command=self.toggle_snap_to_grid)
        self.btn_align_left = ttk.Button(self.toolbar, text="⬅", command=lambda: self.align_widgets("left"))
        self.btn_align_right = ttk.Button(self.toolbar, text="➡", command=lambda: self.align_widgets("right"))
        self.btn_align_top = ttk.Button(self.toolbar, text="⬆", command=lambda: self.align_widgets("top"))
        self.btn_align_bottom = ttk.Button(self.toolbar, text="⬇", command=lambda: self.align_widgets("bottom"))
        self.btn_same_size = ttk.Button(self.toolbar, text="⚏", command=self.make_same_size)

        # Add icons if available (after main window is created)
        self.after(100, lambda: self.setup_designer_icons())

        # Tooltips for buttons
        self.create_tooltip(self.btn_align_left, "Align Left")
        self.create_tooltip(self.btn_align_right, "Align Right")
        self.create_tooltip(self.btn_align_top, "Align Top")
        self.create_tooltip(self.btn_align_bottom, "Align Bottom")
        self.create_tooltip(self.btn_same_size, "Make Same Size")

        # Add buttons to toolbar
        btn_new.pack(side=tk.LEFT, padx=3, pady=3)
        btn_open.pack(side=tk.LEFT, padx=3, pady=3)
        btn_save.pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        btn_run.pack(side=tk.LEFT, padx=3, pady=3)

        # Add design buttons
        self.btn_designer.pack(side=tk.LEFT, padx=3, pady=3)
        self.btn_code.pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        self.btn_snap_grid.pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        self.btn_align_left.pack(side=tk.LEFT, padx=2, pady=3)
        self.btn_align_right.pack(side=tk.LEFT, padx=2, pady=3)
        self.btn_align_top.pack(side=tk.LEFT, padx=2, pady=3)
        self.btn_align_bottom.pack(side=tk.LEFT, padx=2, pady=3)
        self.btn_same_size.pack(side=tk.LEFT, padx=2, pady=3)

        # Pack the toolbar
        self.toolbar.grid(row=0, column=0, sticky="ew")

    def create_main_area(self):
        """Create the main work area with editor and panels"""
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.grid(row=1, column=0, sticky="nsew")

        # Left panel for solution explorer and toolbox
        self.left_panel = ttk.Frame(self.main_paned)

        # Create a notebook for the left panel
        self.left_notebook = ttk.Notebook(self.left_panel)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)

        # Solution explorer tab
        self.solution_explorer_frame = ttk.Frame(self.left_notebook)
        self.solution_explorer = ttk.LabelFrame(self.solution_explorer_frame, text="Solution Explorer")
        self.solution_explorer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Solution explorer tree view
        self.project_tree = ttk.Treeview(self.solution_explorer)
        self.project_tree.pack(fill=tk.BOTH, expand=True)

        # File list with drag and drop
        self.file_list = DragDropListbox(self.solution_explorer, selectmode=tk.SINGLE)
        self.file_list.pack(fill=tk.BOTH, expand=True)
        self.file_list.bind("<Double-1>", self.on_file_double_click)

        # Make the solution explorer droppable
        self.dropframe = DropFrame(self.solution_explorer, self.open_dropped_file)
        self.dropframe.pack(fill=tk.BOTH, expand=True)

        # Toolbox tab (Windows Forms style)
        self.toolbox_frame = ttk.Frame(self.left_notebook)
        self.toolbox = ttk.LabelFrame(self.toolbox_frame, text="Toolbox")
        self.toolbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Search box for toolbox with modern styling
        self.search_frame = ttk.Frame(self.toolbox)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_toolbox)

        search_label = ttk.Label(self.search_frame, text="🔍 Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.search_button = ttk.Button(self.search_frame, text="×", width=2,
                                        command=lambda: self.search_var.set(""))
        self.search_button.pack(side=tk.RIGHT, padx=(2, 0))

        # Add tabs to left notebook
        self.left_notebook.add(self.solution_explorer_frame, text="Solution Explorer")
        self.left_notebook.add(self.toolbox_frame, text="Toolbox")

        # Right panel for editor, designer and output
        self.right_panel = ttk.Frame(self.main_paned)
        self.vertical_pane = ttk.PanedWindow(self.right_panel, orient=tk.VERTICAL)
        self.vertical_pane.pack(fill=tk.BOTH, expand=True)

        # Notebook for editor and designer tabs
        self.main_notebook = ttk.Notebook(self.vertical_pane)

        # Editor tab
        self.editor_frame = ttk.Frame(self.main_notebook)
        self.editor_notebook = ttk.Notebook(self.editor_frame)
        self.editor_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True)

        # Designer tab
        self.designer_frame = ttk.Frame(self.main_notebook)
        self.designer_pane = ttk.PanedWindow(self.designer_frame, orient=tk.HORIZONTAL)
        self.designer_pane.pack(fill=tk.BOTH, expand=True)

        # Design canvas (Windows Forms style)
        # Design canvas with modern styling
        self.design_frame = ttk.LabelFrame(self.designer_pane, text="Form Designer")

        # Add control panel above canvas
        self.design_control_frame = ttk.Frame(self.design_frame, style="Designer.TFrame")
        self.design_control_frame.pack(fill=tk.X, padx=5, pady=3)

        # Form size controls
        ttk.Label(self.design_control_frame, text="Form Size:").pack(side=tk.LEFT, padx=(5, 2))
        self.form_width_var = tk.StringVar(value="400")
        self.form_height_var = tk.StringVar(value="300")
        self.form_width_entry = ttk.Spinbox(self.design_control_frame, from_=200, to=1000,
                                          width=5, textvariable=self.form_width_var)
        self.form_width_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.design_control_frame, text="×").pack(side=tk.LEFT, padx=2)
        self.form_height_entry = ttk.Spinbox(self.design_control_frame, from_=150, to=800,
                                           width=5, textvariable=self.form_height_var)
        self.form_height_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(self.design_control_frame, text="Apply",
                  command=self.resize_form).pack(side=tk.LEFT, padx=5)

        # Add form canvas with scrollbars
        self.design_canvas_frame = ttk.Frame(self.design_frame, style="Designer.TFrame")
        self.design_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.design_canvas = tk.Canvas(self.design_canvas_frame, background="#FFFFFF",
                                     highlightthickness=1, highlightbackground="#CCCCCC")

        # Scrollbars for canvas
        self.design_h_scroll = ttk.Scrollbar(self.design_canvas_frame, orient=tk.HORIZONTAL,
                                          command=self.design_canvas.xview)
        self.design_v_scroll = ttk.Scrollbar(self.design_canvas_frame, orient=tk.VERTICAL,
                                          command=self.design_canvas.yview)

        self.design_canvas.configure(xscrollcommand=self.design_h_scroll.set,
                                  yscrollcommand=self.design_v_scroll.set)

        # Grid layout
        self.design_canvas.grid(row=0, column=0, sticky="nsew")
        self.design_h_scroll.grid(row=1, column=0, sticky="ew")
        self.design_v_scroll.grid(row=0, column=1, sticky="ns")

        self.design_canvas_frame.rowconfigure(0, weight=1)
        self.design_canvas_frame.columnconfigure(0, weight=1)

        # Create a form container on the canvas with a title bar
        try:
            form_width = int(self.form_width_var.get())
            form_height = int(self.form_height_var.get())
        except ValueError:
            form_width = 400
            form_height = 300
            self.form_width_var.set(str(form_width))
            self.form_height_var.set(str(form_height))

        # Form background
        self.form_container = self.design_canvas.create_rectangle(
            10, 30, 10+form_width, 30+form_height,
            fill="#F0F0F0", outline="#000000", tags=("form")
        )

        # Form title bar
        self.form_titlebar = self.design_canvas.create_rectangle(
            10, 10, 10+form_width, 30,
            fill="#0078D7", outline="#0078D7", tags=("form_titlebar")
        )

        # Form title
        self.form_title = self.design_canvas.create_text(
            20, 20, text="Form1", fill="white", anchor="w", tags=("form_title")
        )

        # Add grid lines to the form
        self.draw_grid_lines()

        # Properties panel (Windows Forms style)
        self.properties_frame = ttk.LabelFrame(self.designer_pane, text="Properties")

        # Property grid with category support
        self.property_notebook = ttk.Notebook(self.properties_frame)
        self.property_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Properties tab
        self.properties_tab = ttk.Frame(self.property_notebook, style='PropertyGrid.TFrame')
        self.property_notebook.add(self.properties_tab, text="Properties")

        # Property search
        self.prop_search_frame = ttk.Frame(self.properties_tab)
        self.prop_search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prop_search_var = tk.StringVar()
        self.prop_search_var.trace("w", self.filter_properties)
        self.prop_search_entry = ttk.Entry(self.prop_search_frame, textvariable=self.prop_search_var)
        self.prop_search_entry.pack(fill=tk.X)

        # Properties tree
        self.properties_tree = ttk.Treeview(self.properties_tab, columns=("property", "value"), show="headings")
        self.properties_tree.heading("property", text="Property")
        self.properties_tree.heading("value", text="Value")
        self.properties_tree.column("property", width=100)
        self.properties_tree.column("value", width=150)
        self.properties_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Events tab
        self.events_tab = ttk.Frame(self.property_notebook, style='PropertyGrid.TFrame')
        self.property_notebook.add(self.events_tab, text="Events")

        # Events tree
        self.events_tree = ttk.Treeview(self.events_tab, columns=("event", "handler"), show="headings")
        self.events_tree.heading("event", text="Event")
        self.events_tree.heading("handler", text="Handler")
        self.events_tree.column("event", width=100)
        self.events_tree.column("handler", width=150)
        self.events_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add editor and form property panels to designer pane
        self.designer_pane.add(self.design_frame, weight=3)
        self.designer_pane.add(self.properties_frame, weight=1)

        # Add tabs to main notebook
        self.main_notebook.add(self.editor_frame, text="Code")
        self.main_notebook.add(self.designer_frame, text="Design")

        # Output panel
        self.output_frame = ttk.LabelFrame(self.vertical_pane, text="Output")
        self.output_text = ScrolledText(self.output_frame, height=8, wrap=tk.WORD,
                                        background="#FFFFFF", foreground="#000000")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add panels to the paned window
        self.vertical_pane.add(self.main_notebook, weight=3)
        self.vertical_pane.add(self.output_frame, weight=1)

        self.main_paned.add(self.left_panel, weight=1)
        self.main_paned.add(self.right_panel, weight=3)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self, relief=tk.SUNKEN, style='Statusbar.TFrame')
        self.status_bar.grid(row=2, column=0, sticky="ew")

        self.status_label = ttk.Label(self.status_bar, text="Ready", style='Statusbar.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

        # Add a grip size indicator
        ttk.Sizegrip(self.status_bar).pack(side=tk.RIGHT, padx=2, pady=2)

        self.line_col_label = ttk.Label(self.status_bar, text="Ln 1, Col 1", style='Statusbar.TLabel')
        self.line_col_label.pack(side=tk.RIGHT, padx=5, pady=2)

        # Add position indicator for design mode
        self.position_label = ttk.Label(self.status_bar, text="", style='Statusbar.TLabel')
        self.position_label.pack(side=tk.RIGHT, padx=15, pady=2)

    def new_file(self):
        """Create a new file tab"""
        tab = FileTab(self.editor_notebook)
        self.editor_notebook.add(tab, text="Untitled")
        self.editor_notebook.select(self.editor_notebook.index(tk.END) - 1)

        # Focus the editor
        tab.editor.focus_set()

    def open_file(self):
        """Open a file dialog and load file into editor"""
        filepath = filedialog.askopenfilename(
            title="Open File",
            filetypes=self.file_types
        )

        if filepath:
            self.open_specific_file(filepath)

    def open_specific_file(self, filepath):
        """Open a specific file into the editor"""
        if filepath in self.open_files:
            # File already open, switch to its tab
            self.editor_notebook.select(self.open_files[filepath])
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Create new tab with file content
            tab = FileTab(self.editor_notebook, filepath=filepath, content=content)
            filename = os.path.basename(filepath)

            # Add to notebook
            self.editor_notebook.add(tab, text=filename)
            tab_index = self.editor_notebook.index(tk.END) - 1
            self.editor_notebook.select(tab_index)

            # Update tracking
            self.open_files[filepath] = tab_index
            self.current_file = filepath

            # Add to file list
            if filename not in self.file_list.get(0, tk.END):
                self.file_list.insert(tk.END, filename)

            # Update status
            self.status_label.config(text=f"Opened {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def open_dropped_file(self, filepath):
        """Handle files dropped onto the solution explorer"""
        if os.path.isfile(filepath):
            self.open_specific_file(filepath)

    def save_file(self):
        """Save the current file"""
        current = self.editor_notebook.select()
        if not current:
            return

        tab = self.editor_notebook.nametowidget(current)

        if not hasattr(tab, 'filepath') or not tab.filepath:
            self.save_file_as()
            return

        try:
            content = tab.editor.get("1.0", tk.END)
            with open(tab.filepath, 'w') as f:
                f.write(content)

            # Update tab state
            tab.modified = False
            idx = self.editor_notebook.index(current)
            filename = os.path.basename(tab.filepath)
            self.editor_notebook.tab(idx, text=filename)

            # Update status
            self.status_label.config(text=f"Saved {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def save_file_as(self):
        """Save the current file with a new name"""
        current = self.editor_notebook.select()
        if not current:
            return

        tab = self.editor_notebook.nametowidget(current)

        initial_file = tab.filepath if hasattr(tab, 'filepath') and tab.filepath else ""
        filepath = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=self.file_types,
            initialfile=os.path.basename(initial_file) if initial_file else ""
        )

        if not filepath:
            return

        # Update tab information
        tab.filepath = filepath

        # If this was a new file, update tracking
        if initial_file in self.open_files:
            del self.open_files[initial_file]

        self.open_files[filepath] = self.editor_notebook.index(current)
        self.current_file = filepath

        # Now save the file
        self.save_file()

        # Add to file list if not already there
        filename = os.path.basename(filepath)
        if filename not in self.file_list.get(0, tk.END):
            self.file_list.insert(tk.END, filename)

    def run_code(self):
        """Run the current Python file"""
        current = self.editor_notebook.select()
        if not current:
            return

        tab = self.editor_notebook.nametowidget(current)

        # Save if modified
        if tab.modified:
            result = messagebox.askyesnocancel(
                "Save Changes",
                "Save changes before running?",
                icon=messagebox.QUESTION
            )

            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()

        # Get the code to run
        if hasattr(tab, 'filepath') and tab.filepath and os.path.exists(tab.filepath):
            script_path = tab.filepath
            self._run_python_script(script_path)
        else:
            # Run unsaved code
            content = tab.editor.get("1.0", tk.END)
            self._run_python_code(content)

    def _run_python_script(self, script_path):
        """Run a Python script file"""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Running {os.path.basename(script_path)}...\n\n")

        # Run in a separate thread to keep the UI responsive
        thread = threading.Thread(
            target=self._execute_python,
            args=(["python", script_path],)
        )
        thread.daemon = True
        thread.start()

    def _run_python_code(self, code):
        """Run Python code from a string"""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Running code...\n\n")

        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.py')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)

            # Run the temporary file
            thread = threading.Thread(
                target=self._execute_python,
                args=(["python", path],)
            )
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}\n")

    def _execute_python(self, command):
        """Execute a Python process and capture output"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            # Update UI in the main thread
            self.after(0, lambda: self._update_output(stdout, stderr, process.returncode))

        except Exception as e:
            self.after(0, lambda: self._update_output("", str(e), 1))

    def _update_output(self, stdout, stderr, returncode):
        """Update the output panel with process results"""
        if stdout:
            self.output_text.insert(tk.END, stdout)

        if stderr:
            self.output_text.insert(tk.END, stderr, "error")
            self.output_text.tag_configure("error", foreground="red")

        if returncode == 0:
            self.output_text.insert(tk.END, "\nProcess completed successfully.\n")
        else:
            self.output_text.insert(tk.END, f"\nProcess exited with code {returncode}.\n", "error")

        # Scroll to the end
        self.output_text.see(tk.END)

    def on_tab_changed(self, event):
        """Handle tab change events"""
        current = self.editor_notebook.select()
        if not current:
            return

        tab = self.editor_notebook.nametowidget(current)
        if hasattr(tab, 'filepath') and tab.filepath:
            self.current_file = tab.filepath
            self.status_label.config(text=f"Current file: {os.path.basename(tab.filepath)}")

    def on_file_double_click(self, event):
        """Handle double click on file in the file list"""
        selection = self.file_list.curselection()
        if not selection:
            return

        filename = self.file_list.get(selection[0])

        # Find the file in open_files
        for filepath, tab_index in self.open_files.items():
            if os.path.basename(filepath) == filename:
                self.editor_notebook.select(tab_index)
                return

    def toggle_solution_explorer(self):
        """Toggle visibility of solution explorer"""
        if self.left_panel.winfo_ismapped():
            self.main_paned.forget(self.left_panel)
        else:
            self.main_paned.add(self.left_panel, weight=1)
            self.main_paned.pane(0, weight=1)
            self.main_paned.pane(1, weight=3)
            self.left_notebook.select(0)  # Select solution explorer tab

    def toggle_toolbox(self):
        """Toggle visibility of toolbox"""
        if self.left_panel.winfo_ismapped():
            self.left_notebook.select(1)  # Select toolbox tab
        else:
            self.main_paned.add(self.left_panel, weight=1)
            self.main_paned.pane(0, weight=1)
            self.main_paned.pane(1, weight=3)
            self.left_notebook.select(1)  # Select toolbox tab

    def toggle_properties(self):
        """Toggle visibility of properties panel"""
        if not self.properties_frame.winfo_ismapped():
            self.designer_pane.add(self.properties_frame, weight=1)
            self.designer_pane.pane(0, weight=3)
            self.designer_pane.pane(1, weight=1)
        else:
            self.designer_pane.forget(self.properties_frame)

    def view_code(self):
        """Switch to code view"""
        self.main_notebook.select(0)

    def view_designer(self):
        """Switch to designer view"""
        self.main_notebook.select(1)

    def toggle_output(self):
        """Toggle visibility of output panel"""
        if self.output_frame.winfo_ismapped():
            self.vertical_pane.forget(self.output_frame)
        else:
            self.vertical_pane.add(self.output_frame, weight=1)
            self.vertical_pane.pane(0, weight=3)
            self.vertical_pane.pane(1, weight=1)

    # Edit operations
    def undo(self):
        """Undo last edit"""
        current = self.editor_notebook.select()
        if current:
            tab = self.editor_notebook.nametowidget(current)
            try:
                tab.editor.edit_undo()
            except tk.TclError:
                # No more undo actions
                pass

    def redo(self):
        """Redo last undone edit"""
        current = self.editor_notebook.select()
        if current:
            tab = self.editor_notebook.nametowidget(current)
            try:
                tab.editor.edit_redo()
            except tk.TclError:
                # No more redo actions
                pass

    def cut(self):
        """Cut selected text to clipboard"""
        current = self.editor_notebook.select()
        if current:
            tab = self.editor_notebook.nametowidget(current)
            if tab.editor.tag_ranges(tk.SEL):
                tab.editor.event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text to clipboard"""
        current = self.editor_notebook.select()
        if current:
            tab = self.editor_notebook.nametowidget(current)
            if tab.editor.tag_ranges(tk.SEL):
                tab.editor.event_generate("<<Copy>>")

    def paste(self):
        """Paste clipboard text"""
        current = self.editor_notebook.select()
        if current:
            tab = self.editor_notebook.nametowidget(current)
            tab.editor.event_generate("<<Paste>>")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About TkinterStudio",
            "TkinterStudio - Visual Studio 2010 Style\n\n"
            "A Python IDE built with Tkinter\n"
            "Featuring syntax highlighting, run capabilities, and drag & drop\n\n"
            "Created as a demonstration"
        )

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            try:
                x, y, _, _ = widget.bbox("insert")
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 25
            except:
                # Fallback if bbox fails
                x = event.x_root + 10
                y = event.y_root + 10

            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = ttk.Label(self.tooltip, text=text, background="#FFFFE0", relief=tk.SOLID, borderwidth=1)
            label.pack()

        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def on_close(self):
        """Handle window close event"""
        # Check for unsaved changes
        for tab_id in self.editor_notebook.tabs():
            tab = self.editor_notebook.nametowidget(tab_id)
            if hasattr(tab, 'modified') and tab.modified:
                result = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    "You have unsaved changes. Save before closing?",
                    icon=messagebox.QUESTION
                )

                if result is None:  # Cancel
                    return
                elif result:  # Yes
                    self.editor_notebook.select(tab_id)
                    self.save_file()

        # Save preferences
        self.save_preferences()

        # Destroy the window
        self.destroy()

    def setup_toolbar_icons(self, btn_new, btn_open, btn_save, btn_run):
        """Setup toolbar icons after main window is created"""
        try:
            if get_icon("new"):
                btn_new.config(image=get_icon("new"), compound=tk.LEFT)
            if get_icon("open"):
                btn_open.config(image=get_icon("open"), compound=tk.LEFT)
            if get_icon("save"):
                btn_save.config(image=get_icon("save"), compound=tk.LEFT)
            if get_icon("run"):
                btn_run.config(image=get_icon("run"), compound=tk.LEFT)
        except Exception as e:
            print(f"Could not setup toolbar icons: {e}")

    def setup_designer_icons(self):
        """Setup designer icons after main window is created"""
        try:
            if get_icon("design"):
                self.btn_designer.config(image=get_icon("design"), compound=tk.LEFT)
            if get_icon("code"):
                self.btn_code.config(image=get_icon("code"), compound=tk.LEFT)
            if get_icon("grid"):
                self.btn_snap_grid.config(image=get_icon("grid"), compound=tk.LEFT)
            if get_icon("align_left"):
                self.btn_align_left.config(image=get_icon("align_left"))
            if get_icon("align_right"):
                self.btn_align_right.config(image=get_icon("align_right"))
            if get_icon("align_top"):
                self.btn_align_top.config(image=get_icon("align_top"))
            if get_icon("align_bottom"):
                self.btn_align_bottom.config(image=get_icon("align_bottom"))
            if get_icon("same_size"):
                self.btn_same_size.config(image=get_icon("same_size"))
        except Exception as e:
            print(f"Could not setup designer icons: {e}")

    def save_preferences(self):
        """Save user preferences"""
        # Save preferences
        try:
            prefs = {
                "show_welcome_on_startup": self.show_welcome_on_startup,
                "window_size": self.geometry()
            }

            # Create preferences directory if it doesn't exist
            prefs_dir = "preferences"
            if not os.path.exists(prefs_dir):
                os.makedirs(prefs_dir)

            with open(os.path.join(prefs_dir, "settings.json"), "w") as f:
                json.dump(prefs, f)
        except Exception as e:
            # Print error but don't crash
            print(f"Could not save preferences: {e}")

    def load_preferences(self):
        """Load user preferences"""
        try:
            prefs_file = os.path.join("preferences", "settings.json")
            if os.path.exists(prefs_file):
                with open(prefs_file, "r") as f:
                    prefs = json.load(f)

                self.show_welcome_on_startup = prefs.get("show_welcome_on_startup", True)
        except Exception as e:
            # Use defaults if we can't load preferences
            print(f"Could not load preferences: {e}")
            self.show_welcome_on_startup = True

    def populate_toolbox(self):
        """Populate the toolbox with Tkinter widgets in Windows Forms style"""
        # Create a treeview for the toolbox categories
        self.toolbox_tree = ttk.Treeview(self.toolbox, style="Toolbox.Treeview")
        self.toolbox_tree.pack(fill=tk.BOTH, expand=True)

        # Configure style
        self.style.configure("Toolbox.Treeview", rowheight=24)

        # Add categories and widgets with icons
        category_icons = {
            "Common Controls": "common_controls",
            "Containers": "containers",
            "Data": "data",
            "Menus & Toolbars": "menustrip",
            "Dialogs": "dialogs",
            "Components": "components",
            "Printing": "printing"
        }

        # Add categories and widgets
        for category, widgets in self.tkinter_widgets.items():
            # Get category icon
            icon = get_icon(category_icons.get(category, "toolbox"))
            category_id = self.toolbox_tree.insert("", "end", text=category, image=icon, open=True)

            for widget in widgets:
                # We would create widget-specific icons here, but for now use a generic one
                self.toolbox_tree.insert(category_id, "end", text=widget)

        # Bind selection
        self.toolbox_tree.bind("<<TreeviewSelect>>", self.on_toolbox_select)

        # Add drag and drop support
        self.toolbox_tree.bind("<ButtonPress-1>", self.on_toolbox_press)
        self.toolbox_tree.bind("<B1-Motion>", self.on_toolbox_drag)
        self.toolbox_tree.bind("<ButtonRelease-1>", self.on_toolbox_release)

        # Expand all categories
        for category_id in self.toolbox_tree.get_children():
            self.toolbox_tree.item(category_id, open=True)

    def filter_toolbox(self, *args):
        """Filter toolbox items based on search text"""
        search_text = self.search_var.get().lower()

        # Clear tree
        for item in self.toolbox_tree.get_children():
            self.toolbox_tree.delete(item)

        # Repopulate with filtered items
        if not search_text:
            # Show all categories and widgets
            for category, widgets in self.tkinter_widgets.items():
                category_id = self.toolbox_tree.insert("", "end", text=category)

                for widget in widgets:
                    self.toolbox_tree.insert(category_id, "end", text=widget)

                # Expand all categories
                self.toolbox_tree.item(category_id, open=True)
        else:
            # Show only matching widgets
            for category, widgets in self.tkinter_widgets.items():
                matching_widgets = [w for w in widgets if search_text in w.lower()]

                if matching_widgets:
                    category_id = self.toolbox_tree.insert("", "end", text=category)

                    for widget in matching_widgets:
                        self.toolbox_tree.insert(category_id, "end", text=widget)

                    # Expand filtered categories
                    self.toolbox_tree.item(category_id, open=True)

    def filter_properties(self, *args):
        """Filter properties based on search text"""
        if not self.selected_widget:
            return

        search_text = self.prop_search_var.get().lower()
        widget_info = self.design_widgets[self.selected_widget]

        # Clear tree
        for item in self.properties_tree.get_children():
            self.properties_tree.delete(item)

        # Repopulate with filtered properties
        for prop, value in widget_info["properties"].items():
            if not search_text or search_text in prop.lower():
                self.properties_tree.insert("", "end", values=(prop, value))

    def draw_grid_lines(self):
        """Draw grid lines on the design canvas"""
        if not self.snap_to_grid:
            return

        # Get canvas dimensions
        canvas_width = self.design_canvas.winfo_width()
        canvas_height = self.design_canvas.winfo_height()

        # If canvas is not yet sized, use some defaults
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 300

        # Clear existing grid lines
        self.design_canvas.delete("grid_line")

        # Draw grid lines
        for x in range(0, canvas_width, self.grid_size):
            self.design_canvas.create_line(
                x, 0, x, canvas_height,
                fill="#EEEEEE", tags=("grid_line")
            )

        for y in range(0, canvas_height, self.grid_size):
            self.design_canvas.create_line(
                0, y, canvas_width, y,
                fill="#EEEEEE", tags=("grid_line")
            )

        # Bring widgets to front
        self.design_canvas.tag_raise("widget")
        self.design_canvas.tag_raise("widget_text")

    def toggle_snap_to_grid(self):
        """Toggle snap to grid functionality"""
        self.snap_to_grid = not self.snap_to_grid

        if self.snap_to_grid:
            self.draw_grid_lines()
        else:
            self.design_canvas.delete("grid_line")

    def on_toolbox_press(self, event):
        """Handle mouse press on toolbox for drag and drop"""
        item = self.toolbox_tree.identify_row(event.y)

        if item and self.toolbox_tree.parent(item):  # If it's a widget, not a category
            self._drag_data = {
                "item": item,
                "widget": self.toolbox_tree.item(item, "text"),
                "x": event.x,
                "y": event.y
            }

    def on_toolbox_drag(self, event):
        """Handle dragging from toolbox"""
        if not hasattr(self, "_drag_data") or not self._drag_data:
            return

        # Create a drag image if it doesn't exist
        if not hasattr(self, "_drag_image"):
            widget_name = self._drag_data["widget"]

            # Create a small image to represent the dragged widget
            self._drag_image = tk.Toplevel(self)
            self._drag_image.overrideredirect(True)
            self._drag_image.attributes("-topmost", True)
            self._drag_image.attributes("-alpha", 0.7)

            # Label for drag image
            tk.Label(self._drag_image, text=widget_name, bg="#CCCCFF",
                   relief=tk.RAISED, padx=10, pady=5).pack()

            # Position near cursor
            self._drag_image.geometry(f"+{event.x_root+10}+{event.y_root+10}")

        else:
            # Move the drag image with the cursor
            self._drag_image.geometry(f"+{event.x_root+10}+{event.y_root+10}")

    def on_toolbox_release(self, event):
        """Handle release of toolbox drag"""
        if not hasattr(self, "_drag_data") or not self._drag_data:
            return

        # Check if we're over the design canvas
        if self.main_notebook.select() == str(self.designer_frame):
            # Get mouse position relative to canvas
            x = self.design_canvas.winfo_pointerx() - self.design_canvas.winfo_rootx()
            y = self.design_canvas.winfo_pointery() - self.design_canvas.winfo_rooty()

            # Add widget at the drop position
            widget_name = self._drag_data["widget"]
            self.add_widget_to_design_at_position(widget_name, x, y)

        # Clean up
        if hasattr(self, "_drag_image"):
            self._drag_image.destroy()
            del self._drag_image

        self._drag_data = None

    def on_toolbox_select(self, event):
        """Handle toolbox item selection"""
        selection = self.toolbox_tree.selection()
        if selection:
            item = self.toolbox_tree.item(selection[0])

            # Check if this is a widget (not a category)
            if self.toolbox_tree.parent(selection[0]):
                widget_name = item["text"]
                self.add_widget_to_design(widget_name)

                # Reset selection
                self.toolbox_tree.selection_remove(selection[0])

    def add_widget_to_design(self, widget_name):
        """Add a widget to the design canvas at default position"""
        self.add_widget_to_design_at_position(widget_name, 50, 50)

    def add_widget_to_design_at_position(self, widget_name, x, y):
        """Add a widget to the design canvas at specified position"""
        # Switch to designer view
        self.view_designer()

        # Create a visual representation of the widget
        width, height = 100, 30
        if widget_name in ["Frame", "Panel", "GroupBox", "TabControl", "SplitContainer"]:
            width, height = 200, 150
        elif widget_name in ["TextBox", "DataGridView", "ListView", "TreeView"]:
            width, height = 150, 100
        elif widget_name in ["MenuStrip", "ToolStrip", "StatusStrip"]:
            width, height = 200, 25

        # Apply grid snapping if enabled
        if self.snap_to_grid:
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size
            width = round(width / self.grid_size) * self.grid_size
            height = round(height / self.grid_size) * self.grid_size

        # Create widget on canvas
        widget_id = self.design_canvas.create_rectangle(
            x, y, x+width, y+height,
            fill="#FFFFFF", outline="#000000", tags=("widget", widget_name),
            width=1
        )

        # Create resize handles
        handle_size = 6
        handles = {}

        # Create corner and edge resize handles
        handle_positions = [
            ("nw", x, y),
            ("n", x + width/2, y),
            ("ne", x + width, y),
            ("e", x + width, y + height/2),
            ("se", x + width, y + height),
            ("s", x + width/2, y + height),
            ("sw", x, y + height),
            ("w", x, y + height/2)
        ]

        for pos, hx, hy in handle_positions:
            handle_id = self.design_canvas.create_rectangle(
                hx - handle_size/2, hy - handle_size/2,
                hx + handle_size/2, hy + handle_size/2,
                fill="#FFFFFF", outline="#000000",
                tags=("handle", f"handle_{pos}", f"handle_for_{widget_id}"),
                state="hidden"
            )
            handles[pos] = handle_id

        # Add label
        text_id = self.design_canvas.create_text(
            x+(width/2), y+(height/2),
            text=widget_name, tags=("widget_text", widget_name, f"text_for_{widget_id}")
        )

        # Generate a unique name for the widget
        widget_base_name = widget_name.lower()
        widget_count = 1
        widget_name_id = f"{widget_base_name}{widget_count}"

        # Store widget info
        self.design_widgets[widget_id] = {
            "name": widget_name_id,
            "type": widget_name,
            "text_id": text_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "handles": handles,
            "properties": self.get_default_properties(widget_name)
        }

        # Select the new widget
        self.select_design_widget(widget_id)

        # Make widgets draggable
        self.design_canvas.tag_bind("widget", "<ButtonPress-1>", self.on_widget_press)
        self.design_canvas.tag_bind("widget", "<B1-Motion>", self.on_widget_drag)
        self.design_canvas.tag_bind("widget", "<ButtonRelease-1>", self.on_widget_release)

        # Make handles draggable for resizing
        self.design_canvas.tag_bind("handle", "<ButtonPress-1>", self.on_handle_press)
        self.design_canvas.tag_bind("handle", "<B1-Motion>", self.on_handle_drag)
        self.design_canvas.tag_bind("handle", "<ButtonRelease-1>", self.on_handle_release)

        # Generate code
        self.generate_code_from_design()

        return widget_id

    def get_default_properties(self, widget_name):
        """Get default properties for a widget"""
        return PropertyEditorFactory.get_default_properties(widget_name)

    def select_design_widget(self, widget_id):
        """Select a widget in the design canvas"""
        # Deselect previous selection
        if self.selected_widget:
            self.design_canvas.itemconfig(self.selected_widget, outline="#000000", width=1)

            # Hide handles for previously selected widget
            if self.selected_widget in self.design_widgets:
                for handle_id in self.design_widgets[self.selected_widget]["handles"].values():
                    self.design_canvas.itemconfig(handle_id, state="hidden")

        # Select new widget
        self.selected_widget = widget_id
        self.design_canvas.itemconfig(widget_id, outline="#3399FF", width=2)

        # Show handles for selected widget
        if widget_id in self.design_widgets:
            for handle_id in self.design_widgets[widget_id]["handles"].values():
                self.design_canvas.itemconfig(handle_id, state="normal")

        # Update properties panel
        self.update_properties_panel()

    def update_properties_panel(self):
        """Update properties panel for selected widget"""
        # Clear existing properties
        for item in self.properties_tree.get_children():
            self.properties_tree.delete(item)

        if not self.selected_widget:
            return

        # Get widget properties
        widget_info = self.design_widgets[self.selected_widget]

        # Add properties to the tree
        for prop, value in widget_info["properties"].items():
            self.properties_tree.insert("", "end", values=(prop, value))

        # Make properties editable with double-click
        self.properties_tree.bind("<Double-1>", self.edit_property)

        # Add Edit Properties button
        edit_btn = ttk.Button(
            self.properties_frame,
            text="Edit Properties...",
            command=lambda: self.edit_property(None)
        )
        edit_btn.pack(pady=5, padx=5)

    def edit_property(self, event):
        """Edit a property value using the property editor"""
        item = self.properties_tree.identify_row(event.y)
        column = self.properties_tree.identify_column(event.x)

        if not self.selected_widget:
            return

        # Open the property editor dialog
        widget_info = self.design_widgets[self.selected_widget]
        widget_type = widget_info["type"]

        # Create the property editor
        def update_properties(updated_props):
            # Update the widget properties
            widget_info["properties"].update(updated_props)

            # Update the properties tree
            self.update_properties_panel()

            # Update the widget visual
            self.update_design_widget(self.selected_widget)

            # Generate updated code
            self.generate_code_from_design()

        # Open the property editor dialog
        PropertyEditorFactory.create_editor(
            self,
            widget_type,
            widget_info["properties"],
            update_properties
        )

    def update_design_widget(self, widget_id):
        """Update the visual representation of a widget"""
        if widget_id not in self.design_widgets:
            return

        widget_info = self.design_widgets[widget_id]

        # Update text if applicable
        if "text" in widget_info["properties"]:
            self.design_canvas.itemconfig(
                widget_info["text_id"],
                text=widget_info["properties"]["text"]
            )

        # Update size if applicable
        if "width" in widget_info["properties"] and "height" in widget_info["properties"]:
            try:
                width = int(widget_info["properties"]["width"])
                height = int(widget_info["properties"]["height"])

                # Minimum dimensions
                width = max(width, 30)
                height = max(height, 20)

                # Apply grid snapping if enabled
                if self.snap_to_grid:
                    width = round(width / self.grid_size) * self.grid_size
                    height = round(height / self.grid_size) * self.grid_size

                # Update coordinates
                x, y = widget_info["x"], widget_info["y"]
                self.design_canvas.coords(
                    widget_id,
                    x, y, x + width, y + height
                )

                # Center the text
                self.design_canvas.coords(
                    widget_info["text_id"],
                    x + (width / 2),
                    y + (height / 2)
                )

                # Update handle positions
                handle_positions = {
                    "nw": (x, y),
                    "n": (x + width/2, y),
                    "ne": (x + width, y),
                    "e": (x + width, y + height/2),
                    "se": (x + width, y + height),
                    "s": (x + width/2, y + height),
                    "sw": (x, y + height),
                    "w": (x, y + height/2)
                }

                handle_size = 6
                for pos, (hx, hy) in handle_positions.items():
                    if pos in widget_info["handles"]:
                        handle_id = widget_info["handles"][pos]
                        self.design_canvas.coords(
                            handle_id,
                            hx - handle_size/2, hy - handle_size/2,
                            hx + handle_size/2, hy + handle_size/2
                        )

                # Update stored dimensions
                widget_info["width"] = width
                widget_info["height"] = height
            except ValueError:
                pass

    def on_widget_press(self, event):
        """Handle widget selection on press"""
        # Find the widget under cursor
        item = self.design_canvas.find_withtag("current")[0]
        if item in self.design_widgets:
            self.select_design_widget(item)

            # Store initial position for dragging
            self._drag_data = {
                "x": event.x,
                "y": event.y,
                "item": item,
                "type": "move"
            }

            # Bring selected widget to front
            self.design_canvas.tag_raise(item)
            self.design_canvas.tag_raise(self.design_widgets[item]["text_id"])

            # Raise handles to top
            for handle_id in self.design_widgets[item]["handles"].values():
                self.design_canvas.tag_raise(handle_id)

            # Bind double-click to edit properties
            self.design_canvas.bind("<Double-1>", lambda e: self.edit_property(None))

    def on_widget_drag(self, event):
        """Handle widget dragging"""
        if not hasattr(self, "_drag_data") or not self._drag_data or self._drag_data["type"] != "move":
            return

        # Compute how far we've moved
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Apply grid snapping if enabled
        if self.snap_to_grid:
            # Get current position
            item = self._drag_data["item"]
            x1, y1, x2, y2 = self.design_canvas.coords(item)

            # Calculate new position with grid snapping
            new_x1 = round((x1 + dx) / self.grid_size) * self.grid_size
            new_y1 = round((y1 + dy) / self.grid_size) * self.grid_size

            # Calculate adjusted dx, dy
            dx = new_x1 - x1
            dy = new_y1 - y1

        # Skip if no movement
        if dx == 0 and dy == 0:
            return

        # Move the widget
        item = self._drag_data["item"]
        self.design_canvas.move(item, dx, dy)

        # Move the associated text
        text_id = self.design_widgets[item]["text_id"]
        self.design_canvas.move(text_id, dx, dy)

        # Move the handles
        for handle_id in self.design_widgets[item]["handles"].values():
            self.design_canvas.move(handle_id, dx, dy)

        # Update drag data
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Update widget position
        x1, y1, x2, y2 = self.design_canvas.coords(item)
        self.design_widgets[item]["x"] = x1
        self.design_widgets[item]["y"] = y1

        # Update status bar with position
        self.status_label.config(text=f"Position: ({int(x1)}, {int(y1)}) Size: {int(x2-x1)}×{int(y2-y1)}")

    def on_widget_release(self, event):
        """Handle end of widget drag"""
        if hasattr(self, "_drag_data") and self._drag_data and self._drag_data["type"] == "move":
            # Generate code with updated position
            self.generate_code_from_design()

        self._drag_data = None

        # Update status bar
        self.status_label.config(text="Ready")

    def on_handle_press(self, event):
        """Handle resize handle press"""
        # Find the handle under cursor
        handle_id = self.design_canvas.find_withtag("current")[0]

        # Get the handle position (nw, ne, etc.)
        handle_tags = self.design_canvas.gettags(handle_id)
        handle_pos = None
        widget_id = None

        for tag in handle_tags:
            if tag.startswith("handle_"):
                if tag.startswith("handle_for_"):
                    widget_id = int(tag[11:])  # Extract widget ID
                else:
                    handle_pos = tag[7:]  # Extract handle position (nw, ne, etc.)

        if handle_pos and widget_id and widget_id in self.design_widgets:
            # Store resize data
            self._drag_data = {
                "x": event.x,
                "y": event.y,
                "handle": handle_id,
                "handle_pos": handle_pos,
                "item": widget_id,
                "type": "resize"
            }

            # Select the widget being resized
            self.select_design_widget(widget_id)

    def on_handle_drag(self, event):
        """Handle resize handle dragging"""
        if not hasattr(self, "_drag_data") or not self._drag_data or self._drag_data["type"] != "resize":
            return

        # Get widget and handle info
        widget_id = self._drag_data["item"]
        handle_pos = self._drag_data["handle_pos"]
        widget_info = self.design_widgets[widget_id]

        # Current widget coordinates
        x1, y1, x2, y2 = self.design_canvas.coords(widget_id)

        # Calculate new position based on handle
        new_x1, new_y1, new_x2, new_y2 = x1, y1, x2, y2

        # Compute mouse movement
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Update coordinates based on which handle is being dragged
        if handle_pos in ["nw", "w", "sw"]:
            new_x1 = x1 + dx
        if handle_pos in ["ne", "e", "se"]:
            new_x2 = x2 + dx
        if handle_pos in ["nw", "n", "ne"]:
            new_y1 = y1 + dy
        if handle_pos in ["sw", "s", "se"]:
            new_y2 = y2 + dy

        # Apply grid snapping if enabled
        if self.snap_to_grid:
            new_x1 = round(new_x1 / self.grid_size) * self.grid_size
            new_y1 = round(new_y1 / self.grid_size) * self.grid_size
            new_x2 = round(new_x2 / self.grid_size) * self.grid_size
            new_y2 = round(new_y2 / self.grid_size) * self.grid_size

        # Ensure minimum size
        if new_x2 - new_x1 < 30:
            if handle_pos in ["nw", "w", "sw"]:
                new_x1 = new_x2 - 30
            else:
                new_x2 = new_x1 + 30

        if new_y2 - new_y1 < 20:
            if handle_pos in ["nw", "n", "ne"]:
                new_y1 = new_y2 - 20
            else:
                new_y2 = new_y1 + 20

        # Update widget coordinates
        self.design_canvas.coords(widget_id, new_x1, new_y1, new_x2, new_y2)

        # Update text position
        self.design_canvas.coords(
            widget_info["text_id"],
            new_x1 + (new_x2 - new_x1) / 2,
            new_y1 + (new_y2 - new_y1) / 2
        )

        # Update handle positions
        handle_positions = {
            "nw": (new_x1, new_y1),
            "n": (new_x1 + (new_x2 - new_x1)/2, new_y1),
            "ne": (new_x2, new_y1),
            "e": (new_x2, new_y1 + (new_y2 - new_y1)/2),
            "se": (new_x2, new_y2),
            "s": (new_x1 + (new_x2 - new_x1)/2, new_y2),
            "sw": (new_x1, new_y2),
            "w": (new_x1, new_y1 + (new_y2 - new_y1)/2)
        }

        handle_size = 6
        for pos, (hx, hy) in handle_positions.items():
            if pos in widget_info["handles"]:
                handle_id = widget_info["handles"][pos]
                self.design_canvas.coords(
                    handle_id,
                    hx - handle_size/2, hy - handle_size/2,
                    hx + handle_size/2, hy + handle_size/2
                )

        # Update widget info
        if handle_pos in ["nw", "w", "sw"]:
            widget_info["x"] = new_x1
        if handle_pos in ["nw", "n", "ne"]:
            widget_info["y"] = new_y1
        widget_info["width"] = new_x2 - new_x1
        widget_info["height"] = new_y2 - new_y1

        # Update properties
        widget_info["properties"]["width"] = str(int(new_x2 - new_x1))
        widget_info["properties"]["height"] = str(int(new_y2 - new_y1))

        # Update properties panel if this widget is selected
        if self.selected_widget == widget_id:
            self.update_properties_panel()

        # Update status bar with size
        self.status_label.config(text=f"Position: ({int(new_x1)}, {int(new_y1)}) Size: {int(new_x2-new_x1)}×{int(new_y2-new_y1)}")

        # Update drag position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_handle_release(self, event):
        """Handle resize handle release"""
        if hasattr(self, "_drag_data") and self._drag_data and self._drag_data["type"] == "resize":
            # Generate code with updated size
            self.generate_code_from_design()

        self._drag_data = None

        # Update status bar
        self.status_label.config(text="Ready")

    def generate_code_from_design(self):
        """Generate Python code from the design"""
        if not self.design_widgets:
            messagebox.showinfo("Generate Code", "No widgets to generate code from.")
            return

        # Create a new code tab if needed
        self.view_code()
        current = self.editor_notebook.select()

        if not current:
            self.new_file()
            current = self.editor_notebook.select()

        tab = self.editor_notebook.nametowidget(current)

        # Generate code
        code = self.generate_tkinter_code()

        # Update the editor
        tab.editor.delete("1.0", tk.END)
        tab.editor.insert("1.0", code)

        # Mark as modified
        tab.modified = True
        idx = self.editor_notebook.index(current)
        self.editor_notebook.tab(idx, text=self.editor_notebook.tab(idx, "text") + " *")

        # Update status
        self.status_label.config(text="Generated code from design")

    def generate_tkinter_code(self):
        """Generate Tkinter code from the design"""
        code = [
            "import tkinter as tk",
            "from tkinter import ttk, messagebox",
            "",
            "class Application(tk.Tk):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.title(\"Windows Forms Style Application\")",
            "        self.geometry(\"800x600\")",
            "",
            "        # Configure the window",
            "        self.configure(background=\"#F0F0F0\")",
            "",
            "        # Create widgets",
            "        self.create_widgets()",
            "        self.create_events()",
            "",
            "    def create_widgets(self):"
        ]

        # Map Tkinter equivalents for Windows Forms controls
        winforms_mapping = {
            "Button": "Button",
            "Label": "Label",
            "LinkLabel": "Label",
            "Entry": "Entry",
            "TextBox": "Text",
            "Checkbutton": "Checkbutton",
            "Radiobutton": "Radiobutton",
            "GroupBox": "LabelFrame",
            "PictureBox": "Label",
            "Frame": "Frame",
            "Panel": "Frame",
            "TabControl": "ttk.Notebook",
            "SplitContainer": "PanedWindow",
            "MenuStrip": "Menu",
            "ToolStrip": "Frame",
            "StatusStrip": "Frame",
            "ContextMenuStrip": "Menu",
            "DataGridView": "ttk.Treeview",
            "Listbox": "Listbox",
            "ListView": "ttk.Treeview",
            "TreeView": "ttk.Treeview",
            "ComboBox": "ttk.Combobox"
        }

        # Add widget creation code
        for widget_id, widget_info in self.design_widgets.items():
            original_type = widget_info["type"]
            widget_name = widget_info["name"].lower()
            properties = widget_info["properties"]

            # Map to Tkinter equivalent
            widget_type = winforms_mapping.get(original_type, original_type)

            # Determine if this is a ttk widget
            ttk_widgets = ["Combobox", "Progressbar", "Treeview", "Notebook", "Separator"]
            if widget_type.startswith("ttk."):
                module = ""
            else:
                module = "ttk" if widget_type in ttk_widgets else "tk"

            # Format widget type with module
            full_type = widget_type if widget_type.startswith("ttk.") else f"{module}.{widget_type}"

            # Format properties
            props = []
            for prop, value in properties.items():
                # Skip some properties or format them differently
                if prop in ["background", "foreground", "font", "relief"]:
                    continue

                # Format string values
                if isinstance(value, str) and not value.isdigit() and not value.startswith("("):
                    props.append(f"{prop}=\"{value}\"")
                else:
                    props.append(f"{prop}={value}")

            # Add position
            x, y = int(widget_info["x"]), int(widget_info["y"])
            width, height = int(widget_info["width"]), int(widget_info["height"])

            # Generate the widget creation code
            code.append(f"        self.{widget_name} = {full_type}(self, {', '.join(props)})")
            code.append(f"        self.{widget_name}.place(x={x}, y={y}, width={width}, height={height})")

            # Add special configuration for certain widget types
            if original_type == "Button":
                code.append(f"        self.{widget_name}.configure(command=self.{widget_name}_click)")
            elif original_type == "MenuStrip":
                code.append(f"        self.config(menu=self.{widget_name})")
                code.append(f"        # Example menu items")
                code.append(f"        file_menu = tk.Menu(self.{widget_name}, tearoff=0)")
                code.append(f"        file_menu.add_command(label=\"New\", command=self.menu_new_click)")
                code.append(f"        file_menu.add_command(label=\"Open\", command=self.menu_open_click)")
                code.append(f"        file_menu.add_separator()")
                code.append(f"        file_menu.add_command(label=\"Exit\", command=self.destroy)")
                code.append(f"        self.{widget_name}.add_cascade(label=\"File\", menu=file_menu)")

            code.append("")

        # Add event handler functions
        code.append("    def create_events(self):")

        # Add event handlers for buttons
        button_widgets = [w for w in self.design_widgets.values() if w["type"] == "Button"]
        if button_widgets:
            for widget in button_widgets:
                widget_name = widget["name"].lower()
                code.append(f"        # Event handler for {widget_name}")
                code.append(f"    def {widget_name}_click(self):")
                code.append(f"        messagebox.showinfo(\"Button Click\", \"{widget_name} was clicked\")")
                code.append("")

        # Add default menu handlers
        code.append("    def menu_new_click(self):")
        code.append("        messagebox.showinfo(\"Menu\", \"New menu item clicked\")")
        code.append("")
        code.append("    def menu_open_click(self):")
        code.append("        messagebox.showinfo(\"Menu\", \"Open menu item clicked\")")
        code.append("")

        # Add main
        code.append("if __name__ == \"__main__\":")
        code.append("    app = Application()")
        code.append("    app.mainloop()")

        return "\n".join(code)

    def align_widgets(self, direction):
        """Align selected widgets"""
        if not self.selected_widget:
            messagebox.showinfo("Align Widgets", "No widget selected.")
            return

        selected = self.selected_widget
        widget_info = self.design_widgets[selected]

        if direction == "left":
            target_x = widget_info["x"]
            for widget_id in self.design_widgets:
                if widget_id != selected:
                    # Move to same x coordinate
                    w_info = self.design_widgets[widget_id]
                    dx = target_x - w_info["x"]
                    self.design_canvas.move(widget_id, dx, 0)
                    self.design_canvas.move(w_info["text_id"], dx, 0)
                    w_info["x"] = target_x

        elif direction == "right":
            target_x = widget_info["x"] + widget_info["width"]
            for widget_id in self.design_widgets:
                if widget_id != selected:
                    # Move right edge to same x coordinate
                    w_info = self.design_widgets[widget_id]
                    new_x = target_x - w_info["width"]
                    dx = new_x - w_info["x"]
                    self.design_canvas.move(widget_id, dx, 0)
                    self.design_canvas.move(w_info["text_id"], dx, 0)
                    w_info["x"] = new_x

        elif direction == "top":
            target_y = widget_info["y"]
            for widget_id in self.design_widgets:
                if widget_id != selected:
                    # Move to same y coordinate
                    w_info = self.design_widgets[widget_id]
                    dy = target_y - w_info["y"]
                    self.design_canvas.move(widget_id, 0, dy)
                    self.design_canvas.move(w_info["text_id"], 0, dy)
                    w_info["y"] = target_y

        elif direction == "bottom":
            target_y = widget_info["y"] + widget_info["height"]
            for widget_id in self.design_widgets:
                if widget_id != selected:
                    # Move bottom edge to same y coordinate
                    w_info = self.design_widgets[widget_id]
                    new_y = target_y - w_info["height"]
                    dy = new_y - w_info["y"]
                    self.design_canvas.move(widget_id, 0, dy)
                    self.design_canvas.move(w_info["text_id"], 0, dy)
                    w_info["y"] = new_y

    def make_same_size(self):
        """Make all widgets the same size as the selected widget"""
        if not self.selected_widget:
            messagebox.showinfo("Make Same Size", "No widget selected.")
            return

        selected = self.selected_widget
        widget_info = self.design_widgets[selected]
        target_width = widget_info["width"]
        target_height = widget_info["height"]

        for widget_id in self.design_widgets:
            if widget_id != selected:
                w_info = self.design_widgets[widget_id]

                # Save original position
                x, y = w_info["x"], w_info["y"]

                # Update size
                w_info["width"] = target_width
                w_info["height"] = target_height

                # Update canvas
                self.design_canvas.coords(
                    widget_id,
                    x, y, x + target_width, y + target_height
                )

                # Center the text
                self.design_canvas.coords(
                    w_info["text_id"],
                    x + (target_width / 2),
                    y + (target_height / 2)
                )

    def resize_form(self):
        """Resize the form container"""
        try:
            form_width = int(self.form_width_var.get())
            form_height = int(self.form_height_var.get())

            # Update form container
            self.design_canvas.coords(self.form_container, 10, 30, 10+form_width, 30+form_height)

            # Update titlebar
            self.design_canvas.coords(self.form_titlebar, 10, 10, 10+form_width, 30)

            # Redraw grid
            self.draw_grid_lines()

            # Update any widgets on the form
            for widget_id in self.design_widgets:
                widget_info = self.design_widgets[widget_id]
                if widget_info["x"] + widget_info["width"] > form_width or \
                   widget_info["y"] + widget_info["height"] > form_height:
                    # If widget is outside the form, move it inside
                    new_x = min(widget_info["x"], form_width - widget_info["width"])
                    new_y = min(widget_info["y"], form_height - widget_info["height"])

                    # Calculate movement
                    dx = new_x - widget_info["x"]
                    dy = new_y - widget_info["y"]

                    if dx != 0 or dy != 0:
                        # Move the widget
                        self.design_canvas.move(widget_id, dx, dy)
                        self.design_canvas.move(widget_info["text_id"], dx, dy)

                        # Update handle positions
                        for handle_id in widget_info["handles"].values():
                            self.design_canvas.move(handle_id, dx, dy)

                        # Update widget position
                        widget_info["x"] = new_x
                        widget_info["y"] = new_y

            # Generate updated code
            self.generate_code_from_design()

        except ValueError:
            messagebox.showerror("Error", "Form dimensions must be valid integers")

    def show_welcome_screen(self):
        """Show the welcome screen"""
        def welcome_callback(action, *args):
            if action == "new":
                self.new_file()
            elif action == "open":
                self.open_file()
            elif action == "recent" and args:
                path = args[0]
                if os.path.exists(path):
                    self.open_specific_file(path)
            elif action == "close" and args:
                self.show_welcome_on_startup = args[0]

        # Load preferences before showing welcome screen
        self.load_preferences()

        # Only show welcome screen if enabled and available
        if self.show_welcome_on_startup and WELCOME_AVAILABLE and WelcomeScreen:
            try:
                welcome = WelcomeScreen(self, welcome_callback)
            except Exception as e:
                print(f"Error showing welcome screen: {e}")
                self.new_file()
        else:
            # Create default file
            self.new_file()

# Run the application
if __name__ == "__main__":
    app = TkinterStudio()
    app.mainloop()
