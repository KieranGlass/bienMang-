import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
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
        self.default_register_for_day()   

    def create_registers_window(self):
        # Set up the grid layout with three columns
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Register list (flexible)
        self.grid_columnconfigure(2, weight=1, minsize=200)  # Calendar (flexible)

        # Add the sidebar
        self.create_global_sidebar()
        
        # Column 2 (Middle): Register list and day title
        self.register_frame = ttk.Frame(self)
        self.register_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Date selection and calendar in column 3
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)

        # Calendar widget for date selection
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(pady=10)

        select_button = ttk.Button(self.calendar_frame, text="Select", command=self.show_register_for_day)
        select_button.grid(pady=10)

    def create_global_sidebar(self):
        """ Create the sidebar with tabs """
        # Sidebar container (frame)
        sidebar_frame = ttk.Frame(self, relief="raised")
        sidebar_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsw")

        # Tab buttons
        self.create_sidebar_tab(sidebar_frame, "Home", self.go_home, 0)
        self.create_sidebar_tab(sidebar_frame, "Tab 1", self.go_home, 1)
        self.create_sidebar_tab(sidebar_frame, "Tab 2", self.go_home, 2)
        self.create_sidebar_tab(sidebar_frame, "Tab 3", self.go_home, 3)
        self.create_sidebar_tab(sidebar_frame, "Tab 4", self.go_home, 4)
        self.create_sidebar_tab(sidebar_frame, "Tab 5", self.go_home, 5)
        self.create_sidebar_tab(sidebar_frame, "Log Out", self.go_home, 6)

    def create_sidebar_tab(self, frame, text, command, row):
        """ Helper function to create each sidebar tab """
        tab_button = ttk.Button(frame, text=text, command=command)
        tab_button.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        style = ttk.Style()
        style.configure(
            "Custom.TButton",
            background="#1e3a5f",  # Darkish blue
            foreground="white",     # White text
            font=("Arial", 12, "bold"),
            relief="raised",        # Raised effect (simulates depth)
            padding=(10, 5),        # Padding for more space inside
            borderwidth=2,          # Border width for depth
            anchor="center",  
        )
        style.map("Custom.TButton", background=[("active", "#2c4b7f")])  # Lighter blue on hover
        tab_button.configure(style="Custom.TButton")

    def default_register_for_day(self):
        selected_date_str = self.calendar.get_date()

        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return
        
        self.display_children_for_day(selected_date)

    def show_register_for_day(self):
        selected_date_str = self.calendar.get_date()
        
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

        self.update_day_label(selected_date)

        children = get_all_children()

        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Fetch or create register entries for the selected date
        search_existing_register(selected_date_str, children)

        # Configure the grid for the table-like layout
        self.register_frame.grid_columnconfigure(0, weight=2, minsize=150)  # Column for name
        self.register_frame.grid_columnconfigure(1, weight=1, minsize=100)  # Column for start time
        self.register_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Column for end time
        self.register_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Column for adjust button

        name_header = tk.Label(self.register_frame, text="Child Name", font=("Arial", 12, "bold"))
        name_header.grid(row=1, column=0, padx=10, sticky="ew")

        start_header = tk.Label(self.register_frame, text="Start Time", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="ew")

        end_header = tk.Label(self.register_frame, text="End Time", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="ew")

        adjust_header = tk.Label(self.register_frame, text="Adjust", font=("Arial", 12, "bold"))
        adjust_header.grid(row=1, column=3, padx=10, sticky="ew")

        # Loop through the children and display their schedule
        i = 2  # Keep track of row index
        for child in children:
            child_id, first_name, middle_name, last_name, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
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

            # Display child's information in the grid
            child_name_label = tk.Label(self.register_frame, text=f"{first_name} {last_name}")
            child_name_label.grid(row=i, column=0, pady=10, sticky="ew")

            child_start_label = tk.Label(self.register_frame, text=adjusted_start)
            child_start_label.grid(row=i, column=1, padx=10, sticky="ew")

            child_end_label = tk.Label(self.register_frame, text=adjusted_end)
            child_end_label.grid(row=i, column=2, padx=10, sticky="ew")

            # Button to adjust the schedule for that day (always in the same column)
            adjust_button = ttk.Button(self.register_frame, text="Adjust", command=lambda child_id=child_id, date=selected_date: self.adjust_schedule(child_id, date))
            adjust_button.grid(row=i, column=3, padx=10, sticky="ew")

            # Increment the row index for the next child
            i += 1

    def update_day_label(self, date):
        """ Update the label in the middle column to show the selected day """
        from datetime import datetime
        
        
        # Format the selected date into the desired format (e.g., "Monday, 2nd June 2025")
        day_name = date.strftime("%A")
        print(f"{day_name}")
        day_number = date.day
        print(f"{day_number}")
        month_name = date.strftime("%B")
        print(f"{month_name}")
        year = date.year
        print(f"{year}")
        
        # Handle the suffix for the day number (e.g., 1st, 2nd, 3rd, etc.)
        suffix = 'th'
        if 4 <= day_number <= 20:
            suffix = 'th'
        elif day_number % 10 == 1:
            suffix = 'st'
        elif day_number % 10 == 2:
            suffix = 'nd'
        elif day_number % 10 == 3:
            suffix = 'rd'

        # Format the date string
        formatted_date = f"{day_name} {day_number}{suffix} {month_name} {year}"
        print(f"{formatted_date}")

       
        self.day_label = tk.Label(self.register_frame, text=formatted_date, font=("Arial", 18))
        self.day_label.grid(row=0, column=0, columnspan=4, pady=20, padx=10)

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
    app.mainloop()