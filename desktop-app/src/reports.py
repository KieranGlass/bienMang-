import sqlite3
from contextlib import closing

from utils import calendar_utils

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import time
from datetime import datetime, timedelta

class Reports(tk.Toplevel):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Reports...")
        self.title("Reports")
        self.geometry("1400x900")
        self.lift()
        self.create_reports_window()

        self.protocol("WM_DELETE_WINDOW", self.on_close)    

    def create_reports_window(self):

        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        self.create_global_sidebar()
        
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
        tab_button1 = ttk.Button(frame, text=text, command=command)
        tab_button1.grid(row=row, column=0, padx=10, pady=5, sticky="w")

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
        tab_button1.configure(style="Custom.TButton")

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
        self.dashboard.deiconify()

    def on_close(self):
        self.destroy()
        self.dashboard.deiconify()

if __name__ == "__main__":
    app = Reports()
    app.mainloop()  # Starts the Tkinter event loop