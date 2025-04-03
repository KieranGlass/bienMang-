import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_all_children():
    """Fetch all children records from the database."""

    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM children")
        children = cursor.fetchall()
        
    return children

def search_existing_register(register_date_str, children):
    """Check if the register entry exists, if not, create one."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        # Check if the register already exists for the date
        cursor.execute('SELECT 1 FROM registers WHERE date = ?', (register_date_str,))
        if not cursor.fetchone():
            for child in children:
                child_id, first_name, last_name, _, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
                tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, \
                thursday_finish, friday_arrival, friday_finish = child

                # Determine the default arrival and finish times based on the weekday
                weekday_name = datetime.strptime(register_date_str, "%Y-%m-%d").strftime('%A').lower()
                arrival_column = f"{weekday_name}_arrival"
                finish_column = f"{weekday_name}_finish"
                arrival_time = locals()[arrival_column]
                finish_time = locals()[finish_column]

                cursor.execute('''INSERT INTO registers (date, child_id, adjusted_start_time, adjusted_end_time)
                                VALUES (?, ?, ?, ?)''', (register_date_str, child_id, arrival_time, finish_time))
            conn.commit()

def search_adjusted_schedule(register_date_str, child_id):
    """Check if there's an adjusted schedule for the day."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT adjusted_start_time, adjusted_end_time FROM registers WHERE date = ? AND child_id = ?', 
                       (register_date_str, child_id))
        adjusted_schedule = cursor.fetchone()
    return adjusted_schedule

def save_adjustment(date_str, child_id, start_entry, end_entry):
    """Save adjustments made to the schedule."""
    adjusted_start = start_entry.get()
    adjusted_end = end_entry.get()
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''INSERT OR REPLACE INTO registers (date, child_id, adjusted_start_time, adjusted_end_time)
                          VALUES (?, ?, ?, ?)''', (date_str, child_id, adjusted_start, adjusted_end))
        conn.commit()
            
class Registers(tk.Toplevel):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Registers...")
        self.title("Registers")
        self.geometry("1400x900")
        self.deiconify()
        self.lift()
        self.create_registers_window()      

    def create_registers_window(self):
        # Add a Home button
        home_button = ttk.Button(self, text="Home", command=self.go_home)
        home_button.pack(pady=20) 

        # Date selection (for example, selecting from a calendar)
        self.date_label = tk.Label(self, text="Select Date:")
        self.date_label.pack(pady=10)

        self.date_entry = ttk.Entry(self)  # Text field for date selection (e.g., YYYY-MM-DD)
        self.date_entry.pack(pady=10)

        select_button = ttk.Button(self, text="Select", command=self.show_register_for_day)
        select_button.pack(pady=10)

        # Frame for displaying the register list
        self.register_frame = ttk.Frame(self)
        self.register_frame.pack(fill='both', expand=True, padx=20, pady=20)

    def show_register_for_day(self):
        selected_date_str = self.date_entry.get()
        
        try:
            # Convert the selected date into a datetime object
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return
        
        # Fetch children data and their registers for the selected date
        self.display_children_for_day(selected_date)

    def display_children_for_day(self, selected_date):
        """Display children and their register information."""
        # Clear previous contents
        for widget in self.register_frame.winfo_children():
            widget.destroy()

        children = get_all_children()

        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Fetch or create register entries for the selected date
        search_existing_register(selected_date_str, children)

        for child in children:
            child_id, first_name, last_name, _, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
            tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, \
            thursday_finish, friday_arrival, friday_finish = child

            # Get the default schedule for the selected weekday
            weekday_name = selected_date.strftime('%A').lower()
            arrival_column = f"{weekday_name}_arrival"
            finish_column = f"{weekday_name}_finish"

            arrival_time = locals()[arrival_column]
            finish_time = locals()[finish_column]

            # Check for adjusted schedule
            adjusted_schedule = search_adjusted_schedule(selected_date_str, child_id)
            if adjusted_schedule:
                adjusted_start, adjusted_end = adjusted_schedule
            else:
                adjusted_start, adjusted_end = arrival_time, finish_time

            # Display the child's information and their schedule
            row_frame = ttk.Frame(self.register_frame)
            row_frame.pack(fill='x', padx=10, pady=5)

            child_name_label = tk.Label(row_frame, text=f"{first_name} {last_name}")
            child_name_label.pack(side="left", padx=10)

            child_start_label = tk.Label(row_frame, text=adjusted_start)
            child_start_label.pack(side="left", padx=10)

            child_end_label = tk.Label(row_frame, text=adjusted_end)
            child_end_label.pack(side="left", padx=10)

            # Button to adjust the schedule for that day
            adjust_button = ttk.Button(row_frame, text="Adjust", command=lambda child_id=child_id, date=selected_date: self.adjust_schedule(child_id, date))
            adjust_button.pack(side="left", padx=10)

    def adjust_schedule(self, child_id, date):
        """Adjust the schedule for a child."""
        date_str = date.strftime("%Y-%m-%d")

        # Create the adjustment window
        adjustment_window = tk.Toplevel(self)
        adjustment_window.title("Adjust Schedule")

        start_label = tk.Label(adjustment_window, text="Start Time:")
        start_label.pack(pady=5)
        start_entry = tk.Entry(adjustment_window)
        start_entry.pack(pady=5)

        end_label = tk.Label(adjustment_window, text="End Time:")
        end_label.pack(pady=5)
        end_entry = tk.Entry(adjustment_window)
        end_entry.pack(pady=5)

        save_button = ttk.Button(adjustment_window, text="Save", 
                                 command=lambda: save_adjustment(date_str, child_id, start_entry, end_entry))
        save_button.pack(pady=10)


    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

if __name__ == "__main__":
    app = Registers()
    app.mainloop()  # Starts the Tkinter event loop