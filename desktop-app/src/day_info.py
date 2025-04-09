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
                child_id, first_name, middle_name, last_name, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
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

class DayInfoPage(tk.Toplevel):
    def __init__(self, parent, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date  # The date clicked on the calendar
        self.title(f"Details for {self.selected_date}")
        self.geometry("1400x900")
        
        # Create a label for the day’s date
        self.date_label = tk.Label(self, text=f"Information for {self.selected_date}", font=("Helvetica", 16))
        self.date_label.grid(pady=10)

        # Create fields to display data (menu, register, etc.)
        self.menu_label = tk.Label(self, text="Menu: ", font=("Helvetica", 12))
        self.menu_label.grid(pady=5)

        self.menu_info = tk.Label(self, text="", font=("Helvetica", 12))  # To be populated with DB data
        self.menu_info.grid(pady=5)

        self.register_label = tk.Label(self, text="Register: ", font=("Helvetica", 12))
        self.register_label.grid(pady=5)

        self.register_frame = ttk.Frame(self)
        self.register_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.display_register(selected_date)

        # Back button to go back to the calendar dashboard
        self.back_button = tk.Button(self, text="Close", command=self.go_back)
        self.back_button.grid(pady=10)

        # Populate data for the selected date
        #self.load_day_info(self.selected_date)

    def display_register(self, selected_date):
        
        children = get_all_children()
        print(f"{selected_date}")

        # Fetch or create register entries for the selected date
        search_existing_register(selected_date, children)

        # Configure the grid for the table-like layout
        self.register_frame.grid_columnconfigure(0, weight=2, minsize=150)  # Column for name
        self.register_frame.grid_columnconfigure(1, weight=1, minsize=100)  # Column for start time
        self.register_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Column for end time

        name_header = tk.Label(self.register_frame, text="Child Name", font=("Arial", 12, "bold"))
        name_header.grid(row=1, column=0, padx=10, sticky="ew")

        start_header = tk.Label(self.register_frame, text="Start Time", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="ew")

        end_header = tk.Label(self.register_frame, text="End Time", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="ew")

        i = 2  # Keep track of row index
        for child in children:
            child_id, first_name, middle_name, last_name, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
            tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, \
            thursday_finish, friday_arrival, friday_finish = child

            # Get the default schedule for the selected weekday
            # Convert the string to a datetime object
            selected_date_str = datetime.strptime(selected_date, "%Y-%m-%d")
            weekday_name = selected_date_str.strftime('%A').lower()
            arrival_column = f"{weekday_name}_arrival"
            finish_column = f"{weekday_name}_finish"

            arrival_time = locals()[arrival_column]
            finish_time = locals()[finish_column]

            # Check for adjusted schedule
            adjusted_schedule = search_adjusted_schedule(selected_date, child_id)
            if adjusted_schedule:
                adjusted_start, adjusted_end = adjusted_schedule
            else:
                adjusted_start, adjusted_end = arrival_time, finish_time

            # Display child's information in the grid
            child_name_label = tk.Label(self.register_frame, text=f"{first_name} {last_name}")
            child_name_label.grid(row=i, column=0, pady=10, sticky="ew")

            child_start_label = tk.Label(self.register_frame, text=adjusted_start)
            child_start_label.grid(row=i, column=1, padx=10, sticky="ew")

            child_end_label = tk.Label(self.register_frame, text=adjusted_end)
            child_end_label.grid(row=i, column=2, padx=10, sticky="ew")

            # Increment the row index for the next child
            i += 1

    def go_back(self):
        """ Closes this window and brings the user back to the calendar dashboard """
        self.destroy()  # Close the DayInfoPage

    def load_day_info(self, date):
        """ Fetch and populate data for the selected date from the database """
        
        # Example DB query to fetch information for the selected date
        # Replace with your actual DB fetching logic
        data = self.get_day_data_from_db(date)

        if data:
            # Update the UI with the fetched data
            self.menu_info.config(text=data['menu'])
            self.register_info.config(text=data['register'])
        else:
            # If no data, show a default message
            self.menu_info.config(text="No menu info available")
            self.register_info.config(text="No register info available")

    def get_day_data_from_db(self, date):
        """ Simulate fetching data from a database for the given date """
        # In a real app, this would be replaced with actual database logic
        example_data = {
            "2025-03-29": {'menu': 'Pasta', 'register': 'Register info for March 29'},
            "2025-03-30": {'menu': 'Salad', 'register': 'Register info for March 30'},
        }
        return example_data.get(date, None)  # Returns None if no data is found for the date