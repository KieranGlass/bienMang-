import tkinter as tk
from tkinter import ttk
import sqlite3

from session_manager import SessionManager

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("Bien Manger - Login")
        self.geometry("400x300")
        self.configure(bg="#d9f1fb")
        self.resizable(False, False)
    
        # Create main frame that fills the window
        self.main_frame = ttk.Frame(self)
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
    
        # Create login frame inside main frame
        self.login_frame = ttk.Frame(self.main_frame, padding="20", style="dayInfoBackground.TFrame")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
        # Configure grid weights for proper expansion
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
    
        self.create_login_widgets()

    def create_login_widgets(self):
        # Center title label
        title_label = ttk.Label(self.login_frame, text="Login", font=("Arial", 16, "bold"), background="#003366", foreground="white")
        title_label.grid(row=0, column=0, pady=20)
    
        # Center username section
        ttk.Label(self.login_frame, text="Username:", font=("Arial", 14, "bold"), background="#003366", foreground="white").grid(row=1, column=0, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=2, column=0, pady=5, sticky='ew')
    
        # Center password section
        ttk.Label(self.login_frame, text="Password:", font=("Arial", 14, "bold"), background="#003366", foreground="white").grid(row=3, column=0, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=4, column=0, pady=5, sticky='ew')
    
        # Center login button
        ttk.Button(self.login_frame, text="Login", command=self.login, style="login.TButton").grid(row=5, column=0, pady=20)
    
        # Configure grid weights for proper expansion
        self.login_frame.grid_columnconfigure(0, weight=1)

    def login(self):
        if self.username_entry.get() and self.password_entry.get():
            username = self.username_entry.get()
            password = self.password_entry.get()

            conn = sqlite3.connect('/database/bien-manger.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                is_admin = user[4]

                if is_admin == 1:
                    # Import and open dashboard
                    from dashboard import Dashboard
                    SessionManager.current_user = user
                    self.withdraw()
                    Dashboard(self.parent, self)
                else:
                    ttk.Label(self.login_frame, text="User is not admin", foreground="red").grid(row=6, column=0)
            else:
                ttk.Label(self.login_frame, text="Invalid username or password", foreground="red").grid(row=6, column=0)
        else:
            ttk.Label(self.login_frame, text="Please fill in both fields", foreground="red").grid(row=6, column=0)