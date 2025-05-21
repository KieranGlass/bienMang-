from contextlib import closing
import tkinter as tk
from . import common_db_utils


def save_day_info(self, completed):

    child_id = self.child_id
    selected_date = self.selected_date

    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        # Get current data from the UI
        arrival_time = self.arrival_combobox.get()
        departure_time = self.departure_combobox.get()
        starter = self.sliders.get("starter", None)
        main = self.sliders.get("main")
        dessert = self.sliders.get("dessert")
        pooped = self.pooped_var.get()
        poop_count = int(self.poop_count_spinbox.get()) if pooped else 0
        sleep_duration = self.sleep_combobox.get()
        comments = self.comments_text.get("1.0", tk.END).strip()

        # Convert slider values (round to nearest int)
        starter_val = int(round(starter.get())) if starter else None
        main_val = int(round(main.get())) if main else None
        dessert_val = int(round(dessert.get())) if dessert else None
        # Check if entry exists
        cursor.execute('''
            SELECT id FROM child_day_info WHERE child_id = ? AND date = ?
        ''', (child_id, selected_date))
        existing = cursor.fetchone()
        print(f"{completed}")
        if existing:
            print("Updating existing record:", existing)
            # Update existing record
            cursor.execute('''
                UPDATE child_day_info
                SET actual_arrival = ?, actual_finish = ?, starter = ?, main = ?, dessert = ?, pooped = ?, poop_count = ?, 
                    sleep_duration = ?, comments = ?, completed = ?
                WHERE child_id = ? AND date = ?
            ''', (
                arrival_time, departure_time, starter_val, main_val, dessert_val, pooped, poop_count,
                sleep_duration, comments, completed, child_id, selected_date
            ))
            print("Rows updated:", conn.total_changes)
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO child_day_info 
                (child_id, date, actual_arrival, actual_finish, starter, main, dessert, pooped, poop_count, sleep_duration, comments, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                child_id, selected_date, arrival_time, departure_time, starter_val, main_val, dessert_val,
                pooped, poop_count, sleep_duration, comments, completed
            ))

        conn.commit()
    print("Day info saved and marked as complete." if completed == 1 else "Day info saved.")
    self.parent.refresh_register(selected_date)
    self.destroy()

def load_day_info(self):
    child_id = self.child_id
    selected_date = self.selected_date

    # Try to load existing day info
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            SELECT actual_arrival, actual_finish, starter, main, dessert, pooped, poop_count, sleep_duration, comments
            FROM child_day_info
            WHERE child_id = ? AND date = ?
        ''', (child_id, selected_date))
        row = cursor.fetchone()

        day_data = None
    if row:
        day_data = {
            "actual_arrival": row[0],
            "actual_finish": row[1],
            "starter": row[2],
            "main": row[3],
            "dessert": row[4],
            "pooped": bool(row[5]),
            "poop_count": row[6],
            "sleep_duration": row[7],
            "comments": row[8]
        }
    return day_data