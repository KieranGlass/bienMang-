import tkinter as tk
from tkinter import ttk

from dashboard import Dashboard
from login import LoginWindow
from children import Children
from menus import Menus
from reports import Reports
from registers import Registers
from admin import Setting


def create_global_sidebar(app):
    """ Create the sidebar with tabs """
    # Sidebar container (frame)
    sidebar_frame = ttk.Frame(app, relief="raised")
    sidebar_frame.grid(row=0, column=0, rowspan=1, padx=0, pady=0, sticky="nsw")

    # Tab buttons
    create_sidebar_tab(sidebar_frame, "Dashboard", lambda: show_dashboard(app), 0)
    create_sidebar_tab(sidebar_frame, "Children", lambda: show_children(app), 1)
    create_sidebar_tab(sidebar_frame, "Registers", lambda: show_registers(app), 2)
    create_sidebar_tab(sidebar_frame, "Menus", lambda: show_menus(app), 3)
    create_sidebar_tab(sidebar_frame, "Reports", lambda: show_reports(app), 4)
    create_sidebar_tab(sidebar_frame, "Settings", lambda: show_settings(app), 5)
    create_sidebar_tab(sidebar_frame, "Log Out", lambda: log_out(app), 6)

    return sidebar_frame

def create_sidebar_tab(frame, text, command, row):
    """ Helper function to create each sidebar tab """
    tab_button = ttk.Button(frame, text=text, command=command)
    tab_button.grid(row=row, column=0, padx=10, pady=5, sticky="w")

    style = ttk.Style()
    style.configure(
        "Custom.TButton",
        background="#1e3a5f",
        foreground="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        padding=(10, 5),
        borderwidth=2,
        anchor="center",  
    )
    style.map("Custom.TButton", background=[("active", "#2c4b7f")])
    tab_button.configure(style="Custom.TButton")

def show_dashboard(self):
    print("Showing Dashboard")
    self.withdraw()
    dashboard_window = Dashboard(self, self.root_app)

def show_children(self):
    print("Showing children")
    self.withdraw()
    children_window = Children(self, self.root_app)
           
def show_registers(self):
    print("Showing registers")
    self.withdraw()
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

