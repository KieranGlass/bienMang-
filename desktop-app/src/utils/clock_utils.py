import tkinter as tk
import time

def create_clock(parent, update_target):
    label = tk.Label(parent, font=("Helvetica", 20), bg="#d9f1fb")
    label.grid(pady=10, sticky="ns")
    update_clock(label, update_target)
    return label

def update_clock(label, update_target):
    current_time = time.strftime("%H:%M")
    label.config(text=current_time)
    label.after(1000, lambda: update_clock(label, update_target))