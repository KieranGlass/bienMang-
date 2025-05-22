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
            values=[
                "All Data (Day)",
                "All Data (Week)",
                "All Data (Month)",
                "Meals (Week)",
                "Meals (Month)",
                "Sleep (Week)",
                "Sleep (Month)",
                "Toileting (Week)",
                "Toileting (Month)",
                "Comments (Week)",
                "Comments (Month)"
            ],
            state="readonly",
            width=25
        )
        report_type_combo.grid(row=0, column=1, padx=(0, 10), sticky="w")
        report_type_combo.current(0)  # Default: "All Data (Day)")

        generate_button = ttk.Button(controls_frame, text="Generate", command=self.generate_report)
        generate_button.grid(row=0, column=2, padx=10)

        self.submit_button = tk.Button(controls_frame, text="Submit Reports", command=self.submit_reports)
        self.submit_button.grid(row=0, column=3, pady=10, padx=10)

        self.publish_button = tk.Button(controls_frame, text="Publish to Parents", command=self.submit_reports)
        self.publish_button.grid(row=0, column=4, pady=10, padx=10)

        export_button = ttk.Button(controls_frame, text="Export", command=self.export_report)
        export_button.grid(row=0, column=5)

        # === Report Table ===
        default_columns = (
            "Date", "Child", "Arrival", "Departure",
            "Main", "Dessert", "Sleep", "Pooped", "Poop Count", "Comments"
        )
        self.report_table = ttk.Treeview(
            self.reports_frame,
            columns=default_columns,
            show='headings'
        )
        self.report_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        for col in default_columns:
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

        self.report_type_var.set("All Data (Day)")
        self.generate_report()


    def generate_report(self):

        # Clear existing table data
        self.report_table.delete(*self.report_table.get_children())

        # Get selected report type and date
        report_type = self.report_type_var.get()
        selected_date = self.calendar.get_date()

        # Determine date range
        if "Week" in report_type:
            date_range = calendar_utils.get_week_dates(selected_date)
        elif "Month" in report_type:
            date_range = calendar_utils.get_month_dates(selected_date)
        else:  # "Day"
            date_range = [selected_date]

        # Set up dynamic columns
        if report_type.startswith("All Data"):
            self.report_table["columns"] = (
                "Date", "Child", "Arrival", "Departure",
                "Main", "Dessert", "Sleep", "Pooped", "Poop Count", "Comments"
            )
        elif report_type.startswith("Meals"):
            self.report_table["columns"] = ("Date", "Child", "Main", "Dessert")
        elif report_type.startswith("Sleep"):
            self.report_table["columns"] = ("Date", "Child", "Sleep Duration")
        elif report_type.startswith("Toileting"):
            self.report_table["columns"] = ("Date", "Child", "Pooped", "Poop Count")
        elif report_type.startswith("Comments"):
            self.report_table["columns"] = ("Date", "Child", "Comments")

        for col in self.report_table["columns"]:
            self.report_table.heading(col, text=col)

        # Fetch and display data
        for child in common_db_utils.get_all_children():
            child_id = child[0]
            full_name = f"{child[1]} {child[3]}"
            entries = child_day_info_utils.get_data_for_dates(child_id, date_range)

            for entry in entries:
                if report_type.startswith("All Data"):
                    row = (
                        entry["date"],
                        full_name,
                        entry.get("arrival", "-"),
                        entry.get("departure", "-"),
                        entry.get("main", "-"),
                        entry.get("dessert", "-"),
                        entry.get("sleep", "-"),
                        "Yes" if entry.get("pooped") else "No",
                        entry.get("poop_count", 0),
                        (entry.get("comments") or "")[:50]
                    )
                elif report_type.startswith("Meals"):
                    row = (
                        entry["date"],
                        full_name,
                        entry.get("main", "-"),
                        entry.get("dessert", "-")
                    )
                elif report_type.startswith("Sleep"):
                    row = (
                        entry["date"],
                        full_name,
                        entry.get("sleep", "-")
                    )
                elif report_type.startswith("Toileting"):
                    row = (
                        entry["date"],
                        full_name,
                        "Yes" if entry.get("pooped") else "No",
                        entry.get("poop_count", 0)
                    )
                elif report_type.startswith("Comments"):
                    row = (
                        entry["date"],
                        full_name,
                        (entry.get("comments") or "")[:100]
                    )
                else:
                    continue  # unknown report type

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

    def submit_reports(self):
        print("Submitting Reports!")