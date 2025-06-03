import tkinter as tk
from tkinter import ttk
from datetime import datetime
from child_day_info import ChildDayInfoPage


from utils import navigation_utils
from utils.db_utils import common_db_utils, registers_db_utils, menus_db_utils

class DayInfoPage(tk.Toplevel):
    def __init__(self, parent, root_app, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date
        self.root_app = root_app
        self.configure(bg="#d9f1fb")
        title_date = self.format_title_date(selected_date)
        self.title(f"{title_date}")
        self.geometry("1200x800")

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

        self.register_label = tk.Label(self, text="Scheduled Register", bg="#d9f1fb", font=("Helvetica", 14, "bold"))
        self.register_label.grid(row=0, column=0, pady=5,  padx=10, sticky="w")

        self.register_frame = ttk.Frame(self, style="dayInfoBackground.TFrame")
        self.register_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=20)
        
        # Menu Label 
        self.menu_label = tk.Label(self, text="Menus", font=("Arial", 14, "bold"), bg="#d9f1fb")
        self.menu_label.grid(row=3, column=0, pady=5, sticky="w", padx=10)

        # Baby Menu Section
        self.baby_menu_frame = tk.LabelFrame(self, text="Baby Menu", bg="#d9f1fb", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.baby_menu_frame.grid(row=4, column=0, sticky="new", padx=10)

        # Grands Menu Section
        self.grands_menu_frame = tk.LabelFrame(self, text="Grands Menu", bg="#d9f1fb", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.grands_menu_frame.grid(row=5, column=0, sticky="new", padx=10)    

        self.display_register(selected_date)
        self.display_menu(selected_date)

        self.button_frame = ttk.Frame(self, style="Register.TFrame")
        self.button_frame.grid(row=6, column=0, sticky="nsew")

        # Back button to go back to the calendar dashboard
        self.back_button = ttk.Button(self.button_frame, text="Close", style="dayInfoClose.TButton", command=lambda: navigation_utils.on_close(self))
        self.back_button.grid(row=0, column=0, pady=10, padx=10)

        # Configure the grid layout of the window to be responsive
        self.grid_columnconfigure(0, weight=1)  

    def display_register(self, selected_date):
        
        children = common_db_utils.get_all_children()
        print(f"{selected_date}")

        # Fetch or create register entries for the selected date
        registers_db_utils.search_existing_register(selected_date, children)

        # Configure the grid for the table-like layout
        self.register_frame.grid_columnconfigure(0, weight=2, minsize=150)  # Column for name
        self.register_frame.grid_columnconfigure(1, weight=1, minsize=100)  # Column for start time
        self.register_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Column for finish time
        self.register_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Column for status

        name_header = tk.Label(self.register_frame, text="Child Name", bg="#003366", fg="white", font=("Arial", 12, "bold"))
        name_header.grid(row=1, column=0, padx=10, sticky="nsew")

        start_header = tk.Label(self.register_frame, text="Start", bg="#003366", fg="white", font=("Arial", 12, "bold"))
        start_header.grid(row=1, column=1, padx=10, sticky="nsew")

        end_header = tk.Label(self.register_frame, text="Finish", bg="#003366", fg="white", font=("Arial", 12, "bold"))
        end_header.grid(row=1, column=2, padx=10, sticky="nsew")

        info_header = tk.Label(self.register_frame, text="Status", bg="#003366", fg="white", font=("Arial", 12, "bold"))
        info_header.grid(row=1, column=3, padx=10, sticky="nsew")

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
            adjusted_schedule = registers_db_utils.search_adjusted_schedule(selected_date, child_id)
            if adjusted_schedule:
                adjusted_start, adjusted_end = adjusted_schedule
            else:
                adjusted_start, adjusted_end = arrival_time, finish_time

            if adjusted_start != "N/A":

                row_frame = tk.Frame(self.register_frame, bg="#f9f9f9", highlightbackground="#ccc", highlightthickness=1)
                row_frame.grid(row=i, column=0, columnspan=4, sticky="nsew", pady=2)
                row_frame.grid_columnconfigure(0, weight=2)
                row_frame.grid_columnconfigure(1, weight=1)
                row_frame.grid_columnconfigure(2, weight=1)
                row_frame.grid_columnconfigure(3, weight=1)

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
                tk.Label(row_frame, text=f"{first_name} {last_name}", width=20, bg="#f9f9f9").grid(row=0, column=0, sticky="ew", padx=10, pady=5)
                tk.Label(row_frame, text=adjusted_start, width=10, bg="#f9f9f9").grid(row=0, column=1, sticky="ew", padx=10)
                tk.Label(row_frame, text=adjusted_end, width=10, bg="#f9f9f9").grid(row=0, column=2, sticky="ew", padx=10)
                status = registers_db_utils.get_completed_status(selected_date, child_id)
                print(f"{status}")
                if status and status[0] == 1:
                    status_text = "Complete"
                    status_color = "#4CAF50"
                else:
                    status_text = "Incomplete"
                    status_color = "#A52A2A"

                tk.Label(row_frame, text=status_text, width=10, bg="#f9f9f9", fg=status_color).grid(row=0, column=3, sticky="ew", padx=10)

            # Increment the row index for the next child
            i += 1

    def display_menu(self, selected_date):
        menu = menus_db_utils.get_menu_by_date(selected_date)
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
            tk.Label(self.baby_menu_frame, text="Main:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.baby_menu_frame, text=baby_main, bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w", padx=5)

            tk.Label(self.baby_menu_frame, text="Dessert:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.baby_menu_frame, text=baby_dessert, bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=1, column=1, sticky="w", padx=5)

            # Grands Menu
            tk.Label(self.grands_menu_frame, text="Starter:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_starter, bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w", padx=5)

            tk.Label(self.grands_menu_frame, text="Main:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_main, bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=1, column=1, sticky="w", padx=5)

            tk.Label(self.grands_menu_frame, text="Dessert:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=2)
            tk.Label(self.grands_menu_frame, text=grands_dessert, bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=2, column=1, sticky="w", padx=5)

        else:
            
            print("No menu found. creating default...")

            # Load default values based on the weekday
            weekday = selected_date_datetime.strftime("%A").lower()
            defaults = menus_db_utils.DEFAULT_MENUS.get(weekday, ("", "", "", "", ""))

            menus_db_utils.create_new_menu(date_str, *defaults)
            print("New menu created.")

            self.display_menu(selected_date)
 
    def open_child_day_info(self, child_id, selected_date):
        """Open the child day info page."""
        print(f"Clicked on child {child_id} for date {selected_date}")
    
        # Create the child window
        child_day_info_window = ChildDayInfoPage(self, child_id, selected_date)
        child_day_info_window.mainloop()
  
    def format_title_date(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return dt.strftime(f"%A {day}{suffix} %B")
    
    def refresh_register(self, selected_date):
        """Refresh the register display."""

        # Re-fetch and display the register for the selected date
        self.display_register(selected_date)