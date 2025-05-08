import sqlite3
from contextlib import closing

from utils import calendar_utils, clock_utils, navigation_utils

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

class Reports(tk.Toplevel):
    
    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent 
        print("Initializing Reports...")
        self.title("Reports")
        self.geometry("1400x900")
        self.lift()
        self.create_reports_window()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))    

    def create_reports_window(self):

        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        self.sidebar_frame = navigation_utils.create_global_sidebar(self)
        
        self.reports_frame = ttk.Frame(self)
        self.reports_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 0))

        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(0, weight=1)

        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

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

        select_button = ttk.Button(self.calendar_frame, text="Select", style="Select.TButton")
        select_button.grid(pady=10)

        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)

    def go_home(self):
        self.destroy()
        self.dashboard.deiconify()

    def on_close(self):
        self.destroy()
        self.dashboard.deiconify()

if __name__ == "__main__":
    app = Reports()
    app.mainloop()  # Starts the Tkinter event loop