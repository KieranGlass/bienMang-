import tkinter as tk
from tkinter import ttk

class Today(tk.Tk):
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard  # Store the Dashboard instance
        print("Initializing Today...")
        self.title("Today")
        self.geometry("1400x900")
        self.deiconify()
        self.lift()
        self.create_today_window()      
        
    def create_title_label(self):
        # Create a title label at the top of the window
        title_label = tk.Label(self, text="Today", font=("Helvetica", 24))
        title_label.pack(pady=20)  # Adds some space above the title

    def create_today_window(self):
        # Add a Home button
        home_button = ttk.Button(self, text="Home", command=self.go_home)
        home_button.pack(pady=20) 
        
        self.create_title_label()
    
        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        dashboard_frame.pack(fill='both', expand=True, padx=20, pady=20)

    def go_home(self):
        
        self.destroy()
        
        # Reopen the Dashboard window
        self.dashboard.deiconify()
        self.dashboard.lift()



if __name__ == "__main__":
    app = Today()
    app.mainloop()  # Starts the Tkinter event loop