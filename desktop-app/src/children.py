import re

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

from utils import navigation_utils, clock_utils
from utils.db_utils import common_db_utils, children_db_utils

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

from PIL import Image, ImageTk

'''
TODO:
- Design elements and buttons to pop and look nicer 
- address how page looks when there are no entries
'''

class Children(tk.Toplevel):
    
    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent  # Store the Dashboard instance
        print("Initializing Pupil list...")
        self.title("Current Pupils")
        self.geometry("1400x900")
        self.configure(bg="#d9f1fb")
        self.lift()
        self.create_children_window()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

    def create_children_window(self):

        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        # dashboard_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Ensure that the main window grid can grow as needed
        self.grid_rowconfigure(0, weight=1)  
        self.grid_rowconfigure(1, weight=1)  
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2)  
        self.grid_columnconfigure(2, weight=2)  

        # Content Frame in the center-right section (columns 1 and 2)
        dashboard_frame.grid_rowconfigure(0, weight=1)  
        dashboard_frame.grid_rowconfigure(1, weight=1)  
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_columnconfigure(1, weight=2)  
        dashboard_frame.grid_columnconfigure(2, weight=2)

        self.sidebar_frame = navigation_utils.create_global_sidebar(self)

        self.create_add_new_child_frame()

        self.create_pupil_list()

        self.create_pupil_info()

        self.create_schedule_chart_frame()

        # Bind selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Load and display all children from the database
        self.load_children()

    def create_add_new_child_frame(self):
        """Create the tabbed interface for child info and schedule."""
        
        # Create a Notebook widget for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Make sure the notebook expands in both directions
        self.grid_rowconfigure(1, weight=1)  # Row for notebook (1-based index)
        self.grid_columnconfigure(0, weight=1)  # Column 0 for notebook
        self.grid_columnconfigure(1, weight=1)  # Column 1 for notebook (optional)
        
        # Create three frames, a control panel and one for child info and one for schedule
        self.child_control_panel_frame = ttk.Frame(self.notebook)
        self.child_info_frame = ttk.Frame(self.notebook)
        self.schedule_frame = ttk.Frame(self.notebook)

        # Add the frames as tabs in the notebook
        self.notebook.add(self.child_control_panel_frame, text="Control Panel")
        self.notebook.add(self.child_info_frame, text="Child Information")
        self.notebook.add(self.schedule_frame, text="Weekly Schedule")

        # Initially disable the "Child Information" and "Weekly Schedule" tabs
        self.notebook.tab(self.child_info_frame, state='disabled')
        self.notebook.tab(self.schedule_frame, state='disabled')

        # Call functions to create content in the respective frames
        self.create_control_panel_form(self.child_control_panel_frame)
        self.create_child_info_form(self.child_info_frame)
        self.create_schedule_form(self.schedule_frame)

    def create_control_panel_form(self, parent):
        """Create the child control panel in the first tab."""
        panel_frame = ttk.Frame(parent)
        panel_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        label_widget = ttk.Label(panel_frame, text="Creche Information", anchor="w", font=("Helvetica", 16))
        label_widget.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        total = children_db_utils.get_child_count()
        label_widget = ttk.Label(panel_frame, text=f"Total Children: {total}", anchor="w", font=("Helvetica", 12))
        label_widget.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        petits = children_db_utils.get_age_group_petits()
        label_widget = ttk.Label(panel_frame, text=f"Petits Section: {petits}", anchor="w", font=("Helvetica", 12))
        label_widget.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        moyens = children_db_utils.get_age_group_moyens()
        label_widget = ttk.Label(panel_frame, text=f"Moyens Section: {moyens}", anchor="w", font=("Helvetica", 12))
        label_widget.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        grands = children_db_utils.get_age_group_grands()
        label_widget = ttk.Label(panel_frame, text=f"Grands Section: {grands}", anchor="w", font=("Helvetica", 12))
        label_widget.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        add_child_button = ttk.Button(panel_frame, text="Add New Child", command=self.add_new_child)
        add_child_button.grid(row=0, column=4, padx=5, pady=5, sticky="e" )

        edit_child_info_button = ttk.Button(panel_frame, text="Edit Child Info", command=self.edit_child_info)
        edit_child_info_button.grid(row=1, column=4, padx=5, pady=5, sticky="e" )
        
        edit_child_schedule_button = ttk.Button(panel_frame, text="Edit Child Schedule", command=lambda: self.edit_child_schedule())
        edit_child_schedule_button.grid(row=2, column=4, padx=5, pady=5, sticky="e" )

        delete_child_button = ttk.Button(panel_frame, text="Delete Child", command=lambda: self.delete_child())
        delete_child_button.grid(row=3, column=4, padx=5, pady=5, sticky="e" )

    def create_child_info_form(self, parent):
        """Create the child info form in the second tab."""
        labels_frame = ttk.Frame(parent)
        labels_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create a list of labels
        labels = [
            "First Name", "Middle Name", "Last Name", "Date of Birth", "Year Group", 
            "Guardian 1 First Name", "Guardian 1 Last Name", "Guardian 1 Contact No", 
            "Guardian 1 Email", "Guardian 2 First Name", "Guardian 2 Last Name", 
            "Guardian 2 Contact No"
        ]
    
        entries = []

        # Iterate to create label and entry pairs in two columns
        for i, label in enumerate(labels):
            row = i // 2  # Rows for label-entry pairs
            col = i % 2   # Columns 0 or 1
        
            label_widget = ttk.Label(labels_frame, text=label, anchor="w", font=("Arial", 12))
            label_widget.grid(row=row, column=col * 2, padx=5, pady=5, sticky="w")
        
            if label == "Date of Birth":
                # Use DateEntry widget for Date of Birth
                entry_widget = DateEntry(labels_frame, font=("Arial", 12), date_pattern="yyyy-mm-dd")
                entry_widget.grid(row=row, column=col * 2 + 1, padx=5, pady=5, sticky="ew")
                entries.append(entry_widget)
            elif label == "Year Group":
                # Year Group dropdown (combobox)
                year_group_options = ['Petits', 'Moyens', 'Grands']
                year_group_combobox = ttk.Combobox(labels_frame, values=year_group_options, state="readonly", font=("Arial", 12))
                year_group_combobox.set("Petits")  # Default to "Petits"
                year_group_combobox.grid(row=row, column=col * 2 + 1, padx=5, pady=5, sticky="ew")
                entries.append(year_group_combobox)
            else:
                # For other fields, use Entry widget
                entry_widget = ttk.Entry(labels_frame, font=("Arial", 12))
                entry_widget.grid(row=row, column=col * 2 + 1, padx=5, pady=5, sticky="ew")

                entries.append(entry_widget)

        # Add buttons for navigation
        cancel_button = ttk.Button(labels_frame, text="Cancel", command=self.cancel_process)
        cancel_button.grid(row=len(labels), column=0, padx=5, pady=10, sticky="w")
    
        next_button = ttk.Button(labels_frame, text="Next", command=self.next_to_schedule)
        next_button.grid(row=len(labels), column=1, padx=5, pady=10, sticky="e")

        # Assign entry fields to the respective attributes
        self.first_name_entry = entries[0]
        self.middle_name_entry = entries[1]
        self.last_name_entry = entries[2]
        self.date_of_birth_entry = entries[3]
        self.year_group_entry = entries[4]
        self.guardian_one_fname_entry = entries[5]
        self.guardian_one_lname_entry = entries[6]
        self.guardian_one_contact_no_entry = entries[7]
        self.guardian_one_email_entry = entries[8]
        self.guardian_two_fname_entry = entries[9]
        self.guardian_two_lname_entry = entries[10]
        self.guardian_two_contact_no_entry = entries[11]

    def create_schedule_form(self, parent):
        """Create the weekly schedule form in the second tab."""
        schedule_frame = ttk.LabelFrame(parent, text="Weekly Schedule (Arrival/Finish Times)", padding="10")
        schedule_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.arrival_entries = {}
        self.finish_entries = {}
        self.day_toggles = {}  # This will store the checkbox states

        # Generate the time slots for 7:30 AM to 6:00 PM, with 15-minute intervals
        time_slots = clock_utils.generate_time_slots("7:30", "18:00", 15)

        # Create entry fields and checkboxes for each day
        for idx, day in enumerate(days):

            # CheckButton for each day to indicate presence
            day_toggle = ttk.Checkbutton(schedule_frame, text="Present", command=lambda day=day: self.toggle_day(day))
            day_toggle.grid(row=idx, column=0, padx=5, pady=5, sticky="w")
            self.day_toggles[day] = day_toggle

            day_label = ttk.Label(schedule_frame, text=f"{day}:")
            day_label.grid(row=idx, column=1, padx=5, pady=5, sticky="w")

            # Arrival time dropdown
            arrival_label = ttk.Label(schedule_frame, text="Arrival:")
            arrival_label.grid(row=idx, column=2, padx=5, pady=5, sticky="w")

            arrival_combobox = ttk.Combobox(schedule_frame, values=time_slots, font=("Arial", 12))
            arrival_combobox.set(time_slots[0])  # Default to the first time slot (7:30 AM)
            arrival_combobox.grid(row=idx, column=3, padx=5, pady=5, sticky="ew")
            self.arrival_entries[day] = arrival_combobox

            # Finish time dropdown
            finish_label = ttk.Label(schedule_frame, text="Finish:")
            finish_label.grid(row=idx, column=4, padx=5, pady=5, sticky="w")

            finish_combobox = ttk.Combobox(schedule_frame, values=time_slots, font=("Arial", 12))
            finish_combobox.set(time_slots[0])  # Default to the first time slot (7:30 AM)
            finish_combobox.grid(row=idx, column=5, padx=5, pady=5, sticky="ew")
            self.finish_entries[day] = finish_combobox

            # Set Arrival and Finish fields to N/A by default (disabled if not selected)
            self.set_day_to_na(day, False)

            # Add buttons for navigation
        cancel_button = ttk.Button(schedule_frame, text="Cancel", command=self.cancel_process)
        cancel_button.grid(row=7, column=0, padx=5, pady=10, sticky="w")
    
        back_button = ttk.Button(schedule_frame, text="Back", command=self.back_to_child_info)
        back_button.grid(row=7, column=1, padx=5, pady=10, sticky="w")
    
        finish_button = ttk.Button(schedule_frame, text="Finish", command=self.finish_process)
        finish_button.grid(row=7, column=2, padx=5, pady=10, sticky="e")

    def clear_form(self):
        """Clear all form fields."""
        for attr in dir(self):
            if attr.endswith('_entry'):
                getattr(self, attr).delete(0, tk.END)

    def create_pupil_list(self):

        # Add the Treeview widget to display children (Row 2, Right column)
        self.tree = ttk.Treeview(self, columns=("Id", "First Name", "Last Name", "Year Group"), show="headings", style="ChildrenTree.Treeview")
        self.tree.grid(row=1, column=2, columnspan=1, padx=0, pady=0, sticky="nsew")
    
        # Define the headings
        self.tree.heading("Id", text="Id", command=lambda: self.sort_children(0))
        self.tree.heading("First Name", text="First Name", command=lambda: self.sort_children(1))
        self.tree.heading("Last Name", text="Last Name", command=lambda: self.sort_children(2))
        self.tree.heading("Year Group", text="Year Group", command=lambda: self.sort_children(3))

        # Set width for each column
        self.tree.column("Id", width=20, anchor="center")
        self.tree.column("First Name", width=100, anchor="center")
        self.tree.column("Last Name", width=100, anchor="center")
        self.tree.column("Year Group", width=100, anchor="center")

        # Adjust the width of the entire Treeview based on window resizing
        self.tree.grid_columnconfigure(0, weight=1, uniform="equal")
        self.tree.grid_columnconfigure(1, weight=1, uniform="equal")
        self.tree.grid_columnconfigure(2, weight=1, uniform="equal")
        self.tree.grid_columnconfigure(3, weight=1, uniform="equal")

    def create_pupil_info(self):
        # Add the info box in the middle column (with border)
        self.info_frame = ttk.Frame(self, relief="solid", borderwidth=2)
        self.info_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

        # Configure grid to divide the info_frame into two columns and two rows
        self.info_frame.grid_rowconfigure(0, weight=1, minsize=50)  # First row will take up half of the vertical space
        self.info_frame.grid_rowconfigure(1, weight=1, minsize=50)  # Second row will take up the bottom half
        self.info_frame.grid_columnconfigure(0, weight=1, minsize=200)  # Left column will take up half of the horizontal space
        self.info_frame.grid_columnconfigure(1, weight=2, minsize=300)  # Right column will take up the other half

        # ---------------- Left Half ----------------

        # Add the name and dob fields (bottom half of the left side)
        self.name_frame = ttk.Frame(self.info_frame)
        self.name_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Load the image file (ensure the path is correct)
        image_path = "/app/src/resources/images/potter.PNG"  # Replace with actual path
        img = Image.open(image_path)
        img = img.resize((160, 140))  # Resize image as needed
        photo = ImageTk.PhotoImage(img)

        # Create a Label to display the image
        label = tk.Label(self.name_frame, image=photo)
        label.image = photo  # Keep a reference to the image
        label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Create label-value pairs for Left Half (Name and DOB)
        self.first_name_pair = self.create_label_value_pair(self.name_frame, "First Name", 1, 0)
        self.middle_name_pair = self.create_label_value_pair(self.name_frame, "Middle Name", 2, 0)
        self.last_name_pair = self.create_label_value_pair(self.name_frame, "Last Name", 3, 0)
        self.dob_pair = self.create_label_value_pair(self.name_frame, "Date of Birth", 4, 0)
        self.year_group_pair = self.create_label_value_pair(self.name_frame, "Year Group", 5, 0)

        # ---------------- Right Half ----------------
        # Placeholder for additional information labels (Right half will have 7 labels)
        self.additional_info_frame = ttk.Frame(self.info_frame)
        self.additional_info_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Create label-value pairs for Right Half (Guardian Info)
        self.guardian_one_fname_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 1 First Name", 0, 0)
        self.guardian_one_lname_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 1 Last Name", 1, 0)
        self.guardian_one_contactNo_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 1 Contact No", 2, 0)
        self.guardian_one_email_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 1 Email", 3, 0)
        self.guardian_two_fname_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 2 First Name", 4, 0)
        self.guardian_two_lname_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 2 Last Name", 5, 0)
        self.guardian_two_contactNo_pair = self.create_label_value_pair(self.additional_info_frame, "Guardian 2 Contact No", 6, 0)

    def create_label_value_pair(self, parent_frame, label_text, row, col):
        """ Helper function to create a label-value pair inside a box. """
    
        # Create a frame for the label-value pair to act like a box
        pair_frame = ttk.Frame(parent_frame, relief="solid", borderwidth=1, padding=5)
        pair_frame.grid(row=row, column=col, padx=10, pady=0, sticky="nsew")

        # Configure this pair_frame to have equal width and height (boxes will be uniform size)
        parent_frame.grid_columnconfigure(col, weight=1, uniform="group1")
        parent_frame.grid_rowconfigure(row, weight=1)

        # Label part (displayed at the top of the box)
        label = ttk.Label(pair_frame, text=label_text, anchor="w", font=("Helvetica", 10, "bold"))
        label.pack(fill="x", pady=(0, 0))  # Label on top, with space below

        # Value part (displayed below the label in a different style)
        value = ttk.Label(pair_frame, text="--", anchor="w", font=("Arial", 10), wraplength=400)
        value.pack(fill="x", pady=(5, 5))  # Value below, with space above

        # Return both the label and value so they can be updated later
        return label, value

    def create_schedule_chart_frame(self):
        """Create the chart frame where the bar chart will be displayed."""
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Adjust sticky property to center content
        self.chart_frame.grid_rowconfigure(0, weight=1)  # Make sure the row is stretchable
        self.chart_frame.grid_columnconfigure(0, weight=1)  # Make sure the column is stretchable
        self.chart_frame.grid_propagate(False) 

    def create_schedule_chart(self, child_name, schedule):
        """Create and display the bar chart for the selected child's schedule."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))

        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        colors = ['lightcoral'] * 5

        start_time_base = datetime.strptime("07:30", "%H:%M")
        end_time_base = datetime.strptime("18:00", "%H:%M")

        time_slots = [start_time_base + timedelta(minutes=30 * i)
                  for i in range(int((end_time_base - start_time_base).seconds / 60 / 30) + 1)]
        time_labels = [t.strftime("%H:%M") for t in time_slots]
        time_ticks = [t.hour + t.minute / 60 for t in time_slots]

        for i, day in enumerate(days_of_week):
            day_schedule = schedule.get(day)

            if (
                not day_schedule or
                not isinstance(day_schedule, tuple) or
                len(day_schedule) != 2 or
                day_schedule[0] in [None, "N/A"] or
                day_schedule[1] in [None, "N/A"]
            ):
                empty_start = datetime.strptime("07:30", "%H:%M")
                ax.barh(day, 0, color='lightgrey', left=empty_start.hour + empty_start.minute / 60, height=0.6)
                continue

            # Only gets here if data is valid
            start_str, end_str = day_schedule
            try:
                start = datetime.strptime(start_str, "%H:%M")
                end = datetime.strptime(end_str, "%H:%M")
                duration = (end - start).seconds / 3600
                ax.barh(day, duration, color=colors[i], left=start.hour + start.minute / 60, height=0.6)
            except ValueError:
                # In case parsing still fails
                empty_start = datetime.strptime("07:30", "%H:%M")
                ax.barh(day, 0, color='lightgrey', left=empty_start.hour + empty_start.minute / 60, height=0.6)

        ax.set_title(f"General Weekly Schedule for {child_name}")
        ax.set_xlabel("Time (Hours)")
        ax.set_ylabel("Days of the Week")
        ax.set_xticks(time_ticks)
        ax.set_xticklabels(time_labels, rotation=45, ha="right")
        ax.grid(True, which='both', axis='x', linestyle='--', alpha=0.7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_children(self):
        
        # Clear existing entries in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch all children from the database
        children = common_db_utils.get_all_children()  # Fetch children using the newly moved function

        # Insert children into the Treeview
        for child in children:
            self.tree.insert("", tk.END, values=(child[0], child[1], child[3], child[5]))

         # Automatically select the first child after loading
        if children:
            first_child_id = children[0][0]  # Get the ID of the first child
            first_item = self.tree.get_children()[0]  # Get the first item in the Treeview
            self.tree.selection_set(first_item)  # Select the first item
            self.on_treeview_select(None)  # Trigger the info box update for the first student

    def on_treeview_select(self, event):
        """Updates the student info display when a student is selected in the Treeview."""
    
        selected_item = self.tree.selection()

        if selected_item:
            item = self.tree.item(selected_item[0])
            id = item['values'][0]
    
            # Fetch the full student data from the database
            student_data = children_db_utils.get_child(id)
            schedule_data = children_db_utils.get_schedule(id)

            if student_data:
                # Unpack values with handling for None (NULL) in the database
                first_name, middle_name, last_name, birth_date, year_group, g1_fname, g1_lname, g1_no, g1_email, g2_fname, g2_lname, g2_no = student_data

                # Set default values for missing fields (None or NULL in database)
                first_name = first_name or "N/A"
                middle_name = middle_name or "N/A"
                last_name = last_name or "N/A"
                birth_date = birth_date or "N/A"
                year_group = year_group or "N/A"
                g1_fname = g1_fname or "N/A"
                g1_lname = g1_lname or "N/A"
                g1_no = g1_no or "N/A"
                g1_email = g1_email or "N/A"
                g2_fname = g2_fname or "N/A"
                g2_lname = g2_lname or "N/A"
                g2_no = g2_no or "N/A"

                # Update the info box with additional data using the label-value pairs
                self.first_name_pair[1].config(text=first_name)
                self.middle_name_pair[1].config(text=middle_name)
                self.last_name_pair[1].config(text=last_name)
                self.dob_pair[1].config(text=birth_date)
                self.year_group_pair[1].config(text=year_group)

                self.guardian_one_fname_pair[1].config(text=g1_fname)
                self.guardian_one_lname_pair[1].config(text=g1_lname)
                self.guardian_one_contactNo_pair[1].config(text=g1_no)
                self.guardian_one_email_pair[1].config(text=g1_email)
                self.guardian_two_fname_pair[1].config(text=g2_fname)
                self.guardian_two_lname_pair[1].config(text=g2_lname)
                self.guardian_two_contactNo_pair[1].config(text=g2_no)

            # Convert schedule data into a dictionary
            days_of_week = ['mon', 'tue', 'wed', 'thu', 'fri']
            schedule_dict = {}

            for i, day in enumerate(days_of_week):
                arrival_time = schedule_data[i*2]  # arrival time is at even indices (0, 2, 4, etc.)
                finish_time = schedule_data[i*2 + 1]  # finish time is at odd indices (1, 3, 5, etc.)

                if arrival_time and finish_time:
                    schedule_dict[day.capitalize()] = (arrival_time, finish_time)
                else:
                    schedule_dict[day.capitalize()] = None
            full_name = first_name + " " + last_name
            # Call the create_schedule_chart method to display the chart
            self.create_schedule_chart(full_name, schedule_dict)

    def edit_child_info(self):
        """Open a pop-up window to edit the child info."""
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            return

        child_id = self.tree.item(selected_item[0])['values'][0]

        child_data = children_db_utils.get_child(child_id)

        if not child_data:
            messagebox.showerror("Error", "No child found with this ID.")
            return
        
        # Create the root window
        root = tk.Tk()
        root.title("Edit Child Information")
        
        # Create labels and entry widgets
        labels = ["First Name", "Middle Name", "Last Name", "Birth Date", "Year Group",
                  "Guardian 1 First Name", "Guardian 1 Last Name", "Guardian 1 Contact No.", "Guardian 1 Email",
                  "Guardian 2 First Name", "Guardian 2 Last Name", "Guardian 2 Contact No."]
        
        entries = []
        
        for idx, label in enumerate(labels):
            tk.Label(root, text=label).grid(row=idx, column=0, padx=10, pady=5)
            entry = tk.Entry(root)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries.append(entry)
        
        # Pre-fill the fields with existing data
        for idx, entry in enumerate(entries):
            value = child_data[idx] if child_data[idx] is not None else ""
            entry.insert(0, value)

        def submit_edits():
            # Get the edited data from the fields
            edited_data = [entry.get() for entry in entries]
    
            # Convert empty strings to None before saving to the database
            edited_data = [None if value == "" else value for value in edited_data]
    
            # Save the data to the DB
            children_db_utils.save_edited_child_info(child_id, *edited_data)
            self.load_children()
            root.destroy()

        # Add a submit button
        submit_button = tk.Button(root, text="Save Changes", command=submit_edits)
        submit_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def edit_child_schedule(self):
        """Open a pop-up window to edit the child schedule."""
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "No item selected.")
            return

        child_id = self.tree.item(selected_item[0])['values'][0]
        child_data = children_db_utils.get_schedule(child_id)

        if not child_data:
            messagebox.showerror("Error", "No child found with this ID.")
            return

        root = tk.Toplevel()
        root.title("Edit Child Schedule Info")
        root.grab_set()

        labels = [
            "Monday Start", "Monday Finish",
            "Tuesday Start", "Tuesday Finish",
            "Wednesday Start", "Wednesday Finish",
            "Thursday Start", "Thursday Finish",
            "Friday Start", "Friday Finish"
        ]

        entries = []
        time_slots = ["N/A"] + clock_utils.generate_time_slots("7:30", "18:00", 15)

        for idx, label in enumerate(labels):
            tk.Label(root, text=label).grid(row=idx, column=0, padx=10, pady=5)
            entry = ttk.Combobox(root, values=time_slots, font=("Arial", 12), state="readonly", width=15)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries.append(entry)

        for idx, entry in enumerate(entries):
            value = child_data[idx] if child_data[idx] is not None else "N/A"
            entry.set(value)

        def submit_edits():
            
            edited_data = [entry.get() for entry in entries]

            time_format = "%H:%M"
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

            for i, day in enumerate(weekdays):
                start = edited_data[i * 2]
                end = edited_data[i * 2 + 1]

                if (start == "N/A" and end != "N/A") or (start != "N/A" and end == "N/A"):
                    messagebox.showerror("Invalid Input", f"{day}: Both times must be set or both must be N/A.")
                    return

                if start != "N/A" and end != "N/A":
                    try:
                        start_time = datetime.strptime(start, time_format)
                        end_time = datetime.strptime(end, time_format)
                        if start_time >= end_time:
                            messagebox.showerror("Invalid Time", f"{day}: Start time must be before end time.")
                            return
                    except ValueError:
                        messagebox.showerror("Invalid Format", f"{day}: Time must be in HH:MM format.")
                        return

            edited_data = [None if val == "" else val for val in edited_data]

            children_db_utils.save_edited_child_schedule(child_id, *edited_data)
            self.load_children()
            root.destroy()

        submit_button = tk.Button(root, text="Save Changes", command=submit_edits)
        submit_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_child(self):
        # Get the currently selected item in the Treeview
        selected_item = self.tree.selection()

        # Check if any item is selected
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a child to delete.")
            return

        # Retrieve the ID of the selected item (Assuming the ID is stored in the first column)
        child_id = self.tree.item(selected_item[0])['values'][0]  # Assuming the ID is in the first column
        child_name = self.tree.item(selected_item[0])['values'][1]
        # Ask for confirmation to delete
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {child_name}?")

        item_id = int(child_id)
    
        
        if confirm:
            # Call the delete_child_from_db function to delete the item
            children_db_utils.delete_child_from_db(item_id)

            self.tree.delete(selected_item[0])

    def sort_children(self, column, reverse=False):
        """Sort the Treeview by the selected column."""
        # Get all items from the Treeview
        items = [(self.tree.item(item)['values'], item) for item in self.tree.get_children()]

        # Define sorting function with safety checks
        def sort_key(values):
            # Ensure we have enough values before accessing
            if len(values) <= column:
                return '' if column != 0 else float('inf')
        
            col_value = values[column]
        
            # If it's the first column (ID), sort numerically
            if column == 0:
                try:
                    return int(col_value)  # Ensure ID is sorted numerically
                except ValueError:
                    return float('inf')  # In case the ID is not a number
            else:
                # Sort alphabetically for all other columns
                return str(col_value).lower()  # Case-insensitive sorting
    
        # Sort the items based on the selected column and reverse order
        items.sort(key=lambda item: sort_key(item[0]), reverse=reverse)
    
        # Rearrange the items in sorted order
        for idx, (values, item) in enumerate(items):
            self.tree.move(item, '', idx)

        # Toggle the sort order for the next click
        self.tree.heading(column,
                     command=lambda c=column: self.sort_children(c, not reverse))

    def validate_email(self, email):    
        # Validate the email format using a regular expression
        
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        
        if re.fullmatch(email_pattern, email):
            return True
        else:
            return False
    
    def toggle_day(self, day):
        """Toggle the attendance for a specific day."""
        is_present = self.day_toggles[day].instate(['selected'])

        # Update the state of Arrival and Finish fields
        self.set_day_to_na(day, not is_present)

    def set_day_to_na(self, day, is_disabled):
        """Set the Arrival and Finish fields to 'N/A' and disable them if the day is unselected."""
        if is_disabled:
            # Disable the combo boxes and set the value to 'N/A'
            self.arrival_entries[day].set('N/A')
            self.finish_entries[day].set('N/A')
            self.arrival_entries[day].config(state="disabled")
            self.finish_entries[day].config(state="disabled")
        else:
            # Enable the combo boxes and reset to default value
            self.arrival_entries[day].config(state="normal")
            self.finish_entries[day].config(state="normal")
            self.arrival_entries[day].set(clock_utils.generate_time_slots("7:30", "18:00", 15)[0])  # Default to 7:30 AM
            self.finish_entries[day].set(clock_utils.generate_time_slots("7:30", "18:00", 15)[0])  # Default to 7:30 AM

    def add_new_child(self):
        """Initiate the process of adding a new child."""
        # Enable the "Child Information" tab and disable the "Control Panel" tab
        self.notebook.tab(self.child_info_frame, state='normal')  # Enable the "Child Info" tab
        self.notebook.select(self.child_info_frame)  # Switch to the "Child Info" tab
    
        # Disable the "Control Panel" tab to prevent navigation there
        self.notebook.tab(self.child_control_panel_frame, state='disabled')  # Disable the "Control Panel" tab

        # Disable the "Weekly Schedule" tab until the user completes the Child Info tab
        self.notebook.tab(self.schedule_frame, state='disabled')  # Disable the "Schedule" tab

    def cancel_process(self):
        """Cancel the whole process and reset the forms."""
        # Reset all forms
        self.clear_form()

        # Disable tabs and go back to control panel
        self.notebook.tab(self.child_control_panel_frame, state='normal')
        self.notebook.select(self.child_control_panel_frame)
        self.notebook.tab(self.child_info_frame, state='disabled')
        self.notebook.tab(self.schedule_frame, state='disabled')

    def next_to_schedule(self):
        """Check the required fields in the child info tab and go to schedule tab."""
        # Get all values from the form fields
        first_name = self.first_name_entry.get()
        middle_name = self.middle_name_entry.get()
        last_name = self.last_name_entry.get()
        birth_date = self.date_of_birth_entry.get()
        year_group = self.year_group_entry.get()
        guardian_one_fname = self.guardian_one_fname_entry.get()
        guardian_one_lname = self.guardian_one_lname_entry.get()
        guardian_one_contact_no = self.guardian_one_contact_no_entry.get()
        guardian_one_email = self.guardian_one_email_entry.get()
        guardian_two_fname = self.guardian_two_fname_entry.get()
        guardian_two_lname = self.guardian_two_lname_entry.get()
        guardian_two_contact_no = self.guardian_two_contact_no_entry.get()

        # Map the entry widgets to their respective field names
        field_names = {
            self.first_name_entry: "First Name",
            self.last_name_entry: "Last Name",
            self.guardian_one_fname_entry: "Guardian 1 First Name",
            self.guardian_one_lname_entry: "Guardian 1 Last Name",
            self.guardian_one_contact_no_entry: "Guardian 1 Contact No",
            self.guardian_one_email_entry: "Guardian 1 Email"
        }
    
        # Validate required fields
        required_fields = {
            self.first_name_entry: first_name,
            self.last_name_entry: last_name,
            self.guardian_one_fname_entry: guardian_one_fname,
            self.guardian_one_lname_entry: guardian_one_lname,
            self.guardian_one_contact_no_entry: guardian_one_contact_no,
            self.guardian_one_email_entry: guardian_one_email
    }
    
        # Check for missing required fields
        missing_fields = [field for field, value in required_fields.items() if not value.strip()]
    
        if missing_fields:
            # Get the names of the missing fields from the field_names mapping
            missing_field_names = [field_names[field] for field in missing_fields]
            messagebox.showerror("Error", f"The following required fields are missing:\n{', '.join(missing_field_names)}")
            return
        
        # Validate email format
        if not self.validate_email(guardian_one_email):
            messagebox.showerror("Error", "Invalid Guardian 1 email format")
            self.guardian_one_email_entry.focus_set()  # Focus on the invalid email field
            return

        # If validation is successful, enable the next tab
        self.notebook.tab(self.schedule_frame, state='normal')
        self.notebook.select(self.schedule_frame)

    def back_to_child_info(self):
        """Go back to child info tab."""
        self.notebook.tab(self.schedule_frame, state='disabled')
        self.notebook.select(self.child_info_frame)

    def finish_process(self):
        """Persist the data to the database."""
        # Get all the data from the forms (child info and schedule info)

        first_name = self.first_name_entry.get()
        middle_name = self.middle_name_entry.get()
        last_name = self.last_name_entry.get()
        birth_date = self.date_of_birth_entry.get()
        year_group = self.year_group_entry.get()
        guardian_one_fname = self.guardian_one_fname_entry.get()
        guardian_one_lname = self.guardian_one_lname_entry.get()
        guardian_one_contact_no = self.guardian_one_contact_no_entry.get()
        guardian_one_email = self.guardian_one_email_entry.get()
        guardian_two_fname = self.guardian_two_fname_entry.get()
        guardian_two_lname = self.guardian_two_lname_entry.get()
        guardian_two_contact_no = self.guardian_two_contact_no_entry.get()

        # Validate schedule for all days before saving
        time_format = "%H:%M"
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            start = self.arrival_entries[day].get()
            end = self.finish_entries[day].get()

            if (start == "N/A" and end != "N/A") or (start != "N/A" and end == "N/A"):
                messagebox.showerror("Invalid Input", f"{day}: Both times must be set or both must be N/A.")
                return

            if start != "N/A" and end != "N/A":
                try:
                    start_time = datetime.strptime(start, time_format)
                    end_time = datetime.strptime(end, time_format)
                    if start_time >= end_time:
                        messagebox.showerror("Invalid Time", f"{day}: Start time must be before end time.")
                        return
                except ValueError:
                    messagebox.showerror("Invalid Format", f"{day}: Time must be in HH:MM format.")
                    return

        # Get all the data from the schedule info form
        monday_arrival = self.arrival_entries["Monday"].get()
        monday_finish = self.finish_entries["Monday"].get()

        tuesday_arrival = self.arrival_entries["Tuesday"].get()
        tuesday_finish = self.finish_entries["Tuesday"].get()

        wednesday_arrival = self.arrival_entries["Wednesday"].get()
        wednesday_finish = self.finish_entries["Wednesday"].get()

        thursday_arrival = self.arrival_entries["Thursday"].get()
        thursday_finish = self.finish_entries["Thursday"].get()

        friday_arrival = self.arrival_entries["Friday"].get()
        friday_finish = self.finish_entries["Friday"].get()

        # Add child to database
        try:
            # Assuming add_child is a function that stores child info to the database
            children_db_utils.add_child(
                first_name, middle_name, last_name, birth_date, year_group,
                guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
                guardian_one_email, monday_arrival, monday_finish, 
                tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, 
                thursday_arrival, thursday_finish, friday_arrival, friday_finish, guardian_two_fname, 
                guardian_two_lname, guardian_two_contact_no
            )

            # Reload the list of children
            self.load_children()
            # Clear the form
            self.clear_form()
            
            # Go back to control panel
            self.notebook.tab(self.child_control_panel_frame, state='normal')
            self.notebook.select(self.child_control_panel_frame)
            self.notebook.tab(self.child_info_frame, state='disabled')
            self.notebook.tab(self.schedule_frame, state='disabled')
            messagebox.showinfo("Success", "Child and schedule information saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save child data: {str(e)}")

if __name__ == "__main__":
    app = Children()
    app.mainloop() 