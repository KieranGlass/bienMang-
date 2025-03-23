import os
import tkinter as tk
from login import LoginWindow
from PIL import Image, ImageTk
from tkinter import ttk
from pathlib import Path


class Dashboard(tk.Tk):
    
    def __init__(self):
        super().__init__()
        print("Initializing MainWindow...")
        self.title("Bien Manger")
        self.geometry("1400x900")
        self.deiconify()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.lift()
        self.create_dashboard()      
        
    def create_title_label(self):
        # Create a title label at the top of the window
        title_label = tk.Label(self, text="Bien Manger", font=("Helvetica", 24))
        title_label.pack(pady=20)  # Adds some space above the title

    def create_dashboard(self):
        print(f"Current working directory: {os.getcwd()}")
        print(f"Resources path: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')}")
        

        self.create_title_label()

        # Get absolute path to resources
        is_docker = os.path.exists('/.dockerenv')
    
        # Get the base path depending on the environment (Docker or local)
        if is_docker:
            # For Docker, the path is /app/src/resources
            resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
        else:
            # For local, it should be the same path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            resources_path = os.path.join(current_dir, 'resources')

        print(f"Running in: {'Docker' if is_docker else 'Local'} environment")
        print(f"Resources path: {resources_path}")
    
        # Create main frame for dashboard
        dashboard_frame = ttk.Frame(self)
        dashboard_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
        # Configure grid weights for proper expansion
        for i in range(3):
            dashboard_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            dashboard_frame.grid_rowconfigure(i, weight=1)
    
        # Define boxes configuration
        boxes = [
            {"label": "Today", "image": os.path.join(resources_path, "images/today.PNG"), "command": self.show_today},
            {"label": "Children", "image": os.path.join(resources_path, "images/children.PNG"), "command": self.show_children},
            {"label": "Registers", "image": os.path.join(resources_path, "images/registers.PNG"), "command": self.show_registers},
            {"label": "Menus", "image": os.path.join(resources_path, "images/menus.PNG"), "command": self.show_menus},
            {"label": "Reports", "image": os.path.join(resources_path, "images/reports.PNG"), "command": self.show_reports},
            {"label": "Settings", "image": os.path.join(resources_path, "images/settings.PNG"), "command": self.show_settings}
        ]
    
        # Create boxes in 2x3 grid
        for i, box in enumerate(boxes):
            row = i // 3
            col = i % 3
        
            # Create box frame
            box_frame = ttk.Frame(dashboard_frame, height=150, padding=10)
            box_frame.grid(row=row, column=col, sticky='nsew')
            box_frame.grid_propagate(False)
        
            # Configure box style
            style = ttk.Style()
            style.configure('Box.TFrame', 
                       background='lightgray',
                       relief='raised',          # Added raised relief
                       borderwidth=2,            # Added border width
                       padding=10)
            box_frame.configure(style='Box.TFrame')

            # Add hover effect
            box_frame.bind('<Enter>', lambda e, w=box_frame: self.on_hover(e, w))
            box_frame.bind('<Leave>', lambda e, w=box_frame: self.on_hover_leave(e, w))
        
            # Add click handler
            box_frame.bind('<1>', lambda e, cmd=box['command']: cmd())
        
            # Create box content frame
            content_frame = ttk.Frame(box_frame)
            content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
            try:
                image = Image.open(box['image'])
                image = image.resize((240, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = ttk.Label(content_frame, image=photo)
                image_label.image = photo
                image_label.pack(pady=(0, 10))
            except FileNotFoundError:
                print(f"Error: Image not found at path: {box['image']}")
                error_label = ttk.Label(content_frame, text="Image not found", foreground="red")
                error_label.pack(pady=(0, 10))
            except Exception as e:
                print(f"Error loading image: {str(e)}")
                error_label = ttk.Label(content_frame, text="Error loading image", foreground="red")
                error_label.pack(pady=(0, 10))

            # Add label
            label = ttk.Label(content_frame, text=box['label'], font=("Helvetica", 12))
            label.pack(pady=10)

    def on_hover(self, event, widget):
        # Create shadow effect by creating a dark border
        style = ttk.Style()
        style.configure('Hover.TFrame', 
                    background='lightgray',
                    relief='raised',
                    borderwidth=4,
                    padding=10)
        widget.configure(style='Hover.TFrame')

    def on_hover_leave(self, event, widget):
        # Return to normal state
        style = ttk.Style()
        style.configure('Box.TFrame', 
                    background='lightgray',
                    relief='raised',
                    borderwidth=2,
                    padding=10)
        widget.configure(style='Box.TFrame')

    def show_today(self):
        print("Showing today")
            

    def show_children(self):
        print("Showing children")
           

    def show_registers(self):
        print("Showing registers")
            

    def show_menus(self):
        print("Showing menus")
            

    def show_reports(self):
        print("Showing reports")
            

    def show_settings(self):
        print("Showing settings")
            

def main():
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()