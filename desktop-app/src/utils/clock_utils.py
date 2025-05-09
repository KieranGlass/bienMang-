import tkinter as tk
import time
from datetime import datetime, timedelta

def create_clock(parent, update_target):
    label = tk.Label(parent, font=("Helvetica", 20), bg="#d9f1fb")
    label.grid(pady=10, sticky="ns")
    update_clock(label, update_target)
    return label

def update_clock(label, update_target):
    current_time = time.strftime("%H:%M")
    label.config(text=current_time)
    label.after(1000, lambda: update_clock(label, update_target))

def generate_time_slots(start_time="07:30", end_time="18:00", interval=15):

    # Create a list to store time slots
    time_slots = ["N/A"]
    
    # Parse the start and end times
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    # Generate time slots from start_time to end_time with the specified interval
    while start <= end:
        time_slots.append(start.strftime("%H:%M"))
        start += timedelta(minutes=interval)
    
    return time_slots