import tkinter as tk
from tkinter import ttk
from functools import partial

from utils import clock_utils
from utils.db_utils import children_db_utils, child_day_info_utils

class ChildDayInfoPage(tk.Toplevel):
    def __init__(self, parent, child_id, selected_date):
        super().__init__(parent)
        self.parent = parent
        self.selected_date = selected_date
        self.child_id = child_id
        self.configure(bg="#003366")
        self.geometry("800x600")

        self.setup_page_layout(child_id, selected_date)

    def setup_page_layout(self, child_id, selected_date):
            
            child = children_db_utils.get_child_by_id(child_id)

            self.existing_day_data = child_day_info_utils.load_day_info(self)

            self.slider_words = {
                1: "Nothing",
                2: "A Little",
                3: "Okay",
                4: "Good",
                5: "Excellent"
            }

            fname = child[1]
            lname = child[3]
            self.title(f"{fname} {lname}: {selected_date}")
            group = child[5].lower() if child[5] else "baby"
            print(f"Age group: {group}")

            # Root grid config
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Container Frame
            main_frame = ttk.Frame(self, style="childDayInfoBackground.TFrame")
            main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

            for i in range(3):
                main_frame.grid_columnconfigure(i, weight=1)

            # Title
            self.title_label = tk.Label(
                main_frame,
                text=f"{fname} {lname}: {selected_date}",
                font=("Arial", 14, "bold"),
                wraplength=600,
                anchor="center",
                justify="center",
                bg="#d9f1fb",
                pady=10
            )

            # Generate durations
            durations = []
            for minutes in range(0, 241, 15):
                hours = minutes // 60
                mins = minutes % 60
                if hours == 0:
                    label = f"0:{mins}" if mins > 0 else "0"
                elif mins == 0:
                    label = f"{hours}:00" if hours == 1 else f"{hours}:00"
                else:
                    hour_label = f"{hours}" if hours == 1 else f"{hours}"
                    label = f"{hour_label}:{mins}"
                durations.append(label)

            self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="n")

            #arrival time
            tk.Label(main_frame, text=f"What time did {fname} arrive?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=10, pady=5)
            self.arrival_combobox = ttk.Combobox(main_frame, values=clock_utils.generate_time_slots(), state="readonly", width=20, style="childDayInfo.TCombobox")
            self.arrival_combobox.grid(row=1, column=1, sticky='w', padx=10)

            if self.existing_day_data:
                self.arrival_combobox.set(self.existing_day_data["actual_arrival"])
            else:
                self.arrival_combobox.current(0)

            #departure time
            tk.Label(main_frame, text=f"What time did {fname} leave?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=10, pady=5)
            self.departure_combobox = ttk.Combobox(main_frame, values=clock_utils.generate_time_slots(), state="readonly", width=20, style="childDayInfo.TCombobox")
            self.departure_combobox.grid(row=2, column=1, sticky='w', padx=10)

            if self.existing_day_data:
                self.departure_combobox.set(self.existing_day_data["actual_finish"])
            else:
                self.departure_combobox.current(0)

            # How well the child ate
            tk.Label(main_frame, text=f"How well did {fname} eat?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky='w', padx=10, pady=5)

            self.sliders = {}  # to store slider values

            row_counter = 4

            # Sliders based on group
            if group in ["grands", "moyens"]:
                for label in ["Starter", "Main", "Dessert"]:
                    key = label.lower()
                    value = self.existing_day_data.get(key, 3) if self.existing_day_data else 3
                    self.create_slider(main_frame, label, row_counter, value=value)
                    row_counter += 1
            else:
                for label in ["Main", "Dessert"]:
                    key = label.lower()
                    value = self.existing_day_data.get(key, 3) if self.existing_day_data else 3
                    self.create_slider(main_frame, label, row_counter, value=value)
                    row_counter += 1


            # Poop Checkbox
            self.pooped_var = tk.BooleanVar()
            tk.Label(main_frame, text=f"Did {fname} poop?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=row_counter, column=0, sticky="w", padx=(10, 5), pady=10)

            self.poop_checkbox = tk.Checkbutton(main_frame, variable=self.pooped_var, bg="#d9f1fb", command=self.toggle_poop_count)
            self.poop_checkbox.grid(row=row_counter, column=1, sticky="w", pady=10)

            if self.existing_day_data:
                self.pooped_var.set(self.existing_day_data["pooped"])

            row_counter += 1

            # Poop count
            tk.Label(main_frame, text="How many times?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=row_counter, column=0, sticky='w', padx=10)
            self.poop_count_spinbox = ttk.Spinbox(main_frame, from_=0, to=10, state='normal' if self.pooped_var.get() else 'disabled', style="childDayInfo.TSpinbox")
            self.poop_count_spinbox.grid(row=row_counter, column=1, sticky='w', padx=10)
            if self.existing_day_data:
                self.poop_count_spinbox.delete(0, 'end')
                self.poop_count_spinbox.insert(0, str(self.existing_day_data["poop_count"]))
            row_counter += 1

            # Label and dropdown
            tk.Label(main_frame, text=f"How long did {fname} sleep?", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=row_counter, column=0, sticky='w', padx=10, pady=5)
            self.sleep_combobox = ttk.Combobox(main_frame, values=durations, state="readonly", width=20, style="childDayInfo.TCombobox")
            self.sleep_combobox.grid(row=row_counter, column=1, sticky='w', padx=10)

            if self.existing_day_data:
                self.sleep_combobox.set(self.existing_day_data["sleep_duration"])
            else:
                self.sleep_combobox.current(0)
            row_counter += 1

            # Additional comments
            tk.Label(main_frame, text="Additional comments:", bg="#d9f1fb", font=("Arial", 11, "bold")).grid(row=row_counter, column=0, sticky='nw', padx=10, pady=5)
            self.comments_text = tk.Text(main_frame, width=40, height=6)
            self.comments_text.grid(row=row_counter, column=1, sticky='w', padx=10, pady=5)
            if self.existing_day_data:
                self.comments_text.insert("1.0", self.existing_day_data["comments"])
            row_counter += 1

            # Buttons Frame
            buttons_frame = ttk.Frame(main_frame, style="childDayInfoBackground.TFrame")
            buttons_frame.grid(row=row_counter, column=0, columnspan=2, pady=20)

            # Update Button
            self.save_button = ttk.Button(buttons_frame, text="Update", style="update.TButton", command=lambda: child_day_info_utils.save_day_info(self, completed=0))
            self.save_button.pack(side="left", padx=10)

            # Complete Day Button
            self.complete_button = ttk.Button(buttons_frame, text="Complete Day", style="complete.TButton", command=lambda: child_day_info_utils.save_day_info(self, completed=1))
            self.complete_button.pack(side="left", padx=10)


    def create_slider(self, parent, label_text, row, value=3):
        tk.Label(parent, text=f"{label_text}:", font=("Arial", 11, "bold"), bg="#d9f1fb").grid(
            row=row, column=0, sticky="w", padx=(20, 15)
        )

        scale_var = tk.DoubleVar(value=value)
        slider = ttk.Scale(parent, from_=1, to=5, orient="horizontal", length=100, variable=scale_var, style="Horizontal.TScale")
        slider.grid(row=row, column=1, sticky="ew", padx=(5, 5))

        value_label = tk.Label(parent, text=self.slider_words[int(scale_var.get())], bg="#d9f1fb", width=8, anchor="w")
        value_label.grid(row=row, column=2, sticky="w")

        scale_var.trace_add("write", partial(self.update_slider_word, var=scale_var, label=value_label))
        self.sliders[label_text.lower()] = scale_var

    def update_slider_word(self, *args, var=None, label=None):
        if var and label:
            value = int(round(var.get()))
            label.config(text=self.slider_words.get(value, str(value)))

    def toggle_poop_count(self):
        if self.pooped_var.get():
            self.poop_count_spinbox.config(state='normal')
        else:
            self.poop_count_spinbox.config(state='disabled')
            self.poop_count_spinbox.delete(0, 'end')
            self.poop_count_spinbox.insert(0, '0')
