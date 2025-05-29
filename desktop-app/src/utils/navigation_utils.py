import tkinter as tk
from tkinter import ttk

from dashboard import Dashboard
from children import Children
from menus import Menus
from reports import Reports
from registers import Registers
from admin import Setting

from session_manager import SessionManager
from utils import clock_utils


def create_global_sidebar(app):
    """ Create the sidebar with tabs """
    # Sidebar container (frame)
    sidebar_frame = ttk.Frame(app, relief="raised", style="SidebarBackground.TFrame")
    sidebar_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")

    # Tab buttons
    create_sidebar_tab(sidebar_frame, "Dashboard", lambda: show_dashboard(app), 0)
    create_sidebar_tab(sidebar_frame, "Children", lambda: show_children(app), 1)
    create_sidebar_tab(sidebar_frame, "Registers", lambda: show_registers(app), 2)
    create_sidebar_tab(sidebar_frame, "Menus", lambda: show_menus(app), 3)
    create_sidebar_tab(sidebar_frame, "Reports", lambda: show_reports(app), 4)
    create_sidebar_tab(sidebar_frame, "Settings", lambda: show_settings(app), 5)
    create_sidebar_tab(sidebar_frame, "Log Out", lambda: log_out(app), 6)

    user = SessionManager.current_user

    user_label = tk.Label(sidebar_frame, text=f"User:\n{user[1]}", bg="#003366", fg="white")
    user_label.grid(row=7, column=0, pady=10)

    time_label = clock_utils.create_clock(sidebar_frame, app)
    time_label.grid(row=8, column=0, pady=10)
    
    return sidebar_frame

def create_sidebar_tab(frame, text, command, row):
    """ Helper function to create each sidebar tab """
    tab_button = ttk.Button(frame, text=text, command=command)
    tab_button.grid(row=row, column=0, padx=10, pady=5, sticky="w")

    tab_button.configure(style="Sidebar.TButton")

def show_dashboard(self):
    print("Showing Dashboard")
    self.withdraw()
    dashboard_window = Dashboard(self, self.root_app)

def show_children(self):
    print("Showing children")
    self.withdraw()
    children_window = Children(self, self.root_app)
           
def show_registers(self, selected_date = None):
    print("Showing registers")
    self.withdraw()
    if selected_date:
        registers_window = Registers(self, self.root_app, selected_date)
    else:
        registers_window = Registers(self, self.root_app)
            
def show_menus(self):
    print("Showing menus")
    self.withdraw()
    menus_window = Menus(self, self.root_app)
            
def show_reports(self):
    print("Showing reports")
    self.withdraw()
    reports_window = Reports(self, self.root_app) 
            
def show_settings(self):
    print("Showing settings")
    self.withdraw()
    settings_window = Setting(self, self.root_app) 

def log_out(window):
    window.destroy()
    window.root_app.deiconify()

def on_close(window):
    window.destroy()
    dashboard = Dashboard(window.root_app, window.root_app)
    dashboard.lift()

