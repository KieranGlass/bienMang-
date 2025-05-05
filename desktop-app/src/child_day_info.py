import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from functools import partial


def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_child_by_id(child_id):
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM children WHERE id =?', (child_id,))
        child = cursor.fetchone()
    
    return child

def save_day_info(self, completed):

    child_id = self.child_id
    selected_date = self.selected_date

    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        # Get current data from the UI
        starter = self.sliders.get("starter", None)
        main = self.sliders.get("main")
        dessert = self.sliders.get("dessert")
        pooped = self.pooped_var.get()
        poop_count = int(self.poop_count_spinbox.get()) if pooped else 0
        sleep_duration = self.sleep_combobox.get()
        comments = self.comments_text.get("1.0", tk.END).strip()

        # Convert slider values (round to nearest int)
        starter_val = int(round(starter.get())) if starter else None
        main_val = int(round(main.get())) if main else None
        dessert_val = int(round(dessert.get())) if dessert else None
        # Check if entry exists
        cursor.execute('''
            SELECT id FROM child_day_info WHERE child_id = ? AND date = ?
        ''', (child_id, selected_date))
        existing = cursor.fetchone()
        print(f"{completed}")
        if existing:
            print("Updating existing record:", existing)
            # Update existing record
            cursor.execute('''
                UPDATE child_day_info
                SET starter = ?, main = ?, dessert = ?, pooped = ?, poop_count = ?, 
                    sleep_duration = ?, comments = ?, completed = ?
                WHERE child_id = ? AND date = ?
            ''', (
                starter_val, main_val, dessert_val, pooped, poop_count,
                sleep_duration, comments, completed, child_id, selected_date
            ))
            print("Rows updated:", conn.total_changes)
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO child_day_info 
                (child_id, date, starter, main, dessert, pooped, poop_count, sleep_duration, comments, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                child_id, selected_date, starter_val, main_val, dessert_val,
                pooped, poop_count, sleep_duration, comments, completed
            ))

        conn.commit()
    print("Day info saved and marked as complete." if completed == 1 else "Day info saved.")
    self.parent.refresh_register(selected_date)
    self.destroy()

