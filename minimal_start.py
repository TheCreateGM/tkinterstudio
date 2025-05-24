#!/usr/bin/env python3
"""
Minimal startup script for TkinterStudio without welcome screen
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_minimal_ide():
    """Create a minimal IDE without complex dependencies"""

    class MinimalIDE(tk.Tk):
        def __init__(self):
            super().__init__()

            # Window setup
            self.title("TkinterStudio - Minimal Mode")
            self.geometry("1000x700")
            self.minsize(800, 600)

            # Configure grid
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)

            # Create UI
            self.create_menu()
            self.create_toolbar()
            self.create_main_area()
            self.create_status_bar()

            # Create default file
            self.new_file()

        def create_menu(self):
            """Create menu bar"""
            menubar = tk.Menu(self)

            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="New", command=self.new_file)
            file_menu.add_command(label="Open", command=self.open_file)
            file_menu.add_command(label="Save", command=self.save_file)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.quit)
            menubar.add_cascade(label="File", menu=file_menu)

            # Edit menu
            edit_menu = tk.Menu(menubar, tearoff=0)
            edit_menu.add_command(label="Cut", command=self.cut)
            edit_menu.add_command(label="Copy", command=self.copy)
            edit_menu.add_command(label="Paste", command=self.paste)
            menubar.add_cascade(label="Edit", menu=edit_menu)

            # View menu
            view_menu = tk.Menu(menubar, tearoff=0)
            view_menu.add_command(label="Design Mode", command=self.toggle_design_mode)
            menubar.add_cascade(label="View", menu=view_menu)

            # Build menu
            build_menu = tk.Menu(menubar, tearoff=0)
            build_menu.add_command(label="Run", command=self.run_code)
            menubar.add_cascade(label="Build", menu=build_menu)

            self.config(menu=menubar)

        def create_toolbar(self):
            """Create toolbar"""
            self.toolbar = tk.Frame(self, relief=tk.RAISED, bg='#E6E6E6')
            self.toolbar.grid(row=0, column=0, sticky="ew")

            # Toolbar buttons
            tk.Button(self.toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2, pady=2)
            tk.Button(self.toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2, pady=2)
            tk.Button(self.toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2, pady=2)
            tk.Frame(self.toolbar, width=2, bg='#CCCCCC').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
            tk.Button(self.toolbar, text="Run", command=self.run_code, bg='#0078D7', fg='white').pack(side=tk.LEFT, padx=2, pady=2)

        def create_main_area(self):
            """Create main work area"""
            # Main paned window
            self.main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
            self.main_pane.grid(row=1, column=0, sticky="nsew")

            # Left panel (toolbox/explorer)
            self.left_frame = tk.Frame(self.main_pane, bg='#F0F0F0', width=200)
            self.create_toolbox()

            # Right panel (editor and output)
            self.right_frame = tk.Frame(self.main_pane)
            self.vertical_pane = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL)
            self.vertical_pane.pack(fill=tk.BOTH, expand=True)

            # Editor area
            self.editor_frame = tk.Frame(self.vertical_pane)
            self.create_editor()

            # Output area
            self.output_frame = tk.LabelFrame(self.vertical_pane, text="Output")
            self.output_text = tk.Text(self.output_frame, height=8, wrap=tk.WORD)
            self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Add to paned windows
            self.vertical_pane.add(self.editor_frame, weight=3)
            self.vertical_pane.add(self.output_frame, weight=1)

            self.main_pane.add(self.left_frame, weight=0)
            self.main_pane.add(self.right_frame, weight=1)

        def create_toolbox(self):
            """Create toolbox"""
            toolbox_label = tk.Label(self.left_frame, text="Toolbox", bg='#F0F0F0', font=('Arial', 12, 'bold'))
            toolbox_label.pack(fill=tk.X, padx=5, pady=5)

            # Widget categories
            categories = {
                "Common Controls": ["Button", "Label", "Entry", "Text"],
                "Containers": ["Frame", "LabelFrame"],
                "Data": ["Listbox", "Treeview"]
            }

            for category, widgets in categories.items():
                # Category header
                cat_frame = tk.Frame(self.left_frame, bg='#E0E0E0')
                cat_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(cat_frame, text=category, bg='#E0E0E0', font=('Arial', 10, 'bold')).pack(anchor='w', padx=5)

                # Widgets
                for widget in widgets:
                    btn = tk.Button(self.left_frame, text=widget, command=lambda w=widget: self.add_widget(w))
                    btn.pack(fill=tk.X, padx=10, pady=1)

        def create_editor(self):
            """Create code editor"""
            self.editor_notebook = ttk.Notebook(self.editor_frame)
            self.editor_notebook.pack(fill=tk.BOTH, expand=True)

        def create_status_bar(self):
            """Create status bar"""
            self.status_bar = tk.Frame(self, relief=tk.SUNKEN, bg='#CCCCCC')
            self.status_bar.grid(row=2, column=0, sticky="ew")

            self.status_label = tk.Label(self.status_bar, text="Ready", bg='#CCCCCC')
            self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

        def new_file(self):
            """Create new file"""
            editor_frame = tk.Frame(self.editor_notebook)
            editor = tk.Text(editor_frame, wrap=tk.NONE, undo=True, font=('Courier', 10))

            # Add scrollbars
            v_scroll = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=editor.yview)
            h_scroll = tk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=editor.xview)
            editor.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

            # Layout
            editor.grid(row=0, column=0, sticky="nsew")
            v_scroll.grid(row=0, column=1, sticky="ns")
            h_scroll.grid(row=1, column=0, sticky="ew")

            editor_frame.grid_rowconfigure(0, weight=1)
            editor_frame.grid_columnconfigure(0, weight=1)

            # Add to notebook
            self.editor_notebook.add(editor_frame, text="Untitled")
            self.editor_notebook.select(self.editor_notebook.index(tk.END) - 1)

            # Store reference
            editor_frame.editor = editor

        def open_file(self):
            """Open file"""
            from tkinter import filedialog
            filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
            if filename:
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    self.new_file()
                    current_tab = self.editor_notebook.nametowidget(self.editor_notebook.select())
                    current_tab.editor.insert("1.0", content)
                    self.editor_notebook.tab(self.editor_notebook.select(), text=os.path.basename(filename))
                    self.status_label.config(text=f"Opened {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")

        def save_file(self):
            """Save file"""
            from tkinter import filedialog
            current = self.editor_notebook.select()
            if not current:
                return

            filename = filedialog.asksaveasfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
            if filename:
                try:
                    current_tab = self.editor_notebook.nametowidget(current)
                    content = current_tab.editor.get("1.0", tk.END)
                    with open(filename, 'w') as f:
                        f.write(content)
                    self.editor_notebook.tab(current, text=os.path.basename(filename))
                    self.status_label.config(text=f"Saved {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {e}")

        def run_code(self):
            """Run current code"""
            current = self.editor_notebook.select()
            if not current:
                return

            current_tab = self.editor_notebook.nametowidget(current)
            code = current_tab.editor.get("1.0", tk.END)

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Running code...\n\n")

            try:
                # Redirect stdout to capture print statements
                import io
                import contextlib

                output_buffer = io.StringIO()
                with contextlib.redirect_stdout(output_buffer):
                    exec(code)

                output = output_buffer.getvalue()
                if output:
                    self.output_text.insert(tk.END, output)
                else:
                    self.output_text.insert(tk.END, "Code executed successfully (no output)")

            except Exception as e:
                self.output_text.insert(tk.END, f"Error: {str(e)}")

        def cut(self):
            """Cut text"""
            try:
                self.focus_get().event_generate("<<Cut>>")
            except:
                pass

        def copy(self):
            """Copy text"""
            try:
                self.focus_get().event_generate("<<Copy>>")
            except:
                pass

        def paste(self):
            """Paste text"""
            try:
                self.focus_get().event_generate("<<Paste>>")
            except:
                pass

        def add_widget(self, widget_name):
            """Add widget code to editor"""
            widget_code = {
                "Button": "button = tk.Button(root, text='Button')\nbutton.pack()",
                "Label": "label = tk.Label(root, text='Label')\nlabel.pack()",
                "Entry": "entry = tk.Entry(root)\nentry.pack()",
                "Text": "text = tk.Text(root)\ntext.pack()",
                "Frame": "frame = tk.Frame(root)\nframe.pack()",
                "LabelFrame": "labelframe = tk.LabelFrame(root, text='LabelFrame')\nlabelframe.pack()",
                "Listbox": "listbox = tk.Listbox(root)\nlistbox.pack()",
                "Treeview": "treeview = ttk.Treeview(root)\ntreeview.pack()"
            }

            code = widget_code.get(widget_name, f"# {widget_name} widget")

            current = self.editor_notebook.select()
            if current:
                current_tab = self.editor_notebook.nametowidget(current)
                current_tab.editor.insert(tk.INSERT, code + "\n")

        def toggle_design_mode(self):
            """Toggle design mode"""
            messagebox.showinfo("Design Mode", "Design mode toggle - feature coming soon!")

    return MinimalIDE

def main():
    """Main function"""
    try:
        # Create and run minimal IDE
        MinimalIDE = create_minimal_ide()
        app = MinimalIDE()
        app.mainloop()

    except Exception as e:
        # Fallback error handling
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start TkinterStudio: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
