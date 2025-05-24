#!/usr/bin/env python3
"""
Robust launcher for TkinterStudio that handles all potential errors gracefully
and provides fallbacks for missing dependencies or modules.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback

class RobustLauncher:
    """Robust launcher that tries different startup methods"""

    def __init__(self):
        self.root = None
        self.error_log = []

    def log_error(self, error_msg):
        """Log error messages"""
        self.error_log.append(error_msg)
        print(f"ERROR: {error_msg}")

    def try_full_ide(self):
        """Try to launch the full TkinterStudio application"""
        try:
            # Add current directory to Python path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            # Try importing and running the main IDE
            from main import TkinterStudio

            print("Starting full TkinterStudio...")
            app = TkinterStudio()
            app.mainloop()
            return True

        except Exception as e:
            self.log_error(f"Full IDE startup failed: {str(e)}")
            return False

    def try_minimal_ide(self):
        """Try to launch a minimal IDE version"""
        try:
            from minimal_start import create_minimal_ide

            print("Starting minimal TkinterStudio...")
            MinimalIDE = create_minimal_ide()
            app = MinimalIDE()
            app.mainloop()
            return True

        except Exception as e:
            self.log_error(f"Minimal IDE startup failed: {str(e)}")
            return False

    def create_fallback_ide(self):
        """Create a basic fallback IDE"""
        try:
            print("Creating fallback IDE...")

            class FallbackIDE(tk.Tk):
                def __init__(self):
                    super().__init__()
                    self.title("TkinterStudio - Fallback Mode")
                    self.geometry("800x600")

                    # Create menu
                    menubar = tk.Menu(self)
                    file_menu = tk.Menu(menubar, tearoff=0)
                    file_menu.add_command(label="New", command=self.new_file)
                    file_menu.add_command(label="Open", command=self.open_file)
                    file_menu.add_command(label="Save", command=self.save_file)
                    file_menu.add_separator()
                    file_menu.add_command(label="Exit", command=self.quit)
                    menubar.add_cascade(label="File", menu=file_menu)

                    build_menu = tk.Menu(menubar, tearoff=0)
                    build_menu.add_command(label="Run", command=self.run_code)
                    menubar.add_cascade(label="Build", menu=build_menu)

                    self.config(menu=menubar)

                    # Create main frame
                    main_frame = tk.Frame(self)
                    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                    # Create editor
                    self.editor = tk.Text(main_frame, wrap=tk.NONE, undo=True)

                    # Add scrollbars
                    v_scroll = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.editor.yview)
                    h_scroll = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.editor.xview)
                    self.editor.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

                    # Layout
                    self.editor.grid(row=0, column=0, sticky="nsew")
                    v_scroll.grid(row=0, column=1, sticky="ns")
                    h_scroll.grid(row=1, column=0, sticky="ew")

                    main_frame.grid_rowconfigure(0, weight=1)
                    main_frame.grid_columnconfigure(0, weight=1)

                    # Status bar
                    self.status = tk.Label(self, text="Ready - Fallback Mode", relief=tk.SUNKEN, anchor=tk.W)
                    self.status.pack(side=tk.BOTTOM, fill=tk.X)

                    # Add some default content
                    self.editor.insert("1.0", """# TkinterStudio - Fallback Mode
# Basic Python editor with syntax highlighting disabled

import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Hello World")

    label = tk.Label(root, text="Hello, World!")
    label.pack(padx=20, pady=20)

    button = tk.Button(root, text="Click Me!", command=lambda: print("Button clicked!"))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
""")

                    self.current_file = None

                def new_file(self):
                    self.editor.delete("1.0", tk.END)
                    self.current_file = None
                    self.status.config(text="New file created")

                def open_file(self):
                    try:
                        filename = filedialog.askopenfilename(
                            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
                        )
                        if filename:
                            with open(filename, 'r') as f:
                                content = f.read()
                            self.editor.delete("1.0", tk.END)
                            self.editor.insert("1.0", content)
                            self.current_file = filename
                            self.status.config(text=f"Opened: {filename}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open file: {e}")

                def save_file(self):
                    try:
                        if self.current_file:
                            filename = self.current_file
                        else:
                            filename = filedialog.asksaveasfilename(
                                defaultextension=".py",
                                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
                            )

                        if filename:
                            content = self.editor.get("1.0", tk.END)
                            with open(filename, 'w') as f:
                                f.write(content)
                            self.current_file = filename
                            self.status.config(text=f"Saved: {filename}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not save file: {e}")

                def run_code(self):
                    try:
                        code = self.editor.get("1.0", tk.END)

                        # Create a new window for output
                        output_window = tk.Toplevel(self)
                        output_window.title("Output")
                        output_window.geometry("600x400")

                        output_text = tk.Text(output_window, wrap=tk.WORD)
                        output_scroll = tk.Scrollbar(output_window, command=output_text.yview)
                        output_text.config(yscrollcommand=output_scroll.set)

                        output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

                        # Redirect stdout
                        import io
                        import contextlib

                        output_buffer = io.StringIO()

                        try:
                            with contextlib.redirect_stdout(output_buffer):
                                exec(code)

                            output = output_buffer.getvalue()
                            if output:
                                output_text.insert("1.0", output)
                            else:
                                output_text.insert("1.0", "Code executed successfully (no output)")

                        except Exception as e:
                            output_text.insert("1.0", f"Error executing code:\n{str(e)}\n\n{traceback.format_exc()}")

                        self.status.config(text="Code executed")

                    except Exception as e:
                        messagebox.showerror("Error", f"Could not execute code: {e}")

            app = FallbackIDE()
            app.mainloop()
            return True

        except Exception as e:
            self.log_error(f"Fallback IDE creation failed: {str(e)}")
            return False

    def show_error_dialog(self):
        """Show error dialog with all logged errors"""
        try:
            root = tk.Tk()
            root.withdraw()

            error_msg = "TkinterStudio failed to start. Error details:\n\n"
            error_msg += "\n".join(self.error_log)
            error_msg += "\n\nPlease check that all dependencies are installed:\n"
            error_msg += "- Python 3.x\n"
            error_msg += "- tkinter (usually included with Python)\n"
            error_msg += "\nTry running: pip install -r requirements.txt"

            messagebox.showerror("TkinterStudio Startup Error", error_msg)
            root.destroy()

        except Exception as e:
            print(f"Could not show error dialog: {e}")
            print("Logged errors:")
            for error in self.error_log:
                print(f"  - {error}")

    def launch(self):
        """Try to launch TkinterStudio using different methods"""
        print("TkinterStudio Robust Launcher")
        print("=" * 50)

        # Method 1: Try full IDE
        if self.try_full_ide():
            return

        print("\nFull IDE failed, trying minimal IDE...")

        # Method 2: Try minimal IDE
        if self.try_minimal_ide():
            return

        print("\nMinimal IDE failed, trying fallback IDE...")

        # Method 3: Try fallback IDE
        if self.create_fallback_ide():
            return

        print("\nAll startup methods failed.")

        # Method 4: Show error dialog
        self.show_error_dialog()

def main():
    """Main entry point"""
    launcher = RobustLauncher()
    launcher.launch()

if __name__ == "__main__":
    main()
