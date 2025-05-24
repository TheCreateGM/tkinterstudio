import tkinter as tk
from tkinter import ttk, font
import os
import sys

class WelcomeScreen(tk.Toplevel):
    """Modern welcome screen for TkinterStudio"""

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Welcome to TkinterStudio")
        self.parent = parent
        self.callback = callback

        # Window configuration
        self.minsize(800, 500)
        self.configure(background="#FFFFFF")
        self.attributes("-topmost", True)

        # Center on screen
        width = 900
        height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Create the UI
        self.create_widgets()

        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Create welcome screen widgets"""
        # Main paned window for layout
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Left panel (blue sidebar)
        left_panel = ttk.Frame(main_pane, style="LeftPanel.TFrame")
        left_panel.configure(width=250)

        # Right panel (content)
        right_panel = ttk.Frame(main_pane, style="RightPanel.TFrame")

        # Add panels to paned window
        main_pane.add(left_panel, weight=0)
        main_pane.add(right_panel, weight=1)

        # Configure styles
        try:
            style = ttk.Style()
            style.configure("LeftPanel.TFrame", background="#0078D7")
            style.configure("RightPanel.TFrame", background="#FFFFFF")
            style.configure("Title.TLabel",
                          background="#0078D7",
                          foreground="#FFFFFF",
                          font=("Arial", 20, "bold"))
            style.configure("Subtitle.TLabel",
                          background="#0078D7",
                          foreground="#FFFFFF",
                          font=("Arial", 12))
            style.configure("Header.TLabel",
                          background="#FFFFFF",
                          foreground="#0078D7",
                          font=("Arial", 16, "bold"))
            style.configure("Link.TLabel",
                          background="#FFFFFF",
                          foreground="#0078D7",
                          font=("Arial", 11, "underline"))
            style.configure("Content.TLabel",
                          background="#FFFFFF",
                          foreground="#333333",
                          font=("Arial", 10))
            style.configure("TButton", padding=5)
            style.configure("Action.TButton",
                          background="#0078D7",
                          foreground="#FFFFFF",
                          padding=10,
                          font=("Arial", 10, "bold"))
        except Exception as e:
            print(f"Error configuring styles: {e}")

        # Left panel content
        ttk.Label(left_panel, text="TkinterStudio", style="Title.TLabel").pack(
            anchor=tk.NW, padx=20, pady=(30, 5))
        ttk.Label(left_panel, text="Visual Studio 2010 Style", style="Subtitle.TLabel").pack(
            anchor=tk.NW, padx=20, pady=(0, 30))

        # Version information
        version_frame = ttk.Frame(left_panel)
        version_frame.configure(style="LeftPanel.TFrame")
        version_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        ttk.Label(version_frame, text="Version 1.0",
                 foreground="#FFFFFF", background="#0078D7",
                 font=("Arial", 9)).pack(anchor=tk.W)
        ttk.Label(version_frame, text="© 2025 TkinterStudio",
                 foreground="#FFFFFF", background="#0078D7",
                 font=("Arial", 9)).pack(anchor=tk.W)

        # Right panel content
        content_frame = ttk.Frame(right_panel, style="RightPanel.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Welcome header
        ttk.Label(content_frame, text="Welcome to TkinterStudio", style="Header.TLabel").pack(
            anchor=tk.NW, pady=(0, 20))

        # Start options frame
        start_frame = ttk.LabelFrame(content_frame, text="Start", padding=15)
        start_frame.pack(fill=tk.X, pady=(0, 20))

        # Create new project button
        new_project_button = ttk.Button(
            start_frame, text="Create New Project",
            command=lambda: self.callback("new"),
            style="Action.TButton",
            width=25
        )
        new_project_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Open project button
        open_project_button = ttk.Button(
            start_frame, text="Open Project or File",
            command=lambda: self.callback("open"),
            width=25
        )
        open_project_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # Clone repository button
        clone_button = ttk.Button(
            start_frame, text="Clone Repository",
            command=lambda: self.callback("clone"),
            width=25
        )
        clone_button.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # Descriptions
        ttk.Label(start_frame, text="Start a new project from scratch",
                 style="Content.TLabel").grid(row=0, column=1, padx=10, sticky=tk.W)
        ttk.Label(start_frame, text="Open an existing project or file",
                 style="Content.TLabel").grid(row=1, column=1, padx=10, sticky=tk.W)
        ttk.Label(start_frame, text="Clone a project from a repository",
                 style="Content.TLabel").grid(row=2, column=1, padx=10, sticky=tk.W)

        # Configure grid
        start_frame.grid_columnconfigure(1, weight=1)

        # Recent projects frame
        recent_frame = ttk.LabelFrame(content_frame, text="Recent", padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Sample projects (these would be populated from actual recent projects)
        sample_projects = [
            ("Windows Forms Example", "examples/winforms_style.py"),
            ("Toolbox Demo", "examples/toolbox_demo.py"),
            ("Hello World", "examples/hello_world.py")
        ]

        # Create recent project links
        for i, (name, path) in enumerate(sample_projects):
            project_frame = ttk.Frame(recent_frame, style="RightPanel.TFrame")
            project_frame.pack(fill=tk.X, pady=3)

            project_link = ttk.Label(
                project_frame, text=name, style="Link.TLabel",
                cursor="hand2"
            )
            project_link.pack(side=tk.LEFT)
            project_link.bind("<Button-1>", lambda e, p=path: self.callback("recent", p))

            ttk.Label(
                project_frame, text=path, style="Content.TLabel"
            ).pack(side=tk.LEFT, padx=10)

        # Get started frame
        help_frame = ttk.LabelFrame(content_frame, text="Help & Resources", padding=15)
        help_frame.pack(fill=tk.X, pady=(0, 20))

        # Help links
        help_items = [
            ("Documentation", "View the documentation"),
            ("Video Tutorials", "Watch tutorials to get started"),
            ("Sample Projects", "Explore sample projects")
        ]

        for i, (title, desc) in enumerate(help_items):
            help_link = ttk.Label(
                help_frame, text=title, style="Link.TLabel",
                cursor="hand2"
            )
            help_link.grid(row=i, column=0, padx=10, pady=3, sticky=tk.W)
            help_link.bind("<Button-1>", lambda e, t=title: self.callback("help", t))

            ttk.Label(
                help_frame, text=desc, style="Content.TLabel"
            ).grid(row=i, column=1, padx=10, pady=3, sticky=tk.W)

        # Configure grid
        help_frame.grid_columnconfigure(1, weight=1)

        # Startup options
        startup_frame = ttk.Frame(content_frame, style="RightPanel.TFrame")
        startup_frame.pack(fill=tk.X, pady=(10, 0))

        self.show_welcome_var = tk.BooleanVar(value=True)
        show_welcome_check = ttk.Checkbutton(
            startup_frame,
            text="Show welcome screen at startup",
            variable=self.show_welcome_var,
            style="Content.TCheckbutton"
        )
        show_welcome_check.pack(side=tk.LEFT)

    def on_close(self):
        """Handle window close"""
        # Save startup preferences
        self.callback("close", self.show_welcome_var.get())
        self.destroy()

def test_welcome_screen():
    """Test function to demonstrate the welcome screen"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    def callback(action, *args):
        print(f"Action: {action}, Args: {args}")
        if action == "close":
            root.quit()

    welcome = WelcomeScreen(root, callback)
    root.mainloop()

if __name__ == "__main__":
    test_welcome_screen()
