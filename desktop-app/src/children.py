import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

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

def add_child(first_name, last_name, birth_date):
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
        
    def create_title_label(self):
        # Create a title label at the top of the window
        title_label = tk.Label(self, text="Current Pupils", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

    def create_children_window(self):

        self.create_title_label()

        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        dashboard_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Ensure that the main window grid can grow as needed
        self.grid_rowconfigure(1, weight=1)  # Allow the row with the frame to expand
        self.grid_columnconfigure(0, weight=1)  # Left side (for button)
        self.grid_columnconfigure(1, weight=2)  # Right side (for Treeview)

        # Ensure the dashboard_frame expands with the window
        dashboard_frame.grid_rowconfigure(0, weight=1)  # Allow the row with the Treeview to expand
        dashboard_frame.grid_columnconfigure(0, weight=1)  # Left column (for button)
        dashboard_frame.grid_columnconfigure(1, weight=2)  # Right column (for Treeview)

        # Add the "Add Child" button (Left half)
        add_child_button = ttk.Button(dashboard_frame, text="Add Child", command=self.add_child)
        add_child_button.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Add the Treeview widget to display children (Right half)
        self.tree = ttk.Treeview(dashboard_frame, columns=("First Name", "Last Name"), show="headings")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.grid(row=0, column=1, sticky="nsew")  # Right side Treeview

        # Load and display all children from the database
        self.load_children()

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()

    # Loads all children from the database and displays them in the Treeview.
    def load_children(self):
        """Loads all children from the database and displays them in the Treeview."""
        # Clear existing entries in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch all children from the database
        children = get_all_children()  # Fetch children using the newly moved function

        # Insert children into the Treeview
        for child in children:
            self.tree.insert("", tk.END, values=(child[1], child[2]))

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