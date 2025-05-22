from utils import calendar_utils, clock_utils, navigation_utils
from utils.db_utils import children_db_utils, common_db_utils, child_day_info_utils

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
        # Grid configuration
        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Main content
        self.grid_rowconfigure(1, weight=1)  # Calendar expands

        # Sidebar
        self.sidebar_frame = navigation_utils.create_global_sidebar(self)

        # Reports Frame
        self.reports_frame = ttk.Frame(self)
        self.reports_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 0))
        self.reports_frame.grid_columnconfigure(0, weight=1)
        self.reports_frame.grid_rowconfigure(1, weight=1)

        # === Report Controls ===
        controls_frame = ttk.Frame(self.reports_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.report_type_var = tk.StringVar()
        report_type_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.report_type_var,
            values=["Attendance", "Meals", "Sleep", "Toileting", "Comments"],
            state="readonly"
        )
        report_type_combo.grid(row=0, column=1, padx=(0, 10), sticky="w")
        report_type_combo.current(0)

        generate_button = ttk.Button(controls_frame, text="Generate", command=self.generate_report)
        generate_button.grid(row=0, column=2, padx=10, sticky="w")

        export_button = ttk.Button(controls_frame, text="Export", command=self.export_report)
        export_button.grid(row=0, column=3, sticky="e")

        # === Report Table ===
        self.report_table = ttk.Treeview(self.reports_frame, columns=("Name", "Arrival", "Departure", "Meal", "Sleep", "Poop", "Comments"), show='headings')
        self.report_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        for col in self.report_table["columns"]:
            self.report_table.heading(col, text=col)

        # Calendar Frame
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(0, weight=1)

        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

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

        # Select Button (optional trigger)
        select_button_style = ttk.Style()
        select_button_style.configure(
            "Select.TButton",
            background="#add8e6",
            foreground="black",
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
        )

        select_button_style.map("Select.TButton", background=[("active", "#87ceeb")])

        select_button = ttk.Button(self.calendar_frame, text="Select", style="Select.TButton")
        select_button.grid(row=1, column=0, pady=10)

        # Clock
        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)


    def generate_report(self):

        for row in self.report_table.get_children():
            self.report_table.delete(row)

        selected_date = self.calendar.get_date()
        report_type = self.report_type_var.get()

        children = common_db_utils.get_all_children()

        for child in children:
            child_id = child[0]
            fname = child[1]
            lname = child[3]
            full_name = f"{fname} {lname}"

            day_data = child_day_info_utils.get_day_info_by_date(child_id, selected_date)
            if not day_data:
                continue

            if report_type == "Attendance":
                row = (full_name, day_data.get("actual_arrival", "-"), day_data.get("actual_finish", "-"), "", "", "", "")
            elif report_type == "Meals":
                main = day_data.get("main", 3)
                dessert = day_data.get("dessert", 3)
                meal_summary = f"Main: {main}, Dessert: {dessert}"
                row = (full_name, "", "", meal_summary, "", "", "")
            elif report_type == "Sleep":
                row = (full_name, "", "", "", day_data.get("sleep_duration", "-"), "", "")
            elif report_type == "Toileting":
                pooped = "Yes" if day_data.get("pooped") else "No"
                count = day_data.get("poop_count", 0)
                poop_summary = f"{pooped} ({count})"
                row = (full_name, "", "", "", "", poop_summary, "")
            elif report_type == "Comments":
                comments = day_data.get("comments", "").strip()
                row = (full_name, "", "", "", "", "", comments[:50])
            else:
                row = (full_name, "-", "-", "-", "-", "-", "-")

            self.report_table.insert("", "end", values=row)

    def export_report(self):
        import csv
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.report_table["columns"])
                for row_id in self.report_table.get_children():
                    row = self.report_table.item(row_id)["values"]
                    writer.writerow(row)

if __name__ == "__main__":
    app = Reports()
    app.mainloop()  # Starts the Tkinter event loop