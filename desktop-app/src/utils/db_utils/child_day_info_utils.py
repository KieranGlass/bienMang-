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


def get_day_info_by_date(child_id, date):
    conn = common_db_utils.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            actual_arrival,
            actual_finish,
            main,
            dessert,
            pooped,
            poop_count,
            sleep_duration,
            comments
        FROM child_day_info
        WHERE child_id = ? AND date = ?
    """, (child_id, date))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "actual_arrival": row[0],
        "actual_finish": row[1],
        "main": row[2],
        "dessert": row[3],
        "pooped": bool(row[4]),
        "poop_count": row[5],
        "sleep_duration": row[6],
        "comments": row[7]
    }

def get_data_for_dates(child_id, date_list):
    
    conn = common_db_utils.get_db_connection()
    cursor = conn.cursor()

    results = []
    for date in date_list:
        cursor.execute("""
            SELECT 
                date, actual_arrival, actual_finish, starter, main, dessert,
                pooped, poop_count, sleep_duration, comments
            FROM child_day_info
            WHERE child_id = ? AND date = ?
        """, (child_id, date))

        row = cursor.fetchone()
        if row:
            results.append({
                "date": row[0],
                "arrival": row[1],
                "departure": row[2],
                "starter": row[3],
                "main": row[4],
                "dessert": row[5],
                "pooped": bool(row[6]),
                "poop_count": row[7],
                "sleep": row[8],
                "comments": row[9]
            })

    conn.close()
    return results