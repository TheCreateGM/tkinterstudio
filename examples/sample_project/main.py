import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SampleProject:
    def __init__(self, root):
        self.root = root
        self.root.title("Sample Project")
        self.root.geometry("800x600")
        
        # Configure the grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create the menu bar
        self.create_menu()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Create tabs
        self.create_welcome_tab()
        self.create_calculator_tab()
        self.create_file_explorer_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
    def create_menu(self):
        # Main menu bar
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Copy", command=self.do_nothing)
        edit_menu.add_command(label="Paste", command=self.do_nothing)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_welcome_tab(self):
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        # Welcome message
        welcome_label = ttk.Label(
            welcome_frame, 
            text="Welcome to the Sample Project!",
            font=("Arial", 18)
        )
        welcome_label.pack(pady=30)
        
        description = ttk.Label(
            welcome_frame,
            text="This is a sample project demonstrating various Tkinter widgets and features.\n"
                 "Feel free to explore the different tabs to see what's available.",
            justify=tk.CENTER
        )
        description.pack(pady=10)
        
        # Add a nice image if available
        try:
            self.logo_img = tk.PhotoImage(file="logo.png")
            logo_label = ttk.Label(welcome_frame, image=self.logo_img)
            logo_label.pack(pady=20)
        except:
            fallback = ttk.Label(welcome_frame, text="[Image would be displayed here]", 
                               font=("Arial", 12), foreground="gray")
            fallback.pack(pady=20)
            
    def create_calculator_tab(self):
        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Calculator")
        
        # Calculator display
        self.calc_display = ttk.Entry(calc_frame, justify=tk.RIGHT, font=("Arial", 14))
        self.calc_display.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        
        # Calculator buttons
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        # Create and place buttons in grid
        row, col = 1, 0
        for button_text in buttons:
            btn = ttk.Button(
                calc_frame, 
                text=button_text,
                command=lambda t=button_text: self.calculator_button_click(t)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        # Clear button
        clear_btn = ttk.Button(calc_frame, text="Clear", command=self.calculator_clear)
        clear_btn.grid(row=row, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        for i in range(4):
            calc_frame.grid_columnconfigure(i, weight=1)
        for i in range(1, 6):
            calc_frame.grid_rowconfigure(i, weight=1)
            
    def create_file_explorer_tab(self):
        explorer_frame = ttk.Frame(self.notebook)
        self.notebook.add(explorer_frame, text="File Explorer")
        
        # Directory entry
        dir_frame = ttk.Frame(explorer_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT, padx=(0, 5))
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.dir_entry.insert(0, os.getcwd())
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT)
        
        # File list
        self.file_tree = ttk.Treeview(explorer_frame, columns=("size", "modified"), show="headings")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("modified", text="Modified")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(explorer_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_file_list)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        open_btn = ttk.Button(btn_frame, text="Open Selected", command=self.open_selected_file)
        open_btn.pack(side=tk.LEFT)
        
        # Initial file list
        self.refresh_file_list()
    
    def calculator_button_click(self, button_text):
        current = self.calc_display.get()
        
        if button_text == '=':
            try:
                result = eval(current)
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(tk.END, str(result))
                self.status_var.set(f"Calculation result: {result}")
            except Exception as e:
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(tk.END, "Error")
                self.status_var.set(f"Calculation error: {str(e)}")
        else:
            self.calc_display.delete(0, tk.END)
            self.calc_display.insert(tk.END, current + button_text)
    
    def calculator_clear(self):
        self.calc_display.delete(0, tk.END)
        self.status_var.set("Calculator cleared")
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.refresh_file_list()
    
    def refresh_file_list(self):
        directory = self.dir_entry.get()
        
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            # List directory contents
            for item in os.listdir(directory):
                path = os.path.join(directory, item)
                size = os.path.getsize(path)
                modified = os.path.getmtime(path)
                
                if os.path.isdir(path):
                    item = f"[{item}]"
                
                self.file_tree.insert("", tk.END, values=(item, f"{size} bytes", f"{modified}"))
            
            self.status_var.set(f"Loaded directory: {directory}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {e}")
            self.status_var.set("Error loading directory")
    
    def open_selected_file(self):
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            file_name = item['values'][0]
            # Remove brackets if it's a directory
            if file_name.startswith("[") and file_name.endswith("]"):
                file_name = file_name[1:-1]
                
            path = os.path.join(self.dir_entry.get(), file_name)
            
            if os.path.isfile(path):
                messagebox.showinfo("File Selected", f"Opening file: {path}")
                self.status_var.set(f"Selected file: {path}")
            elif os.path.isdir(path):
                self.dir_entry.delete(0, tk.END)
                self.dir_entry.insert(0, path)
                self.refresh_file_list()
    
    def open_file(self):
        file = filedialog.askopenfilename()
        if file:
            messagebox.showinfo("File Selected", f"You selected: {file}")
            self.status_var.set(f"Opened file: {file}")
    
    def save_file(self):
        file = filedialog.asksaveasfilename()
        if file:
            messagebox.showinfo("File Saved", f"File would be saved as: {file}")
            self.status_var.set(f"Saved file as: {file}")
    
    def show_about(self):
        messagebox.showinfo(
            "About", 
            "Sample Project v1.0\n\n"
            "This is a demonstration project for the Tkinter IDE.\n"
            "Created as an example of Python with Tkinter."
        )
    
    def do_nothing(self):
        self.status_var.set("This feature is not implemented in the sample")

if __name__ == "__main__":
    root = tk.Tk()
    app = SampleProject(root)
    root.mainloop()