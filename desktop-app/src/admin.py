import tkinter as tk
from tkinter import ttk

from utils import clock_utils, navigation_utils

class Setting(tk.Toplevel):
    
    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.parent = parent  # Store the Dashboard instance
        print("Initializing Settings...")
        self.title("Settings")
        self.geometry("1400x900")
        self.lift()
        self.create_settings_window()      

        self.protocol("WM_DELETE_WINDOW", lambda: navigation_utils.on_close(self))

    def create_settings_window(self):

        self.grid_columnconfigure(0, weight=1, minsize=200)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=4, minsize=600)  # Menu list (flexible)
    
        self.sidebar_frame = navigation_utils.create_global_sidebar(self)

        self.time_label = clock_utils.create_clock(self.sidebar_frame, self)


if __name__ == "__main__":
    app = Setting()
    app.mainloop()  # Starts the Tkinter event loop