from utils import calendar_utils, clock_utils, navigation_utils
from utils.db_utils import menus_db_utils

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime

class Menus(tk.Toplevel):
    
    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent  # Store the Dashboard instance
        print("Initializing Menus...")
        self.title("Current Pupils")
        self.geometry("1400x900")
        self.lift()
        self.create_menus_window()

        today = datetime.today()
        self.calendar.selection_set(today)
        self.display_menu_for_day(today)

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))
        
    def create_menus_window(self):
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        # Add the sidebar
        self.sidebar_frame = navigation_utils.create_global_sidebar(self)
        
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

         # Bind the calendar selection event
        self.calendar.bind(
            "<<CalendarSelected>>",
            lambda event: calendar_utils.on_day_selected_for_button(
            self.calendar,
            self.disabled_weekends
            )
        )       

        self.calendar.bind(
            "<<CalendarMonthChanged>>",
            lambda event: calendar_utils.on_month_change(
            self.calendar,
            self.calendar.get_displayed_month,
            lambda val: setattr(self, "disabled_weekends", val)
            )
        )
        
        calendar_utils.highlight_weekdays(self.calendar, self.calendar.get_displayed_month)
        self.disabled_weekends = calendar_utils.highlight_weekdays(self.calendar, self.calendar.get_displayed_month)

        select_button = ttk.Button(self.calendar_frame, text="Select", style="MenuSelect.TButton", command=self.show_menu_for_day)
        select_button.grid(pady=10)

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
        menu = menus_db_utils.search_existing_menu(date_str)

        ttk.Label(self.menus_frame, text=f"{date_str}", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 20)
        )

        # Create a labeled frame for better grouping
        menu_frame = ttk.LabelFrame(self.menus_frame, text="Meal Details", padding=20)
        menu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        labels = ["Baby Main", "Baby Dessert", "Grands Starter", "Grands Main", "Grands Dessert"]
        entries = []

        for idx, label in enumerate(labels):
            ttk.Label(menu_frame, text=label + ":", font=("Arial", 12)).grid(
                row=idx, column=0, sticky="e", padx=10, pady=8
            )
            entry = ttk.Entry(menu_frame, width=50)
            entry.grid(row=idx, column=1, sticky="w", padx=10, pady=8)
            entries.append(entry)

        if menu:
            print(f"Menu found: {menu}")
            for i, value in enumerate(menu[2:]):
                entries[i].insert(0, value)

            def save_edits():
                updated_values = [e.get() for e in entries]
                menus_db_utils.update_menu(menu[0], *updated_values)
                print("Menu updated.")

            action_btn = ttk.Button(self.menus_frame, text="Save Changes", command=save_edits)
        else:
            print("No menu found. Creating default...")

            weekday = selected_date.strftime("%A").lower()
            defaults = menus_db_utils.DEFAULT_MENUS.get(weekday, ("", "", "", "", ""))

            for i, value in enumerate(defaults):
                entries[i].insert(0, value)

            new_values = [e.get() for e in entries]
            menus_db_utils.create_new_menu(date_str, *new_values)
            print("New menu created.")

            menu = menus_db_utils.search_existing_menu(date_str)

            def save_edits():
                updated_values = [e.get() for e in entries]
                menus_db_utils.update_menu(menu[0], *updated_values)
                print("Menu updated.")

            action_btn = ttk.Button(self.menus_frame, text="Save Changes", command=save_edits)

        action_btn.grid(row=2, column=0, columnspan=2, pady=20)

        # Add styling
        style = ttk.Style()
        style.configure("TLabelFrame.Label", font=("Arial", 14, "bold"))
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=6)

if __name__ == "__main__":
    app = Menus()
    app.mainloop() 