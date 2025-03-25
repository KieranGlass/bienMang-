import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
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


        self.create_global_sidebar()

        self.create_bottom_button_frame()

        self.create_pupil_list()

        self.create_pupil_info()

        # Bind selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Load and display all children from the database
        self.load_children()

    def create_bottom_button_frame(self):
        # Create the bordered frame for buttons in the bottom row of the middle column
        button_frame = ttk.Frame(self, relief="raised", borderwidth=2)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure the button frame grid
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        # Create the buttons inside the button frame
        self.add_child_button = ttk.Button(button_frame, text="Add Child", command=self.add_child)
        self.add_child_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.edit_child_button = ttk.Button(button_frame, text="Edit Child", command=self.edit_child)
        self.edit_child_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.delete_child_button = ttk.Button(button_frame, text="Delete Child", command=self.delete_child)
        self.delete_child_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

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
        self.tree.heading("Id", text="Id")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Year Group", text="Year Group")

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
        # Add the image box (top half of the left side)
        self.image_frame = ttk.Frame(self.info_frame, relief="solid", borderwidth=1, height=100, width=100)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
        # Load the placeholder image
        image_path = "/app/src/resources/images/placeholder.png"  # Full path
        try:
            self.image = Image.open(image_path)
            self.image = self.image.resize((100, 100))  # Resize to fit the label
            self.image_tk = ImageTk.PhotoImage(self.image)  # Convert to a Tkinter-compatible photo image

            # Create the image label using tk.Label instead of ttk.Label
            self.image_label = tk.Label(self.image_frame, image=self.image_tk, anchor="center")
            self.image_label.grid(row=0, column=0, padx=10, pady=10)

            # Keep a reference to the image so it doesn't get garbage collected
            self.image_label.image = self.image_tk
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label = tk.Label(self.image_frame, text="Image failed to load")
            self.image_label.grid(row=0, column=0, padx=10, pady=10)

        # Add the name and dob fields (bottom half of the left side)
        self.name_frame = ttk.Frame(self.info_frame)
        self.name_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Create label-value pairs for Left Half (Name and DOB)
        self.first_name_pair = self.create_label_value_pair(self.name_frame, "First Name", 0, 0)
        self.middle_name_pair = self.create_label_value_pair(self.name_frame, "Middle Name", 1, 0)
        self.last_name_pair = self.create_label_value_pair(self.name_frame, "Last Name", 2, 0)
        self.dob_pair = self.create_label_value_pair(self.name_frame, "Date of Birth", 3, 0)
        self.year_group_pair = self.create_label_value_pair(self.name_frame, "Year Group", 4, 0)

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
        value.pack(fill="x", pady=(5, 0))  # Value below, with space above

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

if __name__ == "__main__":
    app = Children()
    app.mainloop()  # Starts the Tkinter event loop