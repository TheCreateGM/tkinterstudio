#!/usr/bin/env python3
"""
Hello World Example
A simple Python script to demonstrate the IDE features
"""

import tkinter as tk
from tkinter import messagebox
import time
import random

def main():
    """Main function that creates a simple Tkinter window"""
    # Create the root window
    root = tk.Tk()
    root.title("Hello World Application")
    root.geometry("400x300")
    
    # Set background color
    root.configure(bg="#f0f0f0")
    
    # Create a frame
    frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
    frame.pack(expand=True)
    
    # Create a label with welcome message
    label = tk.Label(
        frame,
        text="Hello, World!",
        font=("Arial", 24, "bold"),
        fg="#0078d7",  # Blue color similar to VS 2010
        bg="#f0f0f0"
    )
    label.pack(pady=20)
    
    # Function for the button
    def show_message():
        messages = [
            "Python is awesome!",
            "Tkinter makes GUI development easy.",
            "Programming is fun!",
            "Keep learning and coding!",
            "Visual Studio style IDE in Python!"
        ]
        messagebox.showinfo("Message", random.choice(messages))
    
    # Create a button
    button = tk.Button(
        frame,
        text="Click Me!",
        command=show_message,
        font=("Arial", 12),
        bg="#e1e1e1",
        activebackground="#cccccc",
        padx=10,
        pady=5
    )
    button.pack(pady=10)
    
    # Add current time display
    time_label = tk.Label(
        frame,
        text="",
        font=("Arial", 10),
        fg="#666666",
        bg="#f0f0f0"
    )
    time_label.pack(pady=5)
    
    # Update time
    def update_time():
        current_time = time.strftime("%H:%M:%S")
        time_label.config(text=f"Current Time: {current_time}")
        root.after(1000, update_time)  # Update every second
    
    update_time()
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    print("Starting Hello World application...")
    main()
    print("Application closed.")