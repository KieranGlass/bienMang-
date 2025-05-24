import os
from datetime import datetime

from utils import calendar_utils, clock_utils, navigation_utils, comms_utils
from utils.db_utils import common_db_utils, child_day_info_utils

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


        self.bind("<Configure>", self.resize_table_frame)
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
                "Comments (Week)",
                "Hours (Week)"
            ],
            state="readonly",
            width=25
        )
        report_type_combo.grid(row=0, column=1, padx=(0, 10), sticky="w")
        report_type_combo.current(0)  # Default: "All Data (Day)")

        generate_button = ttk.Button(controls_frame, text="Preview Report", command=self.generate_report)
        generate_button.grid(row=0, column=2, padx=10)

        style = ttk.Style()
        style.configure("Blue.TButton", background="#2196F3", foreground="white")
        style.map("Blue.TButton",
            background=[("active", "#1976D2")])

        self.publish_button = ttk.Button(controls_frame, text="Publish Daily Report", style="Blue.TButton",
                                command=self.publish_report)
        self.publish_button.grid(row=0, column=4, pady=10, padx=10)

        export_button = ttk.Button(controls_frame, text="Export", style="Blue.TButton", command=self.export_report)
        export_button.grid(row=0, column=5)

        print_button = ttk.Button(controls_frame, text="Print", style="Blue.TButton", command=self.print_report)
        print_button.grid(row=0, column=6, padx=10)

        style = ttk.Style()
        style.configure("Treeview", rowheight=25)  # default
        style.configure("Mid.Treeview", rowheight=50)
        style.configure("Tall.Treeview", rowheight=140)

        # Row striping
        style.map("Treeview", background=[('selected', '#d9d9d9')])

        # === Report Table ===
        default_columns = (
            "Date", "Child", "Arrival", "Departure",
            "Main", "Dessert", "Sleep", "Poops", "Comments"
        )
        
        self.table_frame = ttk.Frame(self.reports_frame)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Prevent table_frame from resizing itself based on content
        self.table_frame.grid_propagate(False)

        self.report_table = ttk.Treeview(
            self.table_frame,
            columns=default_columns,
            show='headings'
        )
        self.report_table.grid(row=0, column=0, sticky="nsew")

        self.report_table.tag_configure("evenrow", background="#f0f0f0")
        self.report_table.tag_configure("oddrow", background="#ffffff")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.report_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.report_table.configure(yscrollcommand=scrollbar.set)

        # Make table_frame expand
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

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

        d = self.calendar.selection_get()
        dt = clock_utils.format_title_date(d)

        self.date_label = tk.Label(controls_frame, text=f"Selected Date: {dt}")
        self.date_label.grid(row=0, column=3, padx=10)

        calendar_utils.highlight_weekdays(self.calendar, self.calendar.get_displayed_month)
        self.disabled_weekends = calendar_utils.highlight_weekdays(self.calendar, self.calendar.get_displayed_month)

        # Clock
        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)

        self.report_type_var.set("All Data (Day)")
        self.generate_report()


    def generate_report(self):

        groups_with_starter = {"grands", "moyens"}

        self.slider_word_map = {
            1: "Nothing",
            2: "A Little",
            3: "Okay",
            4: "Good",
            5: "Excellent"
        }
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
            self.report_table.configure(style="Treeview")
            columns = ["Child", "Arrival", "Departure"]
            if any((child[5] or "").lower() in groups_with_starter for child in common_db_utils.get_all_children()):
                columns.append("Starter")
            columns += ["Main", "Dessert", "Sleep", "Poops", "Comments"]
            self.report_table["columns"] = columns
            for col in columns:
                self.report_table.heading(col, text=col)

        elif report_type == "All Data (Week)":
            self.report_table.configure(style="Tall.Treeview")
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type in {"Sleep (Week)", "Toileting (Week)", "Comments (Week)"}:
            self.report_table.configure(style="Treeview")
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type in {"Meals (Week)"}:
            self.report_table.configure(style="Mid.Treeview")
            self.report_table["columns"] = ["Child"] + date_range
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        elif report_type == "Hours (Week)":
            self.report_table.configure(style="Treeview")
            self.report_table["columns"] = ["Child"] + date_range + ["Total"]
            for col in self.report_table["columns"]:
                if col == "Child":
                    self.report_table.heading(col, text="Child")
                elif col == "Total":
                    self.report_table.heading(col, text="Total")
                else:
                    dt = datetime.strptime(col, "%Y-%m-%d")
                    label = dt.strftime("%a %-d %b") if os.name != 'nt' else dt.strftime("%a %#d %b")
                    self.report_table.heading(col, text=label)

        else:
            # Unknown report type
            self.report_table["columns"] = ()
            return

        # Fetch and display data
        for child in common_db_utils.get_all_children():
            child_id = child[0]
            full_name = f"{child[1]} {child[3]}"

            if report_type == "All Data (Day)":
                entries = child_day_info_utils.get_data_for_dates(child_id, date_range)
                for entry in entries:
                    main_raw = entry.get("main")
                    main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"

                    dessert_raw = entry.get("dessert")
                    dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"

                    child_group = (child[5] or "").lower()

                    starter = "-"

                    if child_group in groups_with_starter:
                        starter_raw = entry.get("starter")
                        starter = self.slider_word_map.get(int(starter_raw), "-") if starter_raw is not None else "-"

                    main_raw = entry.get("main")
                    main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"

                    dessert_raw = entry.get("dessert")
                    dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"

                    base_row = [
                        full_name,
                        entry.get("arrival", "-"),
                        entry.get("departure", "-")
                    ]

                    if "Starter" in self.report_table["columns"]:
                        if child_group in groups_with_starter:
                            base_row.append(starter)
                        else:
                            base_row.append("-")

                    base_row.extend([
                        main,
                        dessert,
                        entry.get("sleep", "-"),
                        entry.get("poop_count", 0),
                        (entry.get("comments") or "")[:50]
                    ])

                    row = tuple(base_row)

                    tag = "evenrow" if len(self.report_table.get_children()) % 2 == 0 else "oddrow"
                    self.report_table.insert("", "end", values=row, tags=(tag,))

            elif "Week" in report_type:
                entries = child_day_info_utils.get_data_for_dates(child_id, date_range)
                entry_map = {e["date"]: e for e in entries}
                row = [full_name]

                if report_type == "Hours (Week)":
                    total_hours = 0.0
                    for date_str in date_range:
                        entry = entry_map.get(date_str, {})
                        arrival_str = entry.get("arrival")
                        departure_str = entry.get("departure")

                        if arrival_str and departure_str:
                            try:
                                arrival = datetime.strptime(arrival_str, "%H:%M")
                                departure = datetime.strptime(departure_str, "%H:%M")
                                hours = (departure - arrival).total_seconds() / 3600.0
                                if hours < 0:
                                    hours = 0
                            except Exception:
                                hours = 0
                        else:
                            hours = 0

                        total_hours += hours
                        row.append(f"{hours:.2f}")

                    row.append(f"{total_hours:.2f}")

                else:
                    for date_str in date_range:
                        entry = entry_map.get(date_str, {})

                        if report_type == "All Data (Week)":
                            main_raw = entry.get("main")
                            main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"

                            dessert_raw = entry.get("dessert")
                            dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"

                            starter = "-"
                            if (child[5] or "").lower() in groups_with_starter:
                                starter_raw = entry.get("starter")
                                starter = self.slider_word_map.get(int(starter_raw), "-") if starter_raw is not None else "-"

                            val_lines = [
                                f"Arrival: {entry.get('arrival', '-')}",
                                f"Depart: {entry.get('departure', '-')}"
                            ]

                            if (child[5] or "").lower() in groups_with_starter:
                                starter_raw = entry.get("starter")
                                starter = self.slider_word_map.get(int(starter_raw), "-") if starter_raw is not None else "-"
                                val_lines.append(f"Starter: {starter}")

                            main_raw = entry.get("main")
                            main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"
                            val_lines.append(f"Main: {main}")

                            dessert_raw = entry.get("dessert")
                            dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"
                            val_lines.append(f"Dessert: {dessert}")

                            val_lines.append(f"Sleep: {entry.get('sleep', '-')}")
                            val_lines.append(f"Poops: {entry.get('poop_count', 0)}")
                            val_lines.append(f"Comment: {(entry.get('comments') or '')[:30]}")

                            val = "\n".join(val_lines)

                        elif report_type == "Meals (Week)":
                            meal_parts = []
                            if (child[5] or "").lower() in groups_with_starter:
                                starter_raw = entry.get("starter")
                                starter = self.slider_word_map.get(int(starter_raw), "-") if starter_raw is not None else "-"
                                meal_parts.append(starter)

                            main_raw = entry.get("main")
                            main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"
                            meal_parts.append(main)

                            dessert_raw = entry.get("dessert")
                            dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"
                            meal_parts.append(dessert)

                            val = "\n".join(meal_parts)

                        elif report_type == "Sleep (Week)":
                            val = entry.get('sleep', '-')
                        elif report_type == "Toileting (Week)":
                            val = str(entry.get('poop_count', 0))
                        elif report_type == "Comments (Week)":
                            val = (entry.get('comments') or '')[:50]
                        else:
                            val = ""

                        row.append(val)

                tag = "evenrow" if len(self.report_table.get_children()) % 2 == 0 else "oddrow"
                self.report_table.insert("", "end", values=row, tags=(tag,))

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
        groups_with_starter = {"grands", "moyens"}
        selected_date = self.calendar.get_date()
        for child in common_db_utils.get_all_children():
            child_id = child[0]
            full_name = f"{child[1]} {child[3]}"
            email = "kieranglass23@gmail.com"
            print(f"{email}")
            group = (child[5] or "").lower()

            entries = child_day_info_utils.get_data_for_dates(child_id, [selected_date])
            if entries:
                entry = entries[0]
                report_text = comms_utils.generate_plaintext_day_report(self, full_name, entry, include_starter=(group in groups_with_starter))
                comms_utils.send_email(email, f"Nursery Report for {selected_date}", report_text)

    def print_report(self):
        print("Printing!!!")

    def adjust_column_widths(self, event=None):
        total_width = self.report_table.winfo_width()
        if total_width <= 0:
            return  # Avoid division by zero

        columns = self.report_table["columns"]

        if "Child" in columns and len(columns) > 2 and "Comments" not in columns:
            # Weekly layout without "Comments" column
            self.report_table.column("Child", width=int(total_width * 0.15), stretch=False)
            day_width = int(total_width * 0.8 / (len(columns) - 1))
            for col in columns:
                if col != "Child":
                    self.report_table.column(col, width=day_width, stretch=False)
        else:
            # Distribute based on specific proportions
            static_widths = {
                "Child": 0.15,
                "Comments": 0.35
            }

            # Calculate remaining width for other columns
            remaining_cols = [col for col in columns if col not in static_widths]
            num_remaining = len(remaining_cols)
            remaining_width_pct = 0.45

            per_col_pct = remaining_width_pct / num_remaining if num_remaining > 0 else 0

            for col in columns:
                if col in static_widths:
                    pct = static_widths[col]
                else:
                    pct = per_col_pct
                self.report_table.column(col, width=int(total_width * pct), stretch=False)

        d = self.calendar.selection_get()
        dt = clock_utils.format_title_date(d)

        self.date_label.config(text=f"Selected Date: {dt}")

    def resize_table_frame(self, event=None):
        total_height = self.winfo_height()
        target_height = int(total_height * 0.4)  # 40% of window height
        self.table_frame.configure(height=target_height)
