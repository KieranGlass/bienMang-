import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

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
        cursor.execute("SELECT first_name, middle_name, last_name, birth_date, guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, guardian_two_fname, guardian_two_lname, guardian_two_contact_no FROM children WHERE id=?", (ID,))
        child_data = cursor.fetchone() 
    return child_data

def add_child(first_name, last_name, birth_date): #TODO - bUILD UP THIS METHOD!!
    """Add a child to the database."""
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
        INSERT INTO children (first_name, last_name, birth_date)
        VALUES (?, ?, ?)
        ''', (first_name, last_name, birth_date))
        conn.commit()

class Children(tk.Tk):
    
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

        self.create_local_sidebar()

        self.create_global_sidebar()

        self.create_pupil_list()

        self.create_pupil_info()

        self.add_child_button()

        # Bind selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Load and display all children from the database
        self.load_children()
        
    def add_child_button(self):
        add_child_button = ttk.Button(self, text="Add Child", command=self.add_child)
        add_child_button.grid(row=1, column=1, padx=10, pady=20, sticky="w")

    def create_local_sidebar(self):
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
        sidebar_frame = ttk.Frame(self)
        sidebar_frame.grid(row=1, column=0, rowspan=2, padx=0, pady=0, sticky="nswe") 

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

    def create_sidebar_tab(self, sidebar_frame, label, command, row):
        """ Helper function to create a tab (button) in the sidebar """
        tab_button = ttk.Button(sidebar_frame, text=label, command=command, style="Sidebar.TButton")
        tab_button.grid(row=row, column=0, padx=10, pady=10, sticky="w")

    def create_pupil_list(self):
        # Add the Treeview widget to display children (Row 2, Right column)
        self.tree = ttk.Treeview(self, columns=("Id", "First Name", "Last Name"), show="headings")
        self.tree.grid(row=1, column=2, columnspan=1, padx=0, pady=0, sticky="nsew")
        self.tree.heading("Id", text="Id")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")

    def create_pupil_info(self):
        # Add the info box in the middle column (with border)
        self.info_frame = ttk.Frame(self, relief="solid", borderwidth=2)
        self.info_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

        # Configure grid to divide the info_frame into two columns and two rows
        self.info_frame.grid_rowconfigure(0, weight=1)  # First row will take up half of the vertical space
        self.info_frame.grid_rowconfigure(1, weight=1)  # Second row will take up the bottom half
        self.info_frame.grid_columnconfigure(0, weight=1)  # Left column will take up half of the horizontal space
        self.info_frame.grid_columnconfigure(1, weight=2)  # Right column will take up the other half

        # ---------------- Left Half ----------------
        # Add the image box (top half of the left side)
        self.image_frame = ttk.Frame(self.info_frame, relief="solid", borderwidth=1, height=100, width=100)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
        """ # Placeholder for the image (you can load an image later)
        self.image_label = ttk.Label(self.image_frame, text="Image Placeholder", width=10, height=5, anchor="center")
        self.image_label.grid(row=0, column=0, padx=10, pady=10) """

        # Add the name and dob fields (bottom half of the left side)
        self.name_frame = ttk.Frame(self.info_frame)
        self.name_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # First name label
        self.first_name_label = ttk.Label(self.name_frame, text="First Name: ")
        self.first_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # middle name label
        self.middle_name_label = ttk.Label(self.name_frame, text="Middle Name: ")
        self.middle_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Last name label
        self.last_name_label = ttk.Label(self.name_frame, text="Last Name: ")
        self.last_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Date of birth label
        self.dob_label = ttk.Label(self.name_frame, text="Date of Birth: ")
        self.dob_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # ---------------- Right Half ----------------
        # Placeholder for additional information labels (Right half will have 7 labels)
        self.additional_info_frame = ttk.Frame(self.info_frame)
        self.additional_info_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Add 7 placeholder labels for additional information
        # First name Guardian 1 
        self.guardian_one_fname_label = ttk.Label(self.additional_info_frame, text="Guardian 1 First Name: ")
        self.guardian_one_fname_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # Last name Guardian 1
        self.guardian_one_lname_label = ttk.Label(self.additional_info_frame, text="Guardian 1 Last Name: ")
        self.guardian_one_lname_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        # Contact Number Guardian 1
        self.guardian_one_contactNo_label = ttk.Label(self.additional_info_frame, text="Guardian 1 Contact Number: ")
        self.guardian_one_contactNo_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        # Email Guardian 1
        self.guardian_one_email_label = ttk.Label(self.additional_info_frame, text="Guardian 1 Email: ")
        self.guardian_one_email_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        # First name Guardian 2
        self.guardian_two_fname_label = ttk.Label(self.additional_info_frame, text="Guardian 2 First Name: ")
        self.guardian_two_fname_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        # Last name Guardian 1
        self.guardian_two_lname_label = ttk.Label(self.additional_info_frame, text="Guardian 2 Last Name: ")
        self.guardian_two_lname_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        # Contact Number Guardian 2
        self.guardian_two_contactNo_label = ttk.Label(self.additional_info_frame, text="Guardian 2 Contact Number: ")
        self.guardian_two_contactNo_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

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
            self.tree.insert("", tk.END, values=(child[0], child[1], child[3]))

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
                first_name, middle_name, last_name, birth_date, g1_fname, g1_lname, g1_no, g1_email, g2_fname, g2_lname, g2_no = student_data

                # Set default values for missing fields (None or NULL in database)
                first_name = first_name or "N/A"
                middle_name = middle_name or "N/A"
                last_name = last_name or "N/A"
                birth_date = birth_date or "N/A"
                g1_fname = g1_fname or "N/A"
                g1_lname = g1_lname or "N/A"
                g1_no = g1_no or "N/A"
                g1_email = g1_email or "N/A"
                g2_fname = g2_fname or "N/A"
                g2_lname = g2_lname or "N/A"
                g2_no = g2_no or "N/A"

                # Update the info box with additional data
                self.first_name_label.config(text=f"First Name: {first_name}")
                self.middle_name_label.config(text=f"Middle Name: {middle_name}")
                self.last_name_label.config(text=f"Last Name: {last_name}")
                self.dob_label.config(text=f"Date of Birth: {birth_date}")
                self.guardian_one_fname_label.config(text=f"Guardian 1 First Name: {g1_fname}")
                self.guardian_one_lname_label.config(text=f"Guardian 1 Last Name: {g1_lname}")
                self.guardian_one_contactNo_label.config(text=f"Guardian 1 Contact No: {g1_no}")
                self.guardian_one_email_label.config(text=f"Guardian 1 Email: {g1_email}")
                self.guardian_two_fname_label.config(text=f"Guardian 2 First Name: {g2_fname}")
                self.guardian_two_lname_label.config(text=f"Guardian 2 Last Name: {g2_lname}")
                self.guardian_two_contactNo_label.config(text=f"Guardian 2 Contact No: {g2_no}")

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


if __name__ == "__main__":
    app = Children()
    app.mainloop()  # Starts the Tkinter event loop