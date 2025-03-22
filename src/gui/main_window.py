import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        print("Initializing MainWindow...")
        self.title("Bien Mangé")
        self.geometry("1400x900")
        self.deiconify()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.lift()
        self.after(100, self.check_window)
        self.after(1000, self.maximize_window)

        # Add the title label
        self.create_title_label()

    def check_window(self):
        print(f"Window state: {self.state()}")
        print(f"Window position: {self.geometry()}")

    def maximize_window(self):
        print(f"Platform: {sys.platform}")
        if sys.platform == 'win32':
            print("Using Windows maximization")
            self.state('zoomed')
        elif sys.platform == 'darwin':
            print("Using macOS maximization")
            self.attributes('-zoomed', True)
        else:  # Linux
            print("Using Linux maximization")
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}+0+0")
            self.attributes('-fullscreen', True)
        print("Window maximized") 

    def create_navigation(self):
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill='x')
        ttk.Button(nav_frame, text="Dashboard").pack(side='left', padx=5)
        ttk.Button(nav_frame, text="Children").pack(side='left', padx=5)
        ttk.Button(nav_frame, text="Reports").pack(side='left', padx=5)

    def create_title_label(self):
        # Create a title label at the top of the window
        title_label = tk.Label(self, text="Bien Mangé", font=("Helvetica", 24))
        title_label.pack(pady=20)  # Adds some space above the title

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()