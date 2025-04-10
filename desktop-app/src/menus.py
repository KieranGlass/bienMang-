import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta

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
            INSERT INTO menus (date, baby_main, baby_dessert, grands_main, grands_starter, grands_dessert)
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert))
        conn.commit()

def update_menu(menu_id, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE menus
            SET baby_main = ?, baby_dessert = ?, grands_main = ?, grands_starter = ?, grands_dessert = ?
            WHERE menu_id = ?''',
            (baby_main, baby_dessert, grands_starter, grands_main, grands_dessert, menu_id))
        conn.commit()



class Menus(tk.Tk):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Menus...")
        self.title("Current Pupils")
        self.geometry("1400x900")
        self.deiconify()
        self.lift()
        self.create_menus_window()      
        

    def create_menus_window(self):
        # Set up the grid layout with three columns
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
        self.grid_columnconfigure(2, weight=1, minsize=200)  # Calendar (flexible)

        # Add the sidebar
        self.create_global_sidebar()
        
        # Column 2 (Middle): Register list and day title
        self.menus_frame = ttk.Frame(self)
        self.menus_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Date selection and calendar in column 3
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)

        # Calendar widget for date selection
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(pady=10)

        select_button = ttk.Button(self.calendar_frame, text="Select", command=self.show_menu_for_day)
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
            # Fill the form with existing menu
            for i, value in enumerate(menu[2:]):  # Skip menu_id and date
                entries[i].insert(0, value)

            def save_edits():
                updated_values = [e.get() for e in entries]
                update_menu(menu[0], *updated_values)
                print("Menu updated.")

            action_btn = ttk.Button(self.menus_frame, text="Save Changes", command=save_edits)

        else:
            print("No menu found. Ready to create one.")

            def create_menu():
                new_values = [e.get() for e in entries]
                create_new_menu(date_str, *new_values)
                print("New menu created.")

            action_btn = ttk.Button(self.menus_frame, text="Create Menu", command=create_menu)

        action_btn.grid(row=len(labels)+2, column=0, columnspan=2, pady=20)

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

if __name__ == "__main__":
    app = Menus()
    app.mainloop()  # Starts the Tkinter event loop