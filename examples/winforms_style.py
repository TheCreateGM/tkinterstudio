import tkinter as tk
from tkinter import ttk, messagebox

class WindowsFormsStyleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows Forms Style Application")
        self.geometry("800x600")
        
        # Configure the window
        self.configure(background="#F0F0F0")
        
        # Create widgets
        self.create_widgets()
        self.create_events()
        
    def create_widgets(self):
        # Main menu
        self.menustrip = tk.Menu(self)
        self.config(menu=self.menustrip)
        
        # File menu
        file_menu = tk.Menu(self.menustrip, tearoff=0)
        file_menu.add_command(label="New", command=self.menu_new_click)
        file_menu.add_command(label="Open", command=self.menu_open_click)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        self.menustrip.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(self.menustrip, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.focus_get().event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.focus_get().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.focus_get().event_generate("<<Paste>>"))
        self.menustrip.add_cascade(label="Edit", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menustrip, tearoff=0)
        help_menu.add_command(label="About", command=self.menu_about_click)
        self.menustrip.add_cascade(label="Help", menu=help_menu)
        
        # Toolbar
        self.toolstrip = tk.Frame(self, bg="#E6E6E6", height=30)
        self.toolstrip.pack(fill=tk.X)
        
        # Toolbar buttons
        self.new_button = ttk.Button(self.toolstrip, text="New", command=self.menu_new_click)
        self.new_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.open_button = ttk.Button(self.toolstrip, text="Open", command=self.menu_open_click)
        self.open_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Form content
        self.main_panel = ttk.Frame(self)
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (like a GroupBox)
        self.left_panel = ttk.LabelFrame(self.main_panel, text="Input Form")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create form fields
        self.create_form_fields()
        
        # Right panel (like a GroupBox)
        self.right_panel = ttk.LabelFrame(self.main_panel, text="Data Preview")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create DataGridView equivalent
        self.create_data_grid()
        
        # Status strip
        self.statusstrip = ttk.Frame(self, relief=tk.SUNKEN)
        self.statusstrip.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(self.statusstrip, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=3)
        
    def create_form_fields(self):
        # Name field
        ttk.Label(self.left_panel, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_textbox = ttk.Entry(self.left_panel, width=30)
        self.name_textbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Email field
        ttk.Label(self.left_panel, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_textbox = ttk.Entry(self.left_panel, width=30)
        self.email_textbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Age field
        ttk.Label(self.left_panel, text="Age:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.age_numericupdown = ttk.Spinbox(self.left_panel, from_=1, to=120, width=5)
        self.age_numericupdown.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.age_numericupdown.set(25)
        
        # Gender field
        ttk.Label(self.left_panel, text="Gender:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.gender_combobox = ttk.Combobox(self.left_panel, values=["Male", "Female", "Other"], width=10)
        self.gender_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.gender_combobox.current(0)
        
        # Active field
        self.active_checkbox = ttk.Checkbutton(self.left_panel, text="Active User")
        self.active_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Notes field
        ttk.Label(self.left_panel, text="Notes:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        self.notes_textbox = tk.Text(self.left_panel, width=30, height=5)
        self.notes_textbox.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Button panel
        self.button_panel = ttk.Frame(self.left_panel)
        self.button_panel.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # Add button
        self.add_button = ttk.Button(self.button_panel, text="Add", command=self.add_button_click)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(self.button_panel, text="Clear", command=self.clear_button_click)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
    def create_data_grid(self):
        # Create treeview (DataGridView equivalent)
        columns = ("name", "email", "age", "gender")
        self.datagridview = ttk.Treeview(self.right_panel, columns=columns, show="headings")
        
        # Define headings
        self.datagridview.heading("name", text="Name")
        self.datagridview.heading("email", text="Email")
        self.datagridview.heading("age", text="Age")
        self.datagridview.heading("gender", text="Gender")
        
        # Define columns
        self.datagridview.column("name", width=100)
        self.datagridview.column("email", width=150)
        self.datagridview.column("age", width=50)
        self.datagridview.column("gender", width=80)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(self.right_panel, orient=tk.VERTICAL, command=self.datagridview.yview)
        scrollbar_x = ttk.Scrollbar(self.right_panel, orient=tk.HORIZONTAL, command=self.datagridview.xview)
        self.datagridview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack everything
        self.datagridview.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu for DataGridView
        self.grid_context_menu = tk.Menu(self.datagridview, tearoff=0)
        self.grid_context_menu.add_command(label="Delete", command=self.delete_selected_row)
        self.grid_context_menu.add_command(label="View Details", command=self.view_row_details)
        
        # Bind right-click on DataGridView
        self.datagridview.bind("<Button-3>", self.show_context_menu)
        
    def create_events(self):
        # Menu event handlers
        pass
        
    def menu_new_click(self):
        self.clear_form()
        messagebox.showinfo("New", "Form cleared for new entry")
        self.status_label.config(text="New form ready")
        
    def menu_open_click(self):
        messagebox.showinfo("Open", "Open dialog would appear here")
        self.status_label.config(text="Open command executed")
        
    def menu_about_click(self):
        messagebox.showinfo("About", "Windows Forms Style Demo\nCreated with PyIDE")
        
    def add_button_click(self):
        # Validate form
        if not self.name_textbox.get() or not self.email_textbox.get():
            messagebox.showerror("Error", "Name and Email are required fields")
            return
            
        # Get form values
        name = self.name_textbox.get()
        email = self.email_textbox.get()
        age = self.age_numericupdown.get()
        gender = self.gender_combobox.get()
        
        # Add to DataGridView
        self.datagridview.insert("", tk.END, values=(name, email, age, gender))
        
        # Clear form
        self.clear_form()
        
        # Update status
        self.status_label.config(text=f"Added new record: {name}")
        
    def clear_button_click(self):
        self.clear_form()
        
    def clear_form(self):
        # Clear all form fields
        self.name_textbox.delete(0, tk.END)
        self.email_textbox.delete(0, tk.END)
        self.age_numericupdown.set(25)
        self.gender_combobox.current(0)
        self.notes_textbox.delete("1.0", tk.END)
        
    def show_context_menu(self, event):
        # Show context menu on right-click
        try:
            row_id = self.datagridview.identify_row(event.y)
            if row_id:
                # Select the row under cursor
                self.datagridview.selection_set(row_id)
                # Display the context menu
                self.grid_context_menu.post(event.x_root, event.y_root)
        except:
            pass
            
    def delete_selected_row(self):
        # Delete the selected row
        selected = self.datagridview.selection()
        if selected:
            name = self.datagridview.item(selected[0], "values")[0]
            self.datagridview.delete(selected[0])
            self.status_label.config(text=f"Deleted record: {name}")
        
    def view_row_details(self):
        # Show details of the selected row
        selected = self.datagridview.selection()
        if selected:
            values = self.datagridview.item(selected[0], "values")
            detail_text = f"Name: {values[0]}\nEmail: {values[1]}\nAge: {values[2]}\nGender: {values[3]}"
            messagebox.showinfo("Row Details", detail_text)

if __name__ == "__main__":
    app = WindowsFormsStyleApp()
    app.mainloop()
