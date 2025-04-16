import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_child_by_id(child_id):
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM children WHERE id =?', (child_id,))
        child = cursor.fetchone()
    
    return child

class ChildDayInfoPage(tk.Toplevel):
    def __init__(self, parent, child_id, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date
        self.child_id = child_id
        self.geometry("600x600")

        child = get_child_by_id(child_id)
        print(f"{child}")

        fname = child[1]
        lname = child[3]

        self.title(f"Day info for {fname} {lname}")

        # Title Label
        self.title_label = tk.Label(self, text=f"Day info for {fname} {lname} on {selected_date}", font=("Helvetica", 14, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # How well the child ate
        tk.Label(self, text="How well did the child eat? (1-5):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.eating_scale = tk.Scale(self, from_=1, to=5, orient=tk.HORIZONTAL)
        self.eating_scale.grid(row=1, column=1, sticky='w', padx=10)

        # Poop Checkbox
        self.pooped_var = tk.BooleanVar()
        self.poop_checkbox = tk.Checkbutton(self, text="Did the child poop?", variable=self.pooped_var, command=self.toggle_poop_count)
        self.poop_checkbox.grid(row=2, column=0, sticky='w', padx=10, pady=5)

        # Poop count (disabled by default)
        tk.Label(self, text="How many times?").grid(row=3, column=0, sticky='w', padx=10)
        self.poop_count_spinbox = tk.Spinbox(self, from_=0, to=10, state='disabled')
        self.poop_count_spinbox.grid(row=3, column=1, sticky='w', padx=10)

        # Sleep duration
        tk.Label(self, text="How long did the child sleep? (e.g. 1h 30m):").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.sleep_entry = tk.Entry(self)
        self.sleep_entry.grid(row=4, column=1, sticky='w', padx=10)

        # Additional comments
        tk.Label(self, text="Additional comments:").grid(row=5, column=0, sticky='nw', padx=10, pady=5)
        self.comments_text = tk.Text(self, width=40, height=6)
        self.comments_text.grid(row=5, column=1, sticky='w', padx=10, pady=5)

        # Save Button (you could connect this to a save function)
        self.save_button = tk.Button(self, text="Save", command=self.save_day_info)
        self.save_button.grid(row=6, column=0, columnspan=2, pady=20)

    def toggle_poop_count(self):
        if self.pooped_var.get():
            self.poop_count_spinbox.config(state='normal')
        else:
            self.poop_count_spinbox.config(state='disabled')
            self.poop_count_spinbox.delete(0, 'end')
            self.poop_count_spinbox.insert(0, '0')

    def save_day_info(self):
        # Placeholder for saving logic
        data = {
            "child_id": self.child_id,
            "date": self.selected_date,
            "ate_well": self.eating_scale.get(),
            "pooped": self.pooped_var.get(),
            "poop_count": int(self.poop_count_spinbox.get()) if self.pooped_var.get() else 0,
            "sleep_duration": self.sleep_entry.get(),
            "comments": self.comments_text.get("1.0", tk.END).strip()
        }
        print("Saved data:", data)
        # Insert data into your database or process as needed