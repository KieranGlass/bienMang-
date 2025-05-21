from utils import calendar_utils, clock_utils, navigation_utils
from utils.db_utils import common_db_utils, registers_db_utils

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
            
class Registers(tk.Toplevel):
    
    def __init__(self, parent, root_app, date = None):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent
        print("Initializing Registers...")
        self.title("Registers")
        self.geometry("1400x900")
        self.lift()
        self.create_registers_window()

        if date:
            selected_date = datetime.strptime(date, "%Y-%m-%d")
            self.display_children_for_day(selected_date)
        else:
            self.default_register_for_day()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

    def create_registers_window(self):
        # Set up the grid layout with three columns
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Register list (flexible)
        self.grid_rowconfigure(1, weight=1)  # Let row 1 (calendar) expand vertically

        # Add the sidebar
        self.sidebar_frame = navigation_utils.create_global_sidebar(self)
        
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

        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)

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

        children = common_db_utils.get_all_children()

        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Fetch or create register entries for the selected date
        registers_db_utils.search_existing_register(selected_date_str, children)

        # Configure the grid for the table-like layout
        self.scrollable_register_frame.grid_columnconfigure(0, weight=2, minsize=150)  # Column for name
        self.scrollable_register_frame.grid_columnconfigure(1, weight=1, minsize=100)  # Column for start time
        self.scrollable_register_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Column for end time
        self.scrollable_register_frame.grid_columnconfigure(3, weight=1, minsize=50)  # Column for adjust button
        self.scrollable_register_frame.grid_columnconfigure(4, weight=1, minsize=50)

        name_header = tk.Label(self.scrollable_register_frame, text="Child Name", font=("Arial", 12, "bold"))
        name_header.grid(row=1, column=0, padx=0, sticky="ew")

        start_header = tk.Label(self.scrollable_register_frame, text="Start Time", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="ew")

        end_header = tk.Label(self.scrollable_register_frame, text="End Time", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="ew")

        adjust_header = tk.Label(self.scrollable_register_frame, text="")
        adjust_header.grid(row=1, column=3, padx=10, sticky="ew")

        absent_header = tk.Label(self.scrollable_register_frame, text="")
        absent_header.grid(row=1, column=4, padx=10, sticky="ew")

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
            adjusted_schedule = registers_db_utils.search_adjusted_schedule(selected_date_str, child_id)
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

            absent_button_style = ttk.Style()

            absent_button_style.configure("LightPink.TButton",
                background="#ffb6c1",
                foreground="black",
                borderwidth=1,
                focusthickness=3,
                focuscolor='none')
            
            absent_button_style.map("LightPink.TButton",
                background=[("active", "#ff69b4")]) 

            absent_button = ttk.Button(
                self.scrollable_register_frame,
                text="Absent",
                style="LightPink.TButton",
                
                command=lambda id=child_id, date=selected_date: self.mark_absent(id, date)
            )
            absent_button.grid(row=i, column=4, padx=10, sticky="ew")

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
        time_options = clock_utils.generate_time_slots()
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

            registers_db_utils.save_adjustment(date_str, child_id, start_combo, end_combo)
            self.display_children_for_day(date)
            adjustment_window.destroy()

        def cancel_adjust():
            adjustment_window.destroy()
        
        button_frame = ttk.Frame(container)
        button_frame.grid(row=5, column=0, pady=20, sticky="n")

        cancel_button_style = ttk.Style()
        cancel_button_style.configure(
            "Cancel.TButton",
            background="#f4c2c2",  # Light pink
            foreground="black",
            borderwidth=1
        )
        cancel_button_style.map("Cancel.TButton",
            background=[("active", "#e89cae")]  # Slightly darker pink on hover
        )

        cancel_button = ttk.Button(button_frame, text="Cancel", style="Cancel.TButton", command=cancel_adjust)
        cancel_button.grid(row=0, column=0, padx=(0, 10))

        save_button_style = ttk.Style()
        save_button_style.configure(
            "Save.TButton",
            background="#b6e7a6",  # Light green
            foreground="black",
            borderwidth=1
        )
        save_button_style.map("Save.TButton",
            background=[("active", "#9bd18a")]  # Slightly darker green on hover
        )

        save_button = ttk.Button(button_frame, text="Save", style="Save.TButton", command=validate_and_save)
        save_button.grid(row=0, column=1)

    def mark_absent(self, child_id, date):
        """Set a child's register to 'N/A' for both start and end times."""
        date_str = date.strftime("%Y-%m-%d")
        registers_db_utils.save_adjustment(date_str, child_id, "N/A", "N/A")
        self.display_children_for_day(date)

if __name__ == "__main__":
    app = Registers()
    app.mainloop()