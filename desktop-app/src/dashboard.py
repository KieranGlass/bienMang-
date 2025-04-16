import os
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import time
from datetime import datetime, timedelta

from login import LoginWindow
from children import Children
from menus import Menus
from reports import Reports
from registers import Registers
from today import Today
from admin import Setting
from day_info import DayInfoPage


# TODO - When database entries are refused as duplicates, the system must not use up the ID numbers

 
class Dashboard(tk.Tk):
    
    def __init__(self):
        super().__init__()
        print("Initializing MainWindow...")
        self.title("Bien Manger")
        self.geometry("1400x900")
        self.configure(bg="#d9f1fb")
        self.deiconify()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.lift()

        self.create_dashboard()      
    

    def create_dashboard(self):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Resources path: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')}")

        self.create_global_sidebar()
    
        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

         # Configure grid weights for the dashboard frame to make it responsive
        self.grid_rowconfigure(0, weight=1, minsize=50)  # Makes the row with the dashboard frame expand
        self.grid_columnconfigure(1, weight=1, minsize=100)
    
        # Create calendar widget
        self.create_calendar(dashboard_frame)
        # Create clock label
        self.create_clock(self.sidebar_frame)

    
       

    def create_global_sidebar(self):
        """ Create the sidebar with tabs """
        # Sidebar container (frame)
        self.sidebar_frame = ttk.Frame(self, relief="raised")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsw")

        # Tab buttons
        self.create_sidebar_tab(self.sidebar_frame, "Children", self.show_children, 0)
        self.create_sidebar_tab(self.sidebar_frame, "Registers", self.show_registers, 1)
        self.create_sidebar_tab(self.sidebar_frame, "Menus", self.show_menus, 2)
        self.create_sidebar_tab(self.sidebar_frame, "Reports", self.show_reports, 3)
        self.create_sidebar_tab(self.sidebar_frame, "Settings", self.show_settings, 4)
        self.create_sidebar_tab(self.sidebar_frame, "Tab 5", self.show_children, 5)
        self.create_sidebar_tab(self.sidebar_frame, "Log Out", self.log_out, 6)

    def create_sidebar_tab(self, sidebar_frame, label, command, row):
        """ Helper function to create a tab (button) in the sidebar """
        tab_button = ttk.Button(sidebar_frame, text=label, command=command)
        tab_button.grid(row=row, column=0, padx=10, pady=10, sticky="w")

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

    def create_calendar(self, parent):
        """ Create and display the calendar widget """
        self.calendar = Calendar(parent, selectmode="day", date_pattern="y-mm-dd")
        self.calendar.grid(row=0, column=0, sticky="nsew")

        # Set the calendar to take up all the available space in the grid cell
        parent.grid_rowconfigure(0, weight=1)  # Make the row with the calendar expand
        parent.grid_columnconfigure(0, weight=1)

        # Display the current date on the calendar
        # self.calendar.set_date(datetime.today())

        # Bind the calendar's day selection to a function
        self.calendar.bind("<<CalendarSelected>>", self.on_day_selected)
        # Bind the month change event to highlight the weekdays again
        self.calendar.bind("<<CalendarMonthChanged>>", self.highlight_weekdays)

        self.highlight_weekdays()

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
        total_days_in_month = self._get_days_in_month(first_day)

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

    def _get_days_in_month(self, date):
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

    def on_day_selected(self, event):
        """ Handle when a day is selected on the calendar """
        selected_date_str = self.calendar.get_date()  # Get the selected date in 'yyyy-mm-dd' format
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

        if selected_date in self.disabled_weekends:
            print(f"Weekend selected: {selected_date}. Selection disabled.")
            self.calendar.selection_clear()  # Deselect the date
            return  # Stop here, don’t open DayInfoPage

        print("Opening day info page for " + selected_date_str)
        # Open a new window (DayInfoPage) showing details for the selected date
        # Pass the selected date to DayInfoPage

        day_info_window = DayInfoPage(self, selected_date_str)
        day_info_window.mainloop()

    def show_today(self):
        print("Showing today")

        self.withdraw()
        
        today_window = Today(self)  
        today_window.mainloop()  
            
    def show_children(self):
        print("Showing children")

        self.withdraw()

        children_window = Children(self)  # Initialize the Children window class
        children_window.mainloop()  # Start the Tkinter event loop for the new window
           
    def show_registers(self):
        print("Showing registers")

        self.withdraw()
        
        registers_window = Registers(self)  
        registers_window.mainloop() 
            
    def show_menus(self):
        print("Showing menus")

        self.withdraw()
        
        menus_window = Menus(self)  
        menus_window.mainloop() 
            
    def show_reports(self):
        print("Showing reports")

        self.withdraw()
        
        reports_window = Reports(self)  
        reports_window.mainloop() 
            
    def show_settings(self):
        print("Showing settings")

        self.withdraw()
        
        settings_window = Setting(self)  
        settings_window.mainloop() 

    def log_out(self):
        return print("Log Out")  

def main():
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()