import tkinter as tk


class DayInfoPage(tk.Toplevel):
    def __init__(self, parent, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date  # The date clicked on the calendar
        self.title(f"Details for {self.selected_date}")
        self.geometry("600x400")
        
        # Create a label for the day’s date
        self.date_label = tk.Label(self, text=f"Information for {self.selected_date}", font=("Helvetica", 16))
        self.date_label.pack(pady=10)

        # Create fields to display data (menu, register, etc.)
        self.menu_label = tk.Label(self, text="Menu: ", font=("Helvetica", 12))
        self.menu_label.pack(pady=5)

        self.menu_info = tk.Label(self, text="", font=("Helvetica", 12))  # To be populated with DB data
        self.menu_info.pack(pady=5)

        self.register_label = tk.Label(self, text="Register: ", font=("Helvetica", 12))
        self.register_label.pack(pady=5)

        self.register_info = tk.Label(self, text="", font=("Helvetica", 12))  # To be populated with DB data
        self.register_info.pack(pady=5)

        # Populate data for the selected date
        self.load_day_info(self.selected_date)

    def load_day_info(self, date):
        """ Fetch and populate data for the selected date from the database """
        
        # Example DB query to fetch information for the selected date
        # Replace with your actual DB fetching logic
        data = self.get_day_data_from_db(date)

        if data:
            # Update the UI with the fetched data
            self.menu_info.config(text=data['menu'])
            self.register_info.config(text=data['register'])
        else:
            # If no data, show a default message
            self.menu_info.config(text="No menu info available")
            self.register_info.config(text="No register info available")

    def get_day_data_from_db(self, date):
        """ Simulate fetching data from a database for the given date """
        # In a real app, this would be replaced with actual database logic
        example_data = {
            "2025-03-29": {'menu': 'Pasta', 'register': 'Register info for March 29'},
            "2025-03-30": {'menu': 'Salad', 'register': 'Register info for March 30'},
        }
        return example_data.get(date, None)  # Returns None if no data is found for the date