import os
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import date

from utils import calendar_utils, navigation_utils, styles

from login import LoginWindow
from day_info import DayInfoPage


# TODO - When database entries are refused as duplicates, the system must not use up the ID numbers

class Dashboard(tk.Toplevel):
    
    def __init__(self, parent, root_app):
        super().__init__(parent)
        print("Initializing MainWindow...")
        self.root_app = root_app
        self.parent = parent
        self.title("Bien Manger")
        self.geometry("1400x900")
        self.configure(bg="#d9f1fb")
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.lift()

        self.create_dashboard()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))
    

    def create_dashboard(self):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Resources path: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')}")

        self.sidebar_frame = navigation_utils.create_global_sidebar(self)
    
        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self, style="CalendarBg.TFrame")
        dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

         # Configure grid weights for the dashboard frame to make it responsive
        self.grid_rowconfigure(0, weight=1, minsize=50)  # Makes the row with the dashboard frame expand
        self.grid_columnconfigure(1, weight=1, minsize=100)
    
        # Create calendar widget
        self.create_calendar(dashboard_frame)

    def create_calendar(self, parent):
        """ Create and display the calendar widget """
        self.calendar = Calendar(parent, selectmode="day", date_pattern="y-mm-dd", maxdate=date.today(), background="#003366")
        self.calendar.grid(row=0, column=0, sticky="nsew")

        # Set the calendar to take up all the available space in the grid cell
        parent.grid_rowconfigure(0, weight=1)  # Make the row with the calendar expand
        parent.grid_columnconfigure(0, weight=1)

        # Bind the calendar selection event
        self.calendar.bind(
            "<<CalendarSelected>>",
            lambda event: calendar_utils.on_day_selected(
            self.calendar,
            self.disabled_weekends,
            lambda date_str: calendar_utils.open_day_info(self, self.root_app, date_str, DayInfoPage)
            )
        )
        # Bind the month change event to highlight the weekdays again
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

def main():
    root = tk.Tk()
    styles.apply_styles()
    root.withdraw()
    login_window = LoginWindow(root)
    login_window.mainloop()

if __name__ == "__main__":
    main()