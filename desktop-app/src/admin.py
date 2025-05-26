import tkinter as tk
from tkinter import ttk


from utils import navigation_utils, clock_utils
from utils.db_utils import admin_db_utils


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

        self.create_settings_window()

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

    def create_settings_window(self):   
        # Main container for settings
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Left side: Settings sections
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        settings_frame.columnconfigure(0, weight=1)

        # Right side: Staff list Treeview
        staff_list_frame = ttk.LabelFrame(main_frame, text="Staff Members", padding=(10, 10))
        staff_list_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        staff_list_frame.columnconfigure(0, weight=1)

        self.staff_tree = ttk.Treeview(
            staff_list_frame,
            columns=("username", "role", "is_admin", "is_active"),
            show="headings",
            height=25
        )

        self.staff_tree.heading("username", text="Username")
        self.staff_tree.heading("role", text="Role")
        self.staff_tree.heading("is_admin", text="Admin")
        self.staff_tree.heading("is_active", text="Active")
        self.staff_tree.column("username", width=120, anchor="w")
        self.staff_tree.column("role", width=120, anchor="center")
        self.staff_tree.column("is_admin", width=80, anchor="center")
        self.staff_tree.column("is_active", width=80, anchor="center")
        self.staff_tree.grid(row=0, column=0, sticky="nsew")

        # Populate the Treeview
        self.load_staff_members()

        # --- Admin Setup Section ---
        admin_frame = self.create_section(settings_frame, "Admin Setup", 0)
        ttk.Label(admin_frame, text="Replace master user with a secure admin account.").grid(row=0, column=0, sticky="w")
        ttk.Button(admin_frame, text="Create Admin User", command=lambda: self.create_user(1)).grid(row=1, column=0, sticky="w", pady=5)

        # --- Staff Management Section ---
        staff_frame = self.create_section(settings_frame, "Staff Accounts", 1)
        ttk.Label(staff_frame, text="Manage staff members for mobile login access.").grid(row=0, column=0, sticky="w")
        ttk.Button(staff_frame, text="Add Staff Member", command=lambda: self.create_user(0)).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Button(staff_frame, text="Edit Staff", command=lambda: self.edit_user()).grid(row=2, column=0, sticky="w", pady=5)

        # --- Printer Setup ---
        printer_frame = self.create_section(settings_frame, "Printer Setup", 2)
        ttk.Label(printer_frame, text="Configure your default printer for report printing.").grid(row=0, column=0, sticky="w")
        ttk.Button(printer_frame, text="Select Printer").grid(row=1, column=0, sticky="w", pady=5)

        # --- Email Configuration ---
        email_frame = self.create_section(settings_frame, "Email Configuration", 3)
        ttk.Label(email_frame, text="Set the email address used to send reports to parents.").grid(row=0, column=0, sticky="w")
        ttk.Entry(email_frame, width=40).grid(row=1, column=0, sticky="w")
        ttk.Button(email_frame, text="Save Email Settings").grid(row=2, column=0, sticky="w", pady=5)

        # --- Nursery Closure Days ---
        closure_frame = self.create_section(settings_frame, "Closure Days", 4)
        ttk.Label(closure_frame, text="Mark holidays or other closure days to block them on the calendar.").grid(row=0, column=0, sticky="w")
        ttk.Button(closure_frame, text="Add Closure Day").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Button(closure_frame, text="View/Edit Closure Days").grid(row=2, column=0, sticky="w", pady=5)

    def create_section(self, parent, title, row):
        """Creates a titled section frame within the parent frame."""
        section = ttk.LabelFrame(parent, text=title, padding=(10, 10))
        section.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        return section
    

    def create_user(self, user_type):

        print(f"{user_type}: admin")
        popup = tk.Toplevel(self)
        popup.title("Create Admin User")

        ttk.Label(popup, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        username_entry = ttk.Entry(popup)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        password_entry = ttk.Entry(popup, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Job Role:").grid(row=2, column=0, padx=10, pady=5)
        role_entry = ttk.Entry(popup)
        role_entry.grid(row=2, column=1, padx=10, pady=5)

        def handle_create(user_type):
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_entry.get().strip()
            success, msg = admin_db_utils.submit_admin(username, password, role, user_type)
            if success:
                tk.messagebox.showinfo("Success", msg)
                popup.destroy()
            else:
                tk.messagebox.showerror("Error", msg)

        ttk.Button(popup, text="Create", command=lambda: handle_create(user_type)).grid(row=3, column=0, columnspan=2, pady=10)

    def edit_user(self):

        selected_item = self.staff_tree.selection()
        if not selected_item:
            tk.messagebox.showerror("Error", "No user selected.")
            return

        selected_user = self.staff_tree.item(selected_item)["values"]
        if not selected_user or len(selected_user) < 3:
            tk.messagebox.showerror("Error", "Invalid user data.")
            return

        username_old = selected_user[0]
        password_old = selected_user[1]
        role_old = selected_user[2]

        popup = tk.Toplevel(self)
        popup.title("Edit User")

        ttk.Label(popup, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        username_entry = ttk.Entry(popup)
        username_entry.insert(0, username_old)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        password_entry = ttk.Entry(popup, show="*")
        password_entry.insert(0, password_old)
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Role:").grid(row=2, column=0, padx=10, pady=5)
        role_entry = ttk.Entry(popup)
        role_entry.insert(0, role_old)
        role_entry.grid(row=2, column=1, padx=10, pady=5)

        # Admin checkbox
        is_admin_var = tk.IntVar(value=1 if selected_user[3] else 0)  # Adjust index if needed
        admin_check = ttk.Checkbutton(popup, text="Make Admin", variable=is_admin_var)
        admin_check.grid(row=3, column=0, columnspan=2, pady=5)

        def handle_edit():
            new_username = username_entry.get().strip()
            new_password = password_entry.get().strip()
            new_role = role_entry.get().strip()
            user_type = is_admin_var.get()  # 1 if checked, 0 if not

            success, msg = admin_db_utils.edit_user(new_username, new_password, new_role, user_type)
            if success:
                tk.messagebox.showinfo("Success", msg)
                popup.destroy()
            else:
                tk.messagebox.showerror("Error", msg)

        ttk.Button(popup, text="Save Changes", command=handle_edit).grid(row=4, column=0, columnspan=2, pady=10)

    def load_staff_members(self):
        self.staff_tree.delete(*self.staff_tree.get_children())
        staff_list = admin_db_utils.get_all_staff()
        for user in staff_list:
            self.staff_tree.insert(
                "", "end",
                values=(user[1], user[3], "Yes" if user[4] == 1 else "No", "Yes" if user[5] == 1 else "No")
            )