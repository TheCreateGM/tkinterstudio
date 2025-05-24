import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox
from typing import Dict, Any, Optional, Callable, List, Tuple

class PropertyEditorDialog(tk.Toplevel):
    """Advanced property editor dialog for Tkinter widgets styled like Visual Studio 2010"""
    
    def __init__(self, parent, title: str, properties: Dict[str, Any], 
                 widget_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Initialize the property editor dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            properties: Dictionary of property names and values
            widget_type: The type of Tkinter widget being edited
            callback: Function to call with updated properties
        """
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.minsize(400, 500)
        
        # Store parameters
        self.properties = properties.copy()
        self.widget_type = widget_type
        self.callback = callback
        self.property_widgets = {}
        self.property_categories = {}
        
        # Configure the window with modern styling
        self.configure(padx=0, pady=0)
        self.configure(background='#F0F0F0')
        
        # Create the UI
        self._create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = min(600, self.winfo_screenwidth() - 100)
        height = min(600, self.winfo_screenheight() - 100)
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set initial focus
        if self.property_widgets:
            first_widget = next(iter(self.property_widgets.values()))
            first_widget.focus_set()
        
    def _create_widgets(self):
        """Create the dialog widgets in Visual Studio 2010 style"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar with modern styling
        toolbar = ttk.Frame(main_frame, style='Toolbutton.TFrame')
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        toolbar.configure(background='#E6E6E6', height=35)
        
        # Add toolbar buttons (categorized, alphabetical)
        self.view_var = tk.StringVar(value="Categorized")
        
        ttk.Label(toolbar, text="View:", background='#E6E6E6').pack(side=tk.LEFT, padx=5, pady=8)
        
        categorized_btn = ttk.Radiobutton(
            toolbar, text="Categorized", variable=self.view_var, 
            value="Categorized", command=self._refresh_property_view,
            style="Toolbar.TRadiobutton"
        )
        categorized_btn.pack(side=tk.LEFT, padx=5, pady=8)
        
        alphabetical_btn = ttk.Radiobutton(
            toolbar, text="Alphabetical", variable=self.view_var, 
            value="Alphabetical", command=self._refresh_property_view,
            style="Toolbar.TRadiobutton"
        )
        alphabetical_btn.pack(side=tk.LEFT, padx=5, pady=8)
        
        # Property name and type with modern styling
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.configure(background='#F0F0F0')
        
        property_header = ttk.Label(header_frame, text=f"{self.widget_type}", 
                 font=("Segoe UI", 12, "bold"), background='#F0F0F0', foreground='#0078D7')
        property_header.pack(anchor="w", padx=5, pady=3)
        
        # Search box with modern styling
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_frame.configure(background='#F0F0F0')
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._refresh_property_view())
        
        ttk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10), background='#F0F0F0').pack(side=tk.LEFT, padx=(5, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style="Modern.TEntry")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), pady=5)
        
        # Property grid using a Treeview for VS2010 look with modern styling
        self.property_tree = ttk.Treeview(
            main_frame, columns=("value"), 
            show="tree headings", 
            selectmode="browse",
            style="PropertyGrid.Treeview"
        )
        self.property_tree.heading("#0", text="Property")
        self.property_tree.heading("value", text="Value")
        self.property_tree.column("#0", width=200, stretch=False)
        self.property_tree.column("value", width=200)
        
        # Configure property grid style
        try:
            style = ttk.Style()
            style.configure("PropertyGrid.Treeview", 
                           background="#FFFFFF", 
                           foreground="#000000", 
                           rowheight=22,
                           fieldbackground="#FFFFFF")
            style.map("PropertyGrid.Treeview",
                     background=[("selected", "#CCE8FF")],
                     foreground=[("selected", "#000000")])
        except:
            pass
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.property_tree.yview)
        self.property_tree.configure(yscrollcommand=tree_scroll_y.set)
        
        # Pack tree and scrollbar
        self.property_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # Description frame with modern styling
        desc_frame = ttk.LabelFrame(main_frame, text="Description")
        desc_frame.pack(fill=tk.X, padx=5, pady=5)
        desc_frame.configure(padding=5)
        
        self.desc_text = tk.Text(desc_frame, height=3, wrap=tk.WORD, 
                              font=("Segoe UI", 9),
                              background="#F8F8F8",
                              relief="flat")
        self.desc_text.pack(fill=tk.X, padx=5, pady=5)
        self.desc_text.config(state=tk.DISABLED)
        
        # Button frame with modern styling
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        button_frame.configure(background='#F0F0F0')
        
        # OK and Cancel buttons
        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok, style="Primary.TButton")
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure button styles
        try:
            style = ttk.Style()
            style.configure("Primary.TButton", background="#0078D7", foreground="white", padding=5)
            style.map("Primary.TButton", background=[("active", "#005A9E")])
            style.configure("TButton", padding=5)
        except:
            pass
        
        # Bind events
        self.property_tree.bind("<<TreeviewSelect>>", self._on_property_select)
        self.property_tree.bind("<Double-1>", self._on_property_edit)
        
        # Populate the property tree
        self._populate_property_tree()
        
    def _get_ordered_properties(self) -> List[str]:
        """Return properties in a sensible order"""
        # Common properties to show first
        common_props = ["text", "background", "foreground", "font", "width", "height"]
        
        # Create ordered list
        ordered = []
        
        # Add common properties first (if they exist)
        for prop in common_props:
            if prop in self.properties:
                ordered.append(prop)
        
        # Add remaining properties alphabetically
        for prop in sorted(self.properties.keys()):
            if prop not in ordered:
                ordered.append(prop)
                
        return ordered
        
    def _get_categorized_properties(self) -> Dict[str, List[str]]:
        """Categorize properties in Visual Studio 2010 style"""
        categories = {
            "Appearance": ["background", "foreground", "font", "relief", "cursor"],
            "Behavior": ["command", "takefocus", "state"],
            "Layout": ["width", "height", "padx", "pady", "anchor"],
            "Text": ["text", "justify", "wraplength"],
            "Data": ["variable", "value", "values"],
            "Misc": []
        }
        
        # Categorize properties
        categorized = {category: [] for category in categories}
        
        for prop in self.properties:
            for category, props in categories.items():
                if prop in props:
                    categorized[category].append(prop)
                    break
            else:
                categorized["Misc"].append(prop)
        
        # Remove empty categories
        return {k: sorted(v) for k, v in categorized.items() if v}
        
    def _populate_property_tree(self):
        """Populate the property tree with properties"""
        # Clear the tree
        for item in self.property_tree.get_children():
            self.property_tree.delete(item)
            
        # Get view mode
        view_mode = self.view_var.get()
        search_text = self.search_var.get().lower()
        
        if view_mode == "Categorized":
            # Get categorized properties
            categories = self._get_categorized_properties()
            
            # Add categories and properties
            for category, props in categories.items():
                # Filter by search text if provided
                if search_text:
                    filtered_props = [p for p in props if search_text in p.lower() or 
                                     search_text in str(self.properties.get(p, "")).lower()]
                    if not filtered_props:
                        continue
                    props = filtered_props
                    
                # Add category
                category_id = self.property_tree.insert("", "end", text=category, open=True)
                
                # Add properties
                for prop in props:
                    value = self.properties.get(prop, "")
                    prop_id = self.property_tree.insert(
                        category_id, "end", 
                        text=prop, 
                        values=(value,),
                        tags=("property",)
                    )
                    
                    # Store property path for easy lookup
                    self.property_categories[prop] = category_id
        else:
            # Alphabetical view
            props = list(self.properties.keys())
            props.sort()
            
            # Filter by search text if provided
            if search_text:
                props = [p for p in props if search_text in p.lower() or 
                        search_text in str(self.properties.get(p, "")).lower()]
                
            # Add properties directly
            for prop in props:
                value = self.properties.get(prop, "")
                self.property_tree.insert(
                    "", "end", 
                    text=prop, 
                    values=(value,),
                    tags=("property",)
                )
                
    def _refresh_property_view(self):
        """Refresh the property view"""
        self._populate_property_tree()
        
    def _on_property_select(self, event):
        """Handle property selection"""
        selection = self.property_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Check if this is a property (not a category)
        if "property" in self.property_tree.item(item, "tags"):
            prop_name = self.property_tree.item(item, "text")
            
            # Update description
            self.desc_text.config(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert(tk.END, f"Property: {prop_name}\n")
            self.desc_text.insert(tk.END, f"Type: {type(self.properties.get(prop_name, '')).__name__}")
            self.desc_text.config(state=tk.DISABLED)
            
    def _on_property_edit(self, event):
        """Handle double-click on property"""
        selection = self.property_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Check if this is a property (not a category)
        if "property" in self.property_tree.item(item, "tags"):
            prop_name = self.property_tree.item(item, "text")
            value = self.properties.get(prop_name, "")
            
            # Special handling for certain property types
            if prop_name in ["background", "foreground"]:
                self._choose_color(prop_name)
            elif prop_name == "font":
                self._choose_font()
            else:
                # Create inline editor
                x, y, width, height = self.property_tree.bbox(item, column="value")
                
                # Create appropriate editor
                if isinstance(value, bool):
                    # Boolean property - toggle and update
                    self.properties[prop_name] = not value
                    self.property_tree.set(item, "value", str(not value))
                else:
                    # Text editor
                    entry = ttk.Entry(self.property_tree)
                    entry.insert(0, str(value))
                    entry.select_range(0, tk.END)
                    
                    # Position the entry
                    entry.place(x=x, y=y, width=width, height=height)
                    entry.focus_set()
                    
                    # Update property when done editing
                    def on_entry_complete(event=None):
                        new_value = entry.get()
                        
                        # Update property
                        self.properties[prop_name] = new_value
                        self.property_tree.set(item, "value", new_value)
                        
                        # Destroy entry
                        entry.destroy()
                        
                    entry.bind("<Return>", on_entry_complete)
                    entry.bind("<FocusOut>", on_entry_complete)
        
    def _create_property_editor(self, parent, prop_name: str, value: Any) -> tk.Widget:
        """Create an appropriate editor widget for the property"""
        
        # Boolean properties (use Checkbutton)
        if isinstance(value, bool) or (isinstance(value, str) and value.lower() in ["true", "false"]):
            var = tk.BooleanVar(value=bool(value))
            widget = ttk.Checkbutton(parent, variable=var)
            widget.var = var
            return widget
            
        # Numeric properties
        elif isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            var = tk.StringVar(value=str(value))
            widget = ttk.Spinbox(parent, from_=0, to=1000, textvariable=var)
            widget.var = var
            return widget
            
        # Options with specific values
        elif prop_name == "relief":
            values = ["flat", "raised", "sunken", "solid", "ridge", "groove"]
            var = tk.StringVar(value=value)
            widget = ttk.Combobox(parent, values=values, textvariable=var)
            widget.var = var
            return widget
            
        elif prop_name == "anchor":
            values = ["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]
            var = tk.StringVar(value=value)
            widget = ttk.Combobox(parent, values=values, textvariable=var)
            widget.var = var
            return widget
            
        elif prop_name == "justify":
            values = ["left", "center", "right"]
            var = tk.StringVar(value=value)
            widget = ttk.Combobox(parent, values=values, textvariable=var)
            widget.var = var
            return widget
            
        elif prop_name == "orient":
            values = ["horizontal", "vertical"]
            var = tk.StringVar(value=value)
            widget = ttk.Combobox(parent, values=values, textvariable=var)
            widget.var = var
            return widget
            
        elif prop_name == "state":
            values = ["normal", "disabled", "readonly"]
            var = tk.StringVar(value=value)
            widget = ttk.Combobox(parent, values=values, textvariable=var)
            widget.var = var
            return widget
            
        # Default to string entry
        else:
            var = tk.StringVar(value=str(value))
            widget = ttk.Entry(parent, textvariable=var)
            widget.var = var
            return widget
            
    def _choose_color(self, prop_name: str):
        """Open color chooser dialog"""
        current_color = self.properties.get(prop_name, "#FFFFFF")
        color = colorchooser.askcolor(color=current_color, title=f"Choose {prop_name} color")
        
        if color and color[1]:  # color is ((r,g,b), hex)
            # Update property
            self.properties[prop_name] = color[1]
            
            # Update tree view
            selection = self.property_tree.selection()
            if selection:
                self.property_tree.set(selection[0], "value", color[1])
            
    def _choose_font(self):
        """Open font chooser dialog (VS2010 style)"""
        current_font = self.properties.get("font", "TkDefaultFont")
        
        # Parse the current font
        font_family = "TkDefaultFont"
        font_size = 10
        font_weight = "normal"
        
        try:
            if "," in current_font:
                parts = current_font.split(",")
                font_family = parts[0].strip()
                if len(parts) > 1:
                    font_size = int(parts[1].strip())
                if len(parts) > 2:
                    font_weight = parts[2].strip()
        except:
            pass
            
        # Create a VS2010-style font chooser dialog with modern styling
        font_dialog = tk.Toplevel(self)
        font_dialog.title("Font")
        font_dialog.transient(self)
        font_dialog.grab_set()
        font_dialog.minsize(450, 350)
        font_dialog.configure(background='#F0F0F0')
        
        main_frame = ttk.Frame(font_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.configure(padding=5, style="Modern.TFrame")
        
        # Font selection frame with modern styling
        font_frame = ttk.LabelFrame(main_frame, text="Font")
        font_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        font_frame.configure(padding=8)
        
        # Font families
        font_family_frame = ttk.Frame(font_frame)
        font_family_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(font_family_frame, text="Font:").pack(side=tk.LEFT)
        
        family_var = tk.StringVar(value=font_family)
        family_combo = ttk.Combobox(font_family_frame, textvariable=family_var, width=25)
        family_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Get available font families
        families = sorted(font.families())
        family_combo['values'] = families
        
        # Preview with modern styling
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        preview_frame.configure(padding=8)
        
        preview_font = font.Font(family=font_family, size=font_size, weight=font_weight)
        preview_text = tk.Text(preview_frame, height=3, width=30, font=preview_font,
                            background="#FFFFFF", relief="flat", borderwidth=1)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_text.insert("1.0", "AaBbYyZz\n0123456789")
        preview_text.tag_configure("center", justify='center')
        preview_text.tag_add("center", "1.0", "end")
        preview_text.config(state=tk.DISABLED)
        
        # Update preview when font changes
        def update_preview(*args):
            try:
                preview_font.configure(
                    family=family_var.get(),
                    size=size_var.get(),
                    weight=weight_var.get()
                )
            except:
                pass
        
        # Font size and style frame
        font_details_frame = ttk.Frame(font_frame)
        font_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Font size
        ttk.Label(font_details_frame, text="Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        size_var = tk.IntVar(value=font_size)
        size_combo = ttk.Combobox(font_details_frame, textvariable=size_var, width=5,
                                 values=[8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72])
        size_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Font style
        ttk.Label(font_details_frame, text="Style:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        weight_var = tk.StringVar(value=font_weight)
        style_combo = ttk.Combobox(font_details_frame, textvariable=weight_var, width=10,
                                  values=["normal", "bold", "italic", "bold italic"])
        style_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Bind preview updates
        family_combo.bind("<<ComboboxSelected>>", update_preview)
        size_combo.bind("<<ComboboxSelected>>", update_preview)
        style_combo.bind("<<ComboboxSelected>>", update_preview)
        
        # OK/Cancel buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def on_font_ok():
            # Combine font properties
            font_str = f"{family_var.get()}, {size_var.get()}, {weight_var.get()}"
            
            # Update property
            self.properties["font"] = font_str
            
            # Update tree view
            selection = self.property_tree.selection()
            if selection:
                self.property_tree.set(selection[0], "value", font_str)
                
            font_dialog.destroy()
            
        ttk.Button(button_frame, text="OK", command=on_font_ok, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=font_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center the dialog
        font_dialog.update_idletasks()
        width = max(400, font_dialog.winfo_width())
        height = max(300, font_dialog.winfo_height())
        x = (font_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (font_dialog.winfo_screenheight() // 2) - (height // 2)
        font_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
    def _on_ok(self):
        """Handle OK button click"""
        # Call the callback with the updated properties
        self.callback(self.properties)
        
        # Close the dialog
        self.destroy()
        
class PropertyEditorFactory:
    """Factory class to create property editors for different widget types"""
    
    @staticmethod
    def create_editor(parent, widget_type: str, properties: Dict[str, Any], 
                      callback: Callable[[Dict[str, Any]], None]) -> PropertyEditorDialog:
        """Create a property editor dialog for a specific widget type"""
        
        # Title based on widget type
        title = f"Properties - {widget_type}"
        
        # Create and return the dialog
        return PropertyEditorDialog(parent, title, properties, widget_type, callback)
        
    @staticmethod
    def get_default_properties(widget_type: str) -> Dict[str, Any]:
        """Get default properties for a specific widget type"""
        
        # Common properties
        common = {
            "background": "#FFFFFF",
            "foreground": "#000000",
            "font": "TkDefaultFont",
            "relief": "flat"
        }
        
        # Widget-specific properties
        specific = {
            "Button": {
                "text": "Button",
                "command": "on_button_click",
                "width": 10,
                "height": 1
            },
            "Label": {
                "text": "Label",
                "width": 10,
                "height": 1,
                "anchor": "center"
            },
            "Entry": {
                "width": 20,
                "show": "",
                "state": "normal"
            },
            "Checkbutton": {
                "text": "Checkbutton",
                "variable": "var",
                "onvalue": True,
                "offvalue": False
            },
            "Radiobutton": {
                "text": "Radiobutton",
                "variable": "var",
                "value": 1
            },
            "Frame": {
                "width": 200,
                "height": 150,
                "borderwidth": 1
            },
            "LabelFrame": {
                "text": "LabelFrame",
                "width": 200,
                "height": 150
            },
            "Listbox": {
                "height": 5,
                "width": 20,
                "selectmode": "single"
            },
            "Text": {
                "width": 30,
                "height": 5,
                "wrap": "word"
            },
            "Canvas": {
                "width": 200,
                "height": 150,
                "borderwidth": 1
            },
            "Scrollbar": {
                "orient": "vertical"
            },
            "Scale": {
                "orient": "horizontal",
                "from_": 0,
                "to": 100,
                "resolution": 1
            },
            "Spinbox": {
                "from_": 0,
                "to": 100,
                "increment": 1,
                "width": 10
            },
            "Combobox": {
                "values": ["Item 1", "Item 2", "Item 3"],
                "width": 15,
                "state": "readonly"
            },
            "Treeview": {
                "columns": "column1,column2",
                "show": "headings",
                "height": 5
            },
            "Progressbar": {
                "orient": "horizontal",
                "length": 100,
                "mode": "determinate",
                "value": 50
            },
            "Notebook": {
                "width": 300,
                "height": 200
            },
            "PanedWindow": {
                "orient": "horizontal",
                "width": 300,
                "height": 200
            }
        }
        
        # Combine common with specific properties
        if widget_type in specific:
            return {**common, **specific[widget_type]}
        else:
            return common

if __name__ == "__main__":
    # Test the property editor
    root = tk.Tk()
    root.title("Property Editor Test")
    
    def test_callback(properties):
        print("Updated properties:", properties)
    
    button = ttk.Button(root, text="Edit Button Properties")
    button.pack(padx=20, pady=20)
    
    # Sample properties
    props = PropertyEditorFactory.get_default_properties("Button")
    
    button.configure(command=lambda: PropertyEditorFactory.create_editor(
        root, "Button", props, test_callback))
    
    root.mainloop()