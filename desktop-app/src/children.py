import sqlite3
import re
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkcalendar import DateEntry

from PIL import Image, ImageTk

from styles import apply_styles

def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_all_children():
    """Fetch all children records from the database."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM children")
        children = cursor.fetchall()
    return children

def get_child(ID):
    """Fetch a complete child record from the database using the child's ID."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT first_name, middle_name, last_name, birth_date, year_group, guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, guardian_two_fname, guardian_two_lname, guardian_two_contact_no FROM children WHERE id=?", (ID,))
        child_data = cursor.fetchone() 
    return child_data

def add_child(
    first_name, middle_name, last_name, birth_date, year_group,
    guardian_one_fname, guardian_one_lname, guardian_one_contact_no, 
    guardian_one_email, guardian_two_fname=None, guardian_two_lname=None,
    guardian_two_contact_no=None):

    """Add a child to the database with all required fields."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            INSERT INTO children (
                first_name, middle_name, last_name, birth_date, year_group,
                guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
                guardian_one_email, guardian_two_fname, guardian_two_lname,
                guardian_two_contact_no
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, middle_name, last_name, birth_date, year_group,
            guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
            guardian_one_email, guardian_two_fname, guardian_two_lname,
            guardian_two_contact_no
        ))
        conn.commit()

class Children(tk.Toplevel):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Pupil list...")
        self.title("Current Pupils")
        self.geometry("1400x900")
        self.deiconify()
        self.lift()
        self.create_children_window()      

    def create_children_window(self):

        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        #dashboard_frame.grid(row=2, column=3, sticky="nsew")

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

        self.create_global_sidebar()

        self.delete_child_button = ttk.Button(self, text="Delete Child", command=self.delete_child)
        self.delete_child_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.create_add_new_child_frame() # "/app/src/resources/images/settings.PNG"

        self.create_pupil_list()

        self.create_pupil_info()

        # Bind selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Load and display all children from the database
        self.load_children()

    def create_add_new_child_frame(self):
        """Create the bordered frame for buttons and child input fields in the bottom row."""
        button_frame = ttk.Frame(self, relief="raised", borderwidth=2)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Add the Add Child button
        self.add_child_button = ttk.Button(button_frame, text="Add Child", 
                                       command=self.add_child_validation)
        self.add_child_button.grid(row=0, column=0, columnspan=12, pady=10, sticky="w")

    
        # Configure grid to create a form layout
        for i in range(2):  # 2 columns for labels and entries
            button_frame.grid_columnconfigure(i, weight=1)

        # Create a frame for labels and entries
        labels_frame = ttk.Frame(button_frame)
        labels_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

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
            elif label == "Year Group":
                #Year Group dropdown (combobox)
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

    def clear_form(self):
        """Clear all form fields."""
        for attr in dir(self):
            if attr.endswith('_entry'):
                getattr(self, attr).delete(0, tk.END)

    def add_child_validation(self):
        """Add a new child using the form fields."""
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
    
        # Validate required fields
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Date of Birth': birth_date,
            'Year Group': year_group,
            'Guardian 1 First Name': guardian_one_fname,
            'Guardian 1 Last Name': guardian_one_lname,
            'Guardian 1 Contact No': guardian_one_contact_no,
            'Guardian 1 Email': guardian_one_email
        }
    
        # Check for missing required fields
        missing_fields = [field for field, value in required_fields.items() 
                     if not value.strip()]
    
        if missing_fields:
            messagebox.showerror("Error", 
                f"The following required fields are missing:\n{', '.join(missing_fields)}")
            return
    
        # Validate email format
        if not self.validate_email(guardian_one_email):
            messagebox.showerror("Error", "Invalid Guardian 1 email format")
            return
    
        # Add child to database
        try:
            add_child(
                first_name, middle_name, last_name, birth_date, year_group,
                guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
                guardian_one_email, guardian_two_fname, guardian_two_lname,
                guardian_two_contact_no
            )
            # Reload the list of children
            self.load_children()
            # Clear the form
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add child: {str(e)}")

        """ Create the sidebar with tabs """
        # Sidebar container (frame)
        sidebar_frame = ttk.Frame(self)
        sidebar_frame.grid(row=0, column=0, rowspan=1, padx=0, pady=0, sticky="nswe") 

        # Set the background color for the sidebar
        sidebar_frame.configure(style="Sidebar.TFrame")

        # Tab buttons
        self.create_sidebar_tab(sidebar_frame, "Home", self.go_home, 0)
        self.create_sidebar_tab(sidebar_frame, "Tab 1", self.go_home, 1)
        self.create_sidebar_tab(sidebar_frame, "Tab 2", self.go_home, 2)
        self.create_sidebar_tab(sidebar_frame, "Tab 3", self.go_home, 3)
        self.create_sidebar_tab(sidebar_frame, "Tab 4", self.go_home, 4)
        self.create_sidebar_tab(sidebar_frame, "Tab 5", self.go_home, 5)
        self.create_sidebar_tab(sidebar_frame, "Tab 6", self.go_home, 6)

    def create_global_sidebar(self):
        """ Create the sidebar with tabs """
        # Sidebar container (frame)
        sidebar_frame = ttk.Frame(self, relief="raised")
        sidebar_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nswe")

        # Tab buttons
        self.create_sidebar_tab(sidebar_frame, "Home", self.go_home, 0)
        self.create_sidebar_tab(sidebar_frame, "Tab 1", self.go_home, 1)
        self.create_sidebar_tab(sidebar_frame, "Tab 2", self.go_home, 2)
        self.create_sidebar_tab(sidebar_frame, "Tab 3", self.go_home, 3)
        self.create_sidebar_tab(sidebar_frame, "Tab 4", self.go_home, 4)
        self.create_sidebar_tab(sidebar_frame, "Tab 5", self.go_home, 5)
        self.create_sidebar_tab(sidebar_frame, "Log Out", self.go_home, 6)

    def create_sidebar_tab(self, sidebar_frame, label, command, row):
        """ Helper function to create a tab (button) in the sidebar """
        tab_button = ttk.Button(sidebar_frame, text=label, command=command, style="Sidebar.TButton")
        tab_button.grid(row=row, column=0, padx=10, pady=10, sticky="w")

    def create_pupil_list(self):
        # Create a style for Treeview
        style = ttk.Style(self)
        style.configure("Treeview",
                    font=("Arial", 12),  # Set font size for better readability
                    rowheight=30,        # Set row height for bigger entries
                    padding=5)       
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        # Add the Treeview widget to display children (Row 2, Right column)
        self.tree = ttk.Treeview(self, columns=("Id", "First Name", "Last Name", "Year Group"), show="headings", style="Treeview")
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
        img = img.resize((210, 180))  # Resize image as needed
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

        self.edit_child_button = ttk.Button(self.name_frame, text="Edit Child", command=self.edit_child)
        self.edit_child_button.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

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
        pair_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

        # Configure this pair_frame to have equal width and height (boxes will be uniform size)
        parent_frame.grid_columnconfigure(col, weight=1, uniform="group1")
        parent_frame.grid_rowconfigure(row, weight=1)

        # Label part (displayed at the top of the box)
        label = ttk.Label(pair_frame, text=label_text, anchor="w", font=("Helvetica", 10, "bold"))
        label.pack(fill="x", pady=(0, 5))  # Label on top, with space below

        # Value part (displayed below the label in a different style)
        value = ttk.Label(pair_frame, text="--", anchor="w", font=("Arial", 10), wraplength=400)
        value.pack(fill="x", pady=(5, 5))  # Value below, with space above

        # Return both the label and value so they can be updated later
        return label, value

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

    def load_children(self):
        
        # Clear existing entries in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch all children from the database
        children = get_all_children()  # Fetch children using the newly moved function

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
            student_data = get_child(id)

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

    def add_child(self):
        """Prompts the user to enter child details and adds them to the database."""
        # Get the child's details from the user
        first_name = simpledialog.askstring("Input", "Enter the child's first name:")
        last_name = simpledialog.askstring("Input", "Enter the child's last name:")
        birth_date = simpledialog.askstring("Input", "Enter the child's birth date (YYYY-MM-DD):")

        if first_name and last_name and birth_date:
            # Insert the new child into the database
            add_child(first_name, last_name, birth_date)

            # Reload the list of children after adding
            self.load_children()

    def edit_child(self):
        """Prompts the user to enter child details and adds them to the database."""
        # Get the child's details from the user
        first_name = simpledialog.askstring("Input", "Enter the child's first name:")
        last_name = simpledialog.askstring("Input", "Enter the child's last name:")
        birth_date = simpledialog.askstring("Input", "Enter the child's birth date (YYYY-MM-DD):")

        if first_name and last_name and birth_date:
            # Insert the new child into the database
            add_child(first_name, last_name, birth_date)

            # Reload the list of children after adding
            self.load_children()

    def delete_child(self):
        """Prompts the user to enter child details and adds them to the database."""
        # Get the child's details from the user
        first_name = simpledialog.askstring("Input", "Enter the child's first name:")
        last_name = simpledialog.askstring("Input", "Enter the child's last name:")
        birth_date = simpledialog.askstring("Input", "Enter the child's birth date (YYYY-MM-DD):")

        if first_name and last_name and birth_date:
            # Insert the new child into the database
            add_child(first_name, last_name, birth_date)

            # Reload the list of children after adding
            self.load_children()

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
        
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        
        if re.match(email_pattern, email):
            return True
        else:
            return False

if __name__ == "__main__":
    app = Children()
    app.mainloop()  # Starts the Tkinter event loop