def load_day_info(self):
    child_id = self.child_id
    selected_date = self.selected_date

    # Try to load existing day info
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            SELECT starter, main, dessert, pooped, poop_count, sleep_duration, comments
            FROM child_day_info
            WHERE child_id = ? AND date = ?
        ''', (child_id, selected_date))
        row = cursor.fetchone()

        day_data = None
    if row:
        day_data = {
            "starter": row[0],
            "main": row[1],
            "dessert": row[2],
            "pooped": bool(row[3]),
            "poop_count": row[4],
            "sleep_duration": row[5],
            "comments": row[6]
        }
    return day_data

class ChildDayInfoPage(tk.Toplevel):
    def __init__(self, parent, child_id, selected_date):
        super().__init__(parent)
        self.parent = parent
        self.selected_date = selected_date
        self.child_id = child_id
        self.geometry("800x800")

        self.setup_page_layout(child_id, selected_date)

    def setup_page_layout(self, child_id, selected_date):
            
            child = get_child_by_id(child_id)

            self.existing_day_data = load_day_info(self)

            self.slider_words = {
                1: "Nothing",
                2: "A Little",
                3: "Okay",
                4: "Good",
                5: "Excellent"
            }

            fname = child[1]
            lname = child[3]
            self.title(f"{fname} {lname}: {selected_date}")
            group = child[5].lower() if child[5] else "baby"
            print(f"Child group: {group}")

            # Root grid config
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Container Frame
            main_frame = tk.Frame(self)
            main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

            for i in range(3):
                main_frame.grid_columnconfigure(i, weight=1)

            # Title
            self.title_label = tk.Label(
                main_frame,
                text=f"{fname} {lname}: {selected_date}",
                font=("Helvetica", 14, "bold"),
                wraplength=600,
                anchor="center",
                justify="center"
            )
            self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="n")


            # How well the child ate
            tk.Label(main_frame, text=f"How well did {fname} eat?").grid(row=1, column=0, sticky='w', padx=10, pady=5)

            self.sliders = {}  # to store slider values

            row_counter = 2

            # Sliders based on group
            if group in ["grands", "moyens"]:
                for label in ["Starter", "Main", "Dessert"]:
                    key = label.lower()
                    value = self.existing_day_data.get(key, 3) if self.existing_day_data else 3
                    self.create_slider(main_frame, label, row_counter, value=value)
                    row_counter += 1
            else:
                for label in ["Main", "Dessert"]:
                    key = label.lower()
                    value = self.existing_day_data.get(key, 3) if self.existing_day_data else 3
                    self.create_slider(main_frame, label, row_counter, value=value)
                    row_counter += 1


            # Poop Checkbox
            self.pooped_var = tk.BooleanVar()
            tk.Label(main_frame, text="Did the child poop?").grid(row=row_counter, column=0, sticky="w", padx=(10, 5), pady=10)

            self.poop_checkbox = tk.Checkbutton(main_frame, variable=self.pooped_var, command=self.toggle_poop_count)
            self.poop_checkbox.grid(row=row_counter, column=1, sticky="w", pady=10)

            if self.existing_day_data:
                self.pooped_var.set(self.existing_day_data["pooped"])

            row_counter += 1

            # Poop count
            tk.Label(main_frame, text="How many times?").grid(row=row_counter, column=0, sticky='w', padx=10)
            self.poop_count_spinbox = tk.Spinbox(main_frame, from_=0, to=10, state='normal' if self.pooped_var.get() else 'disabled')
            self.poop_count_spinbox.grid(row=row_counter, column=1, sticky='w', padx=10)
            if self.existing_day_data:
                self.poop_count_spinbox.delete(0, 'end')
                self.poop_count_spinbox.insert(0, str(self.existing_day_data["poop_count"]))
            row_counter += 1

            # Generate durations
            durations = []
            for minutes in range(0, 241, 15):
                hours = minutes // 60
                mins = minutes % 60
                if hours == 0:
                    label = f"{mins} mins" if mins > 0 else "0"
                elif mins == 0:
                    label = f"{hours} hour" if hours == 1 else f"{hours} hours"
                else:
                    hour_label = f"{hours} hour" if hours == 1 else f"{hours} hours"
                    label = f"{hour_label} {mins} mins"
                durations.append(label)

            # Label and dropdown
            tk.Label(main_frame, text=f"How long did {fname} sleep?").grid(row=row_counter, column=0, sticky='w', padx=10, pady=5)
            self.sleep_combobox = ttk.Combobox(main_frame, values=durations, state="readonly", width=20)
            self.sleep_combobox.grid(row=row_counter, column=1, sticky='w', padx=10)

            if self.existing_day_data:
                self.sleep_combobox.set(self.existing_day_data["sleep_duration"])
            else:
                self.sleep_combobox.current(0)
            row_counter += 1

            # Additional comments
            tk.Label(main_frame, text="Additional comments:").grid(row=row_counter, column=0, sticky='nw', padx=10, pady=5)
            self.comments_text = tk.Text(main_frame, width=40, height=6)
            self.comments_text.grid(row=row_counter, column=1, sticky='w', padx=10, pady=5)
            if self.existing_day_data:
                self.comments_text.insert("1.0", self.existing_day_data["comments"])
            row_counter += 1

            # Buttons Frame
            buttons_frame = tk.Frame(main_frame)
            buttons_frame.grid(row=row_counter, column=0, columnspan=2, pady=20)

            # Update Button
            self.save_button = tk.Button(buttons_frame, text="Update", command=lambda: save_day_info(self, completed=0))
            self.save_button.pack(side="left", padx=10)

            # Complete Day Button
            self.complete_button = tk.Button(buttons_frame, text="Complete Day", bg="#4CAF50", fg="white",
                                 command=lambda: save_day_info(self, completed=1))
            self.complete_button.pack(side="left", padx=10)


    def create_slider(self, parent, label_text, row, value=3):
        tk.Label(parent, text=f"{label_text}:", font=("Helvetica", 11)).grid(
            row=row, column=0, sticky="w", padx=(20, 15)
        )

        scale_var = tk.DoubleVar(value=value)
        slider = ttk.Scale(parent, from_=1, to=5, orient="horizontal", length=100, variable=scale_var)
        slider.grid(row=row, column=1, sticky="ew", padx=(5, 5))

        value_label = tk.Label(parent, text=self.slider_words[int(scale_var.get())], width=8, anchor="w")
        value_label.grid(row=row, column=2, sticky="w")

        scale_var.trace_add("write", partial(self.update_slider_word, var=scale_var, label=value_label))
        self.sliders[label_text.lower()] = scale_var

    def update_slider_word(self, *args, var=None, label=None):
        if var and label:
            value = int(round(var.get()))
            label.config(text=self.slider_words.get(value, str(value)))

    def toggle_poop_count(self):
        if self.pooped_var.get():
            self.poop_count_spinbox.config(state='normal')
        else:
            self.poop_count_spinbox.config(state='disabled')
            self.poop_count_spinbox.delete(0, 'end')
            self.poop_count_spinbox.insert(0, '0')
