import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import time
from datetime import datetime, timedelta

DEFAULT_MENUS = {
        "monday": ("Beef and Carrot Puree", "Apple Compote", "Vegetable Soup", "Sautéed Beef and Potatoes", "Natural Yogurt"),
        "tuesday": ("Chicken and Broccoli Puree", "Fromage Blanc", "Pasta Salad", "Roasted Chicken and Broccoli", "Cheese and Crackers"),
        "wednesday": ("Lentil and Celeri Puree", "Banana Compote", "Cherry Tomatoes", "Lentil and Vegetable Curry", "Clementines"),
        "thursday": ("Haddock and Green Bean Puree", "Pear Compote", "Green Bean Salad", "Haddock and Sweet Potato", "Rice Pudding"),
        "friday": ("Pork and Cauliflower Puree", "Natural Yogurt", "Beetroot Salad", "Roasted Pork and Cauliflower", "Gateau au Chocolat")
}

def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def search_existing_menu(date):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menus WHERE date = ?', (date,))
        return cursor.fetchone()

def create_new_menu(date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menus (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert)
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert))
        conn.commit()

def update_menu(menu_id, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE menus
            SET baby_main = ?, baby_dessert = ?, grands_starter = ?, grands_main = ?, grands_dessert = ?
            WHERE menu_id = ?''',
            (baby_main, baby_dessert, grands_starter, grands_main, grands_dessert, menu_id))
        conn.commit()



class Menus(tk.Toplevel):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Menus...")
        self.title("Current Pupils")
        self.geometry("1400x900")
        self.deiconify()
        self.lift()
        self.create_menus_window()

        today = datetime.today()
        self.calendar.selection_set(today)
        self.display_menu_for_day(today)
        

    def create_menus_window(self):
        # Set up the grid layout with three columns
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        # Add the sidebar
        self.create_global_sidebar()
        
        # Column 2 (Middle): Register list and day title
        self.menus_frame = ttk.Frame(self)
        self.menus_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 0))

        # Date selection and calendar in column 3
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

        # Ensure the calendar_frame also expands
        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(0, weight=1)

        # Calendar widget for date selection
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.calendar.bind("<<CalendarMonthChanged>>", self.highlight_weekdays)

        self.highlight_weekdays()

        select_button = ttk.Button(self.calendar_frame, text="Select", command=self.show_menu_for_day)
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

    def show_menu_for_day(self):
        selected_date_str = self.calendar.get_date()
        
        try:
            # Convert the selected date into a datetime object
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return
        
        # Fetch children data and their registers for the selected date
        self.display_menu_for_day(selected_date)

    def display_menu_for_day(self, selected_date):
        for widget in self.menus_frame.winfo_children():
            widget.destroy()  # Clear previous content

        date_str = selected_date.strftime("%Y-%m-%d")
        menu = search_existing_menu(date_str)

        ttk.Label(self.menus_frame, text=f"Menu for {date_str}", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        labels = ["Baby Main", "Baby Dessert", "Grands Starter", "Grands Main", "Grands Dessert"]
        entries = []

        for idx, label in enumerate(labels):
            ttk.Label(self.menus_frame, text=label).grid(row=idx+1, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(self.menus_frame, width=40)
            entry.grid(row=idx+1, column=1, padx=5, pady=5)
            entries.append(entry)

        if menu:
            print(f"Menu found: {menu}")
            for i, value in enumerate(menu[2:]):  # Skip menu_id and date
                entries[i].insert(0, value)

            def save_edits():
                updated_values = [e.get() for e in entries]
                update_menu(menu[0], *updated_values)
                print("Menu updated.")

            action_btn = ttk.Button(self.menus_frame, text="Save Changes", command=save_edits)

        else:
            print("No menu found. creating default...")

            # Load default values based on the weekday
            weekday = selected_date.strftime("%A").lower()
            defaults = DEFAULT_MENUS.get(weekday, ("", "", "", "", ""))

            for i, value in enumerate(defaults):
                entries[i].insert(0, value)

            new_values = [e.get() for e in entries]
            create_new_menu(date_str, *new_values)
            print("New menu created.")

            menu = search_existing_menu(date_str)

            def save_edits():
                updated_values = [e.get() for e in entries]
                update_menu(menu[0], *updated_values)
                print("Menu updated.")

            action_btn = ttk.Button(self.menus_frame, text="Save Changes", command=save_edits)

        action_btn.grid(row=len(labels)+2, column=0, columnspan=2, pady=20)

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

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

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

if __name__ == "__main__":
    app = Menus()
    app.mainloop() 