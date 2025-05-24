import re

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

from utils import navigation_utils, clock_utils
from utils.db_utils import common_db_utils, children_db_utils, admin_db_utils

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

from PIL import Image, ImageTk

class Setting(tk.Toplevel):
    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent
        self.title("Settings")
        self.geometry("1400x900")
        self.lift()

        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Main area

        self.sidebar_frame = navigation_utils.create_global_sidebar(self)
        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)

        self.create_settings_window()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

    def create_settings_window(self):
        # Main container for settings
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)

        # Admin Setup Section
        admin_frame = self.create_section(main_frame, "Admin Setup", 0)
        ttk.Label(admin_frame, text="Replace master user with a secure admin account.").grid(row=0, column=0, sticky="w")
        ttk.Button(admin_frame, text="Create Admin User", command=self.create_admin_user).grid(row=1, column=0, sticky="w")

        # Staff Management Section
        staff_frame = self.create_section(main_frame, "Staff Accounts", 1)
        ttk.Label(staff_frame, text="Manage staff members for mobile login access.").grid(row=0, column=0, sticky="w")
        ttk.Button(staff_frame, text="Add Staff Member").grid(row=1, column=0, sticky="w")
        ttk.Button(staff_frame, text="View/Edit Staff").grid(row=2, column=0, sticky="w")

        # Printer Setup Section
        printer_frame = self.create_section(main_frame, "Printer Setup", 2)
        ttk.Label(printer_frame, text="Configure your default printer for report printing.").grid(row=0, column=0, sticky="w")
        ttk.Button(printer_frame, text="Select Printer").grid(row=1, column=0, sticky="w")

        # Email Configuration Section
        email_frame = self.create_section(main_frame, "Email Configuration", 3)
        ttk.Label(email_frame, text="Set the email address used to send reports to parents.").grid(row=0, column=0, sticky="w")
        ttk.Entry(email_frame, width=40).grid(row=1, column=0, sticky="w")
        ttk.Button(email_frame, text="Save Email Settings").grid(row=2, column=0, sticky="w", pady=5)

        # Nursery Closure Days Section
        closure_frame = self.create_section(main_frame, "Closure Days", 4)
        ttk.Label(closure_frame, text="Mark holidays or other closure days to block them on the calendar.").grid(row=0, column=0, sticky="w")
        ttk.Button(closure_frame, text="Add Closure Day").grid(row=1, column=0, sticky="w")
        ttk.Button(closure_frame, text="View/Edit Closure Days").grid(row=2, column=0, sticky="w")

    def create_section(self, parent, title, row):
        """Creates a titled section frame within the parent frame."""
        section = ttk.LabelFrame(parent, text=title, padding=(10, 10))
        section.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        return section
    

    def create_admin_user(self):
        popup = tk.Toplevel(self)
        popup.title("Create Admin User")

        ttk.Label(popup, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        username_entry = ttk.Entry(popup)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        password_entry = ttk.Entry(popup, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        def handle_create():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            success, msg = admin_db_utils.submit_admin(username, password)
            if success:
                tk.messagebox.showinfo("Success", msg)
                popup.destroy()
            else:
                tk.messagebox.showerror("Error", msg)
                #TODO user created admin but master not removed as admin, and login doesnt verify if is admin anyeway

        ttk.Button(popup, text="Create", command=handle_create).grid(row=2, column=0, columnspan=2, pady=10)