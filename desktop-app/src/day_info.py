import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
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

def get_menu_by_date(selected_date):
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT baby_main, baby_dessert, grands_starter, grands_main, grands_dessert FROM menus WHERE date = ?', (selected_date,))
        menu = cursor.fetchone()
    return menu

def create_new_menu(date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menus (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert)
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert))
        conn.commit()

class DayInfoPage(tk.Toplevel):
    def __init__(self, parent, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date
        self.title(f"Details for {self.selected_date}")
        self.geometry("1400x900")

        title_date = self.format_title_date(selected_date)
        
        # Create a label for the day’s date
        self.date_label = tk.Label(self, text=title_date, font=("Helvetica", 16))
        self.date_label.grid(pady=10)

        # Menu Label
        self.menu_label = tk.Label(self, text="Menus", font=("Helvetica", 14, "bold"))
        self.menu_label.grid(row=1, column=0, pady=5, sticky="w", padx=10)

        # Baby Menu Section
        self.baby_menu_frame = tk.LabelFrame(self, text="Baby Menu", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        self.baby_menu_frame.grid(row=2, column=0, sticky="new", padx=10)

        # Grands Menu Section
        self.grands_menu_frame = tk.LabelFrame(self, text="Grands Menu", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        self.grands_menu_frame.grid(row=3, column=0, sticky="new", padx=10)    

        self.register_label = tk.Label(self, text="Register: ", font=("Helvetica", 12))
        self.register_label.grid(row=1, column=1, pady=5,  padx=10, sticky="w")

        self.register_frame = ttk.Frame(self)
        self.register_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        self.display_register(selected_date)
        self.display_menu(selected_date)

        # Back button to go back to the calendar dashboard
        self.back_button = tk.Button(self, text="Close", command=self.go_back)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Configure the grid layout of the window to be responsive
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)  # More weight for the register frame
        self.grid_rowconfigure(2, weight=1)  # Let the main content row expand
        self.grid_rowconfigure(3, weight=1)

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
        name_header.grid(row=1, column=0, padx=10, sticky="nsw")

        start_header = tk.Label(self.register_frame, text="Start Time", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="nsew")

        end_header = tk.Label(self.register_frame, text="End Time", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="nsew")

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

            if adjusted_start != "N/A":

                row_frame = tk.Frame(self.register_frame, bg="#f9f9f9", highlightbackground="#ccc", highlightthickness=1)
                row_frame.grid(row=i, column=0, columnspan=3, sticky="nsew", pady=2)
                row_frame.grid_columnconfigure(0, weight=2)
                row_frame.grid_columnconfigure(1, weight=1)
                row_frame.grid_columnconfigure(2, weight=1)

                # Hover effects
                def on_enter(e, frame=row_frame):
                    frame.config(bg="#e0f7fa")

                def on_leave(e, frame=row_frame):
                    frame.config(bg="#f9f9f9")

                row_frame.bind("<Enter>", on_enter)
                row_frame.bind("<Leave>", on_leave)

                # Click binding
                row_frame.bind("<Button-1>", lambda e, cid=child_id: self.open_child_day_info(cid, selected_date))

                # Child info
                tk.Label(row_frame, text=f"{first_name} {last_name}", width=25, bg="#f9f9f9").grid(row=0, column=0, sticky="w", padx=10, pady=5)
                tk.Label(row_frame, text=adjusted_start, width=10, bg="#f9f9f9").grid(row=0, column=1, sticky="ew", padx=10)
                tk.Label(row_frame, text=adjusted_end, width=10, bg="#f9f9f9").grid(row=0, column=2, sticky="ew", padx=10)

            # Increment the row index for the next child
            i += 1

    def display_menu(self, selected_date):
        menu = get_menu_by_date(selected_date)
        selected_date_datetime = datetime.strptime(selected_date, "%Y-%m-%d")
        date_str = selected_date_datetime.strftime("%Y-%m-%d")

        if menu:
            baby_main, baby_dessert, grands_starter, grands_main, grands_dessert = menu

            # Clear previous content (if reloading)
            for widget in self.baby_menu_frame.winfo_children():
                widget.destroy()
            for widget in self.grands_menu_frame.winfo_children():
                widget.destroy()

            # Baby Menu (Grid layout inside frame)
            tk.Label(self.baby_menu_frame, text="Main:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.baby_menu_frame, text=baby_main, font=("Helvetica", 11)).grid(row=0, column=1, sticky="w", padx=5)

            tk.Label(self.baby_menu_frame, text="Dessert:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.baby_menu_frame, text=baby_dessert, font=("Helvetica", 11)).grid(row=1, column=1, sticky="w", padx=5)

            # Grands Menu
            tk.Label(self.grands_menu_frame, text="Starter:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_starter, font=("Helvetica", 11)).grid(row=0, column=1, sticky="w", padx=5)

            tk.Label(self.grands_menu_frame, text="Main:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_main, font=("Helvetica", 11)).grid(row=1, column=1, sticky="w", padx=5)

            tk.Label(self.grands_menu_frame, text="Dessert:", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_dessert, font=("Helvetica", 11)).grid(row=2, column=1, sticky="w", padx=5)

        else:
            
            print("No menu found. creating default...")

            # Load default values based on the weekday
            weekday = selected_date_datetime.strftime("%A").lower()
            defaults = DEFAULT_MENUS.get(weekday, ("", "", "", "", ""))

            create_new_menu(date_str, *defaults)
            print("New menu created.")

            self.display_menu(selected_date)

    def open_child_day_info(self, child_id, selected_date):
        
        print(f"Clicked on child {child_id} for date {selected_date}")
    
        
        top = tk.Toplevel(self)
        top.title("Child Day Info")
        top.geometry("400x300")

        tk.Label(top, text=f"Child ID: {child_id}\nDate: {selected_date}", font=("Arial", 14)).pack(pady=20)
  
    def format_title_date(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return dt.strftime(f"%A {day}{suffix} %B")

    def go_back(self):
        """ Closes this window and brings the user back to the calendar dashboard """
        self.destroy() 