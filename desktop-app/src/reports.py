import os
from datetime import datetime

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
                "Meals (Week)",
                "Sleep (Week)",
                "Toileting (Week)",
                "Comments (Week)"
            ],
            state="readonly",
            width=25
        )
        report_type_combo.grid(row=0, column=1, padx=(0, 10), sticky="w")
        report_type_combo.current(0)  # Default: "All Data (Day)")

        generate_button = ttk.Button(controls_frame, text="Preview Report", command=self.generate_report)
        generate_button.grid(row=0, column=2, padx=10)

        self.publish_button = tk.Button(controls_frame, text="Publish to Parents", command=self.publish_report)
        self.publish_button.grid(row=0, column=4, pady=10, padx=10)

        export_button = ttk.Button(controls_frame, text="Export", command=self.export_report)
        export_button.grid(row=0, column=5)

        print_button = ttk.Button(controls_frame, text="Print", command=self.print_report)
        print_button.grid(row=0, column=6, padx=10)

        # === Report Table ===
        default_columns = (
            "Date", "Child", "Arrival", "Departure",
            "Main", "Dessert", "Sleep", "Poops", "Comments"
        )
        self.report_table = ttk.Treeview(
            self.reports_frame,
            columns=default_columns,
            show='headings'
        )

        self.report_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.report_table.bind("<Configure>", self.adjust_column_widths)
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
            # Get full week Mon-Sun for selected_date
            full_week_dates = calendar_utils.get_week_dates(selected_date)
            # Filter to weekdays only Mon-Fri
            date_range = [d for d in full_week_dates if datetime.strptime(d, "%Y-%m-%d").weekday() < 5]
        else:  # Day report
            date_range = [selected_date]

        # Set up dynamic columns
        if report_type.startswith("All Data (Day)"):
            self.report_table["columns"] = (
                "Date", "Child", "Arrival", "Departure",
                "Main", "Dessert", "Sleep", "Poops", "Comments"
            )

            for col in self.report_table["columns"]:
                self.report_table.heading(col, text=col)

        elif report_type == "All Data (Week)":
            # Columns: Child + weekdays of the week
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type == "Meals (Week)":
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type == "Sleep (Week)":
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type == "Toileting (Week)":
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type == "Comments (Week)":
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)
                
        else:
            # Unknown report type - clear columns
            self.report_table["columns"] = ()
            return

            # Fetch and display data
        for child in common_db_utils.get_all_children():
            child_id = child[0]
            full_name = f"{child[1]} {child[3]}"

            if report_type == "All Data (Day)":
                entries = child_day_info_utils.get_data_for_dates(child_id, date_range)
                for entry in entries:
                    row = (
                        entry["date"],
                        full_name,
                        entry.get("arrival", "-"),
                        entry.get("departure", "-"),
                        entry.get("main", "-"),
                        entry.get("dessert", "-"),
                        entry.get("sleep", "-"),
                        entry.get("poop_count", 0),
                        (entry.get("comments") or "")[:50]
                    )
                    self.report_table.insert("", "end", values=row)

            elif "Week" in report_type:
                # Weekly reports have one row per child,
                # columns are weekdays in date_range (except Child at index 0)
                # Gather data per date for that child
                entries = child_day_info_utils.get_data_for_dates(child_id, date_range)
                # Map date -> entry
                entry_map = {e["date"]: e for e in entries}

                row = [full_name]
                for date_str in date_range:
                    entry = entry_map.get(date_str, {})

                    if report_type == "All Data (Week)":
                        # Combine summary info into cell (or you can customize)
                        val = (
                            f"A:{entry.get('arrival', '-')}, "
                            f"D:{entry.get('departure', '-')}, "
                            f"M:{entry.get('main', '-')}, "
                            f"DS:{entry.get('dessert', '-')}, "
                            f"S:{entry.get('sleep', '-')}, "
                            f"P:{entry.get('poop_count', 0)}, "
                            f"C:{(entry.get('comments') or '')[:20]}"
                        )
                    elif report_type == "Meals (Week)":
                        val = f"{entry.get('main', '-')}, {entry.get('dessert', '-')}"
                    elif report_type == "Sleep (Week)":
                        val = entry.get('sleep', '-')
                    elif report_type == "Toileting (Week)":
                        val = str(entry.get('poop_count', 0))
                    elif report_type == "Comments (Week)":
                        val = (entry.get('comments') or '')[:50]
                    else:
                        val = ""

                    row.append(val)

                self.report_table.insert("", "end", values=row)
                
        self.adjust_column_widths()


    def export_report(self):
        import csv
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                initialdir=os.path.expanduser("~"))
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.report_table["columns"])
                for row_id in self.report_table.get_children():
                    row = self.report_table.item(row_id)["values"]
                    writer.writerow(row)

    def publish_report(self):
        print("Publishing!!!")

    def print_report(self):
        print("Printing!!!")

    def adjust_column_widths(self, event=None):
        total_width = self.report_table.winfo_width()
        if total_width <= 0:
            return  # Avoid division by zero

        columns = self.report_table["columns"]

        if "Child" in columns and len(columns) > 2:
            # Weekly layout
            self.report_table.column("Child", width=int(total_width * 0.2), stretch=False)
            day_width = int(total_width * 0.8 / (len(columns) - 1))
            for col in columns:
                if col != "Child":
                    self.report_table.column(col, width=day_width, stretch=False)
        else:
            # Fallback to named percentage layout
            column_widths = {
                "Comments": 0.30,
                "Child": 0.20,
                "Date": 0.10,
                "Arrival": 0.10,
                "Departure": 0.10,
                "Main": 0.08,
                "Dessert": 0.08,
                "Sleep": 0.10,
                "Poops": 0.07,
            }
            for col in columns:
                pct = column_widths.get(col, 0.10)
                self.report_table.column(col, width=int(total_width * pct), stretch=False)

