import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import time
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
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        # Add the sidebar
        self.create_global_sidebar()
        
        # ===== Scrollable Register Container =====
        self.register_container = ttk.Frame(self)
        self.register_container.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=(10, 0))

        # Canvas for scrollable content
        self.register_canvas = tk.Canvas(self.register_container)
        self.scrollbar = ttk.Scrollbar(self.register_container, orient="vertical", command=self.register_canvas.yview)

        # Inner frame that will hold all child rows
        self.scrollable_register_frame = ttk.Frame(self.register_canvas)
        
        # Window inside canvas (capture window ID to modify width)
        self.canvas_window_id = self.register_canvas.create_window(
            (0, 0), window=self.scrollable_register_frame, anchor="nw"
        )

        # Bind canvas resizing to match inner frame width
        self.register_canvas.bind(
            "<Configure>",
            lambda e: self.register_canvas.itemconfig(self.canvas_window_id, width=e.width)
        )

        # Scroll region update when frame size changes
        self.scrollable_register_frame.bind(
            "<Configure>",
            lambda e: self.register_canvas.configure(
                scrollregion=self.register_canvas.bbox("all")
            )
        )       

        # Scroll settings
        self.register_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar into container
        self.register_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.register_container.grid_propagate(True)        

        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(0, weight=1)

        # Calendar widget for date selection
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.calendar.bind("<<CalendarMonthChanged>>", self.highlight_weekdays)

        self.highlight_weekdays()

        select_button_style = ttk.Style()
        select_button_style.configure(
            "Select.TButton",
            background="#add8e6",
            foreground="black",
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
        )
        select_button_style.map("Select.TButton",
                background=[("active", "#87ceeb")])


        select_button = ttk.Button(self.calendar_frame, text="Select", style="Select.TButton", command=self.show_register_for_day)
        select_button.grid(pady=10)

        self.create_clock(self.sidebar_frame)

    def create_global_sidebar(self):
        """ Create the sidebar with tabs """
        # Sidebar container (frame)
        self.sidebar_frame = ttk.Frame(self, relief="raised")
        self.sidebar_frame.grid(row=0, column=0, rowspan=1, padx=0, pady=0, sticky="nsw")

        # Tab buttons
        self.create_sidebar_tab(self.sidebar_frame, "Home", self.go_home, 0)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 1", self.go_home, 1)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 2", self.go_home, 2)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 3", self.go_home, 3)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 4", self.go_home, 4)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 5", self.go_home, 5)
        self.create_sidebar_tab(self.sidebar_frame, "Log Out", self.go_home, 6)

    def create_sidebar_tab(self, frame, text, command, row):
        """ Helper function to create each sidebar tab """
        tab_button = ttk.Button(frame, text=text, command=command)
        tab_button.grid(row=row, column=0, padx=0, pady=5, sticky="w")

        tab_button_style = ttk.Style()
        tab_button_style.configure(
            "Custom.TButton",
            background="#1e3a5f",
            foreground="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            padding=(10, 5),
            borderwidth=2,
            anchor="center",
        )
        tab_button_style.map("Custom.TButton", background=[("active", "#2c4b7f")])
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
        for widget in self.scrollable_register_frame.winfo_children():
            widget.destroy()

        self.update_day_label(selected_date)

        children = get_all_children()

        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Fetch or create register entries for the selected date
        search_existing_register(selected_date_str, children)

        # Configure the grid for the table-like layout
        self.scrollable_register_frame.grid_columnconfigure(0, weight=2, minsize=150)  # Column for name
        self.scrollable_register_frame.grid_columnconfigure(1, weight=1, minsize=100)  # Column for start time
        self.scrollable_register_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Column for end time
        self.scrollable_register_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Column for adjust button

        name_header = tk.Label(self.scrollable_register_frame, text="Child Name", font=("Arial", 12, "bold"))
        name_header.grid(row=1, column=0, padx=0, sticky="ew")

        start_header = tk.Label(self.scrollable_register_frame, text="Start Time", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="ew")

        end_header = tk.Label(self.scrollable_register_frame, text="End Time", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="ew")

        adjust_header = tk.Label(self.scrollable_register_frame, text="")
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
            child_name_label = tk.Label(self.scrollable_register_frame, text=f"{first_name} {last_name}", bg="#f4f4f4", relief="solid", padx=5)
            child_name_label.grid(row=i, column=0, pady=10, sticky="ew")

            child_start_label = tk.Label(self.scrollable_register_frame, text=adjusted_start, bg="#f4f4f4", relief="solid", padx=5)
            child_start_label.grid(row=i, column=1, padx=10, sticky="ew")

            child_end_label = tk.Label(self.scrollable_register_frame, text=adjusted_end, bg="#f4f4f4", relief="solid", padx=5)
            child_end_label.grid(row=i, column=2, padx=10, sticky="ew")

            adjust_button_style = ttk.Style()

            adjust_button_style.configure("LightBlue.TButton",
                background="#add8e6",
                foreground="black",
                borderwidth=1,
                focusthickness=3,
                focuscolor='none')
            
            adjust_button_style.map("LightBlue.TButton",
                background=[("active", "#87ceeb")]) 

            adjust_button = ttk.Button(
                self.scrollable_register_frame,
                text="Adjust",
                style="LightBlue.TButton",
                # Saves the pupil varaibles for each iteration, for passing info to adjust schedule
                command=lambda id=child_id, date=selected_date, start=adjusted_start, end=adjusted_end,
                name=first_name + "" + last_name: self.adjust_schedule(id, date, start, end, name)
            )
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

       
        self.day_label = tk.Label(self.scrollable_register_frame, text=formatted_date, font=("Arial", 14))
        self.day_label.grid(row=0, column=0, columnspan=2, pady=10, padx=0)

    def adjust_schedule(self, child_id, date, current_start, current_end, name):
        """Adjust the schedule for a child."""
        date_str = date.strftime("%Y-%m-%d")
        time_options = self.generate_time_slots()
        print(f"{current_start} // {current_end}")

        adjustment_window = tk.Toplevel(self)
        adjustment_window.title(f"Adjust Schedule for {name}")
        adjustment_window.geometry("400x300")
        adjustment_window.resizable(True, True)

        adjustment_window.grab_set()

        adjustment_window.grid_rowconfigure(0, weight=1)
        adjustment_window.grid_columnconfigure(0, weight=1)

        container = ttk.Frame(adjustment_window, padding=20)
        container.grid(row=0, column=0, sticky="nsew")

        for r in range(7):
            container.grid_rowconfigure(r, weight=1)
        container.grid_columnconfigure(0, weight=1)

        start_label = ttk.Label(container, text="Start Time:", anchor="center", justify="center")
        start_label.grid(row=0, column=0, pady=(20, 5), sticky="n")

        start_combo = ttk.Combobox(container, values=time_options, state="readonly", width=20)
        start_combo.set(current_start if current_start in time_options else "N/A")
        start_combo.grid(row=1, column=0, pady=(0, 10), sticky="n")

        end_label = ttk.Label(container, text="End Time:", anchor="center", justify="center")
        end_label.grid(row=2, column=0, pady=(10, 5), sticky="n")

        end_combo = ttk.Combobox(container, values=time_options, state="readonly", width=20)
        end_combo.set(current_end if current_end in time_options else "N/A")
        end_combo.grid(row=3, column=0, pady=(0, 10), sticky="n")

        container.grid_rowconfigure(4, minsize=10)

        def validate_and_save():
            start = start_combo.get()
            end = end_combo.get()

            if (start == "N/A" and end != "N/A") or (start != "N/A" and end == "N/A"):
                messagebox.showerror("Invalid Input", "Both times must be set or both must be N/A.")
                return

            if start != "N/A" and end != "N/A":
                
                fmt = "%H:%M"
                try:
                    start_time = datetime.strptime(start, fmt)
                    end_time = datetime.strptime(end, fmt)
                    if start_time >= end_time:
                        messagebox.showerror("Invalid Time", "Start time must be before end time.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format.")
                    return

            save_adjustment(date_str, child_id, start_combo, end_combo)
            self.display_children_for_day(date)
            adjustment_window.destroy()

        save_button = ttk.Button(container, text="Save", command=validate_and_save)
        save_button.grid(row=5, column=0, pady=20, sticky="n")

    def generate_time_slots(self, start_time="07:30", end_time="18:00", interval=15):

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

    def highlight_weekdays(self, event=None):
        """ Highlight weekdays (Mon-Fri) for the currently viewed month """
        print("Month changed!")
        # Get the first day of the currently displayed month
        current_month = self.calendar.get_displayed_month()  # This returns a tuple like (year, month)
        print(f"The month is: {current_month}")
    
        # Check if current_month is a tuple and format it into 'YYYY-MM' string
        if isinstance(current_month, tuple) and len(current_month) == 2:
            month, year = current_month  # Unpack the tuple
            # Ensure the month is 2 digits, e.g., '03' for March
            current_month_str = f"{year:04d}-{month:02d}"  # Format as 'YYYY-MM'
        else:
            # Handle error if the current_month is not a tuple or has invalid data
            raise ValueError("Expected current_month to be a tuple with (year, month)")
    
        # Get the first day of the current month (ensure the date string is 'YYYY-MM-01')
        first_day = datetime.strptime(current_month_str + "-01", "%Y-%m-%d")  # Creating a datetime object for the first day
        print(f"First day is: {first_day.strftime('%Y-%m-%d')}")
        

        # Get all the days in the current month
        total_days_in_month = self.get_days_in_month(first_day)

        # Clear any existing events before applying new ones
        self.calendar.calevent_remove("weekday")
        self.calendar.calevent_remove("weekend")
 
        # Try and delete existing tags so calendar doesnt keep previous months coloring
        try:
            self.calendar.tag_delete("weekday")
            self.calendar.tag_delete("weekend")
            print("Deleted exisiting tags")
        except:
            print("No tags currently present")

        self.disabled_weekends = set()  # Track disabled weekend dates

        for day in total_days_in_month:

            day_date = day.date()

            if day.weekday() < 5:  # Monday to Friday
                self.calendar.calevent_create(day_date, f"{day.day}", "weekday")  
                self.calendar.tag_config("weekday", background="lightgreen", foreground="black") 
            else:  # Weekend days (Saturday and Sunday)
                self.calendar.calevent_create(day_date, f"{day.day}", "weekend")
                self.calendar.tag_config("weekend", background="pink", foreground="black")
                self.disabled_weekends.add(day_date)

        self.current_hovered_day = None

    def get_days_in_month(self, date):
        """ Get all the days in the month for the given date """
        # Get the last day of the current month
        next_month = date.replace(day=28) + timedelta(days=4)  # Go to the next month
        last_day_of_month = next_month - timedelta(days=next_month.day)  # Get the last day of the month

        # Generate all days in the month
        days_in_month = [date.replace(day=d) for d in range(1, last_day_of_month.day + 1)]
        return days_in_month

    def create_clock(self, parent):
        """ Create and display a label that shows real-time clock """
        self.time_label = tk.Label(parent, font=("Helvetica", 20), bg="#d9f1fb")
        self.time_label.grid(pady=10, sticky="ns")

        # Update the clock every second
        self.update_clock()

    def update_clock(self):
        """ Update the clock to show the current time """
        current_time = time.strftime("%H:%M")  # Get current time
        self.time_label.config(text=current_time)  # Update label with current time

        # Call this function every 1000 milliseconds (1 second)
        self.after(1000, self.update_clock)

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

if __name__ == "__main__":
    app = Registers()
    app.mainloop()