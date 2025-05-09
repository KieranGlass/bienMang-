from contextlib import closing
from datetime import datetime
from . import common_db_utils

def search_existing_register(register_date_str, children):
    """Check if the register entry exists, if not, create one."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        # Check if the register already exists for the date
        cursor.execute('SELECT 1 FROM registers WHERE date = ?', (register_date_str,))
        if not cursor.fetchone():
            for child in children:
                child_id, first_name, middle_name, last_name, _, _, _, _, _, _, _, _, _, monday_arrival, monday_finish, \
                tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, \
                thursday_finish, friday_arrival, friday_finish = child

                # Determine the default arrival and finish times based on the weekday
                weekday_name = datetime.strptime(register_date_str, "%Y-%m-%d").strftime('%A').lower()
                arrival_column = f"{weekday_name}_arrival"
                finish_column = f"{weekday_name}_finish"
                arrival_time = locals()[arrival_column]
                finish_time = locals()[finish_column]

                cursor.execute('''INSERT INTO registers (date, child_id, adjusted_start_time, adjusted_end_time)
                                VALUES (?, ?, ?, ?)''', (register_date_str, child_id, arrival_time, finish_time))
            conn.commit()

def search_adjusted_schedule(register_date_str, child_id):
    """Check if there's an adjusted schedule for the day."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT adjusted_start_time, adjusted_end_time FROM registers WHERE date = ? AND child_id = ?', 
                       (register_date_str, child_id))
        adjusted_schedule = cursor.fetchone()
    return adjusted_schedule

def save_adjustment(date_str, child_id, start_entry, end_entry):
    """Save adjustments made to the schedule."""
    adjusted_start = start_entry.get()
    adjusted_end = end_entry.get()
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''INSERT OR REPLACE INTO registers (date, child_id, adjusted_start_time, adjusted_end_time)
                          VALUES (?, ?, ?, ?)''', (date_str, child_id, adjusted_start, adjusted_end))
        conn.commit()

def get_completed_status(selected_date, child_id):
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT completed FROM child_day_info WHERE date = ? AND child_id = ?', (selected_date, child_id,))
        status = cursor.fetchone()
    return status