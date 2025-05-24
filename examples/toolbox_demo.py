#!/usr/bin/env python3
"""
Toolbox and Form Designer Demonstration

This file demonstrates a Tkinter application that could be created using
the Visual Studio 2010-style Toolbox and Form Designer in PyIDE.

The layout and widget placement shown here can be created by dragging
widgets from the Toolbox onto the Form Designer, adjusting their properties,
and then generating code.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random

class ToolboxDemoApp:
    """Application demonstrating widgets that can be added from the Toolbox"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PyIDE Toolbox Demo")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure the window
        self.root.configure(background="#EFEFF2")
        
        # Create form components
        self.create_widgets()
        
    def create_widgets(self):
        """Create all the widgets that would be dragged from the Toolbox"""
        
        # Frame for form header (drag a Frame from Toolbox)
        self.header_frame = tk.Frame(self.root, bg="#3C78D8", height=60)
        self.header_frame.pack(fill=tk.X)
        
        # Title label (drag a Label from Toolbox)
        self.title_label = tk.Label(
            self.header_frame, 
            text="Form Designer Demo",
            font=("Arial", 16, "bold"),
            bg="#3C78D8",
            fg="white"
        )
        self.title_label.pack(pady=15)
        
        # Main content frame (drag a Frame from Toolbox)
        self.main_frame = tk.Frame(self.root, bg="#EFEFF2")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel (drag a LabelFrame from Toolbox)
        self.left_panel = ttk.LabelFrame(self.main_frame, text="Controls Demo")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel (drag a LabelFrame from Toolbox)
        self.right_panel = ttk.LabelFrame(self.main_frame, text="Output")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create controls on left panel
        self.create_controls()
        
        # Create output area on right panel
        self.create_output_area()
        
        # Status bar (drag a Label from Toolbox)
        self.status_bar = tk.Label(
            self.root, 
            text="Ready", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_controls(self):
        """Create control widgets in the left panel"""
        
        # Name label (drag a Label from Toolbox)
        self.name_label = ttk.Label(self.left_panel, text="Name:")
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Name entry (drag an Entry from Toolbox)
        self.name_entry = ttk.Entry(self.left_panel, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Age label (drag a Label from Toolbox)
        self.age_label = ttk.Label(self.left_panel, text="Age:")
        self.age_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Age spinbox (drag a Spinbox from Toolbox)
        self.age_spin = ttk.Spinbox(self.left_panel, from_=1, to=120, width=5)
        self.age_spin.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.age_spin.set(25)
        
        # Gender label (drag a Label from Toolbox)
        self.gender_label = ttk.Label(self.left_panel, text="Gender:")
        self.gender_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Gender frame (drag a Frame from Toolbox)
        self.gender_frame = ttk.Frame(self.left_panel)
        self.gender_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Gender radio buttons (drag Radiobuttons from Toolbox)
        self.gender_var = tk.StringVar(value="Male")
        self.male_radio = ttk.Radiobutton(
            self.gender_frame, 
            text="Male", 
            variable=self.gender_var, 
            value="Male"
        )
        self.male_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        self.female_radio = ttk.Radiobutton(
            self.gender_frame, 
            text="Female", 
            variable=self.gender_var, 
            value="Female"
        )
        self.female_radio.pack(side=tk.LEFT)
        
        # Country label (drag a Label from Toolbox)
        self.country_label = ttk.Label(self.left_panel, text="Country:")
        self.country_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Country combobox (drag a Combobox from Toolbox)
        self.country_combo = ttk.Combobox(
            self.left_panel, 
            values=["USA", "Canada", "UK", "Australia", "Germany", "France", "Japan"]
        )
        self.country_combo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.country_combo.current(0)
        
        # Subscribe checkbox (drag a Checkbutton from Toolbox)
        self.subscribe_var = tk.BooleanVar(value=True)
        self.subscribe_check = ttk.Checkbutton(
            self.left_panel, 
            text="Subscribe to newsletter", 
            variable=self.subscribe_var
        )
        self.subscribe_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Notes label (drag a Label from Toolbox)
        self.notes_label = ttk.Label(self.left_panel, text="Notes:")
        self.notes_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        
        # Notes text (drag a Text from Toolbox)
        self.notes_text = tk.Text(self.left_panel, width=25, height=5)
        self.notes_text.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Progress bar (drag a Progressbar from Toolbox)
        self.progress = ttk.Progressbar(
            self.left_panel, 
            orient=tk.HORIZONTAL, 
            length=200, 
            mode='determinate'
        )
        self.progress.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # Button frame (drag a Frame from Toolbox)
        self.button_frame = ttk.Frame(self.left_panel)
        self.button_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        # Submit button (drag a Button from Toolbox)
        self.submit_button = ttk.Button(
            self.button_frame, 
            text="Submit", 
            command=self.submit_form
        )
        self.submit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button (drag a Button from Toolbox)
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="Clear", 
            command=self.clear_form
        )
        self.clear_button.pack(side=tk.LEFT)
        
    def create_output_area(self):
        """Create output area in the right panel"""
        
        # Output text (drag a Text from Toolbox)
        self.output_text = tk.Text(
            self.right_panel, 
            wrap=tk.WORD, 
            width=30, 
            height=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar (drag a Scrollbar from Toolbox)
        self.scrollbar = ttk.Scrollbar(
            self.output_text, 
            orient=tk.VERTICAL, 
            command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial message
        self.output_text.insert(tk.END, "Form data will appear here when submitted.\n\n")
        self.output_text.insert(tk.END, "This demo shows how the Form Designer and Toolbox " 
                               "can be used to create Tkinter interfaces visually.\n\n")
        self.output_text.insert(tk.END, "Try submitting the form to see the data!\n")
        
    def submit_form(self):
        """Handle form submission"""
        # Validate form
        if not self.name_entry.get():
            messagebox.showerror("Error", "Please enter your name")
            return
            
        # Update progress bar
        self.progress['value'] = 0
        self.update_progress_bar()
        
        # Get form data
        name = self.name_entry.get()
        age = self.age_spin.get()
        gender = self.gender_var.get()
        country = self.country_combo.get()
        subscribed = "Yes" if self.subscribe_var.get() else "No"
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Clear and update output
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "=== Form Submission ===\n\n")
        self.output_text.insert(tk.END, f"Name: {name}\n")
        self.output_text.insert(tk.END, f"Age: {age}\n")
        self.output_text.insert(tk.END, f"Gender: {gender}\n")
        self.output_text.insert(tk.END, f"Country: {country}\n")
        self.output_text.insert(tk.END, f"Subscribed: {subscribed}\n")
        self.output_text.insert(tk.END, f"Notes: {notes}\n")
        
        # Update status
        self.status_bar.config(text=f"Form submitted by {name} at {country}")
        
    def update_progress_bar(self):
        """Simulate progress bar updating"""
        if self.progress['value'] < 100:
            self.progress['value'] += 10
            self.root.after(100, self.update_progress_bar)
        
    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.age_spin.set(25)
        self.gender_var.set("Male")
        self.country_combo.current(0)
        self.subscribe_var.set(True)
        self.notes_text.delete("1.0", tk.END)
        self.progress['value'] = 0
        
        # Update status
        self.status_bar.config(text="Form cleared")
        
        # Clear output
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Form has been cleared.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolboxDemoApp(root)
    root.mainloop()