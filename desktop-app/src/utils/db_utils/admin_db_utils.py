import sqlite3
from contextlib import closing

from tkinter import messagebox

from . import common_db_utils


def submit_admin(username, password, role, user_type):
    
    if username and password:

        conn = common_db_utils.get_db_connection()
        cursor = conn.cursor()

        if user_type == 1:
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, role, is_admin, is_active)
                    VALUES (?, ?, ?, 1, 1)
                """, (username, password, role))
                cursor.execute("UPDATE users SET is_active = 0, is_admin = 0 WHERE username = 'master'")
                conn.commit()
                return True, "Admin created and master disabled."
            except sqlite3.IntegrityError:
                return False, "Username already exists."
            finally:
                conn.close()
        else:
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, role, is_admin, is_active)
                    VALUES (?, ?, ?, 0, 1)
                """, (username, password, role))
                cursor.execute("UPDATE users SET is_active = 0, is_admin = 0 WHERE username = 'master'")
                conn.commit()
                return True, "Admin created and master disabled."
            except sqlite3.IntegrityError:
                return False, "Username already exists."
            finally:
                conn.close()
    else:
            return False, "Invalid username and password"
    
def edit_user():
    print("editing!!")
    
def get_all_staff():

    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

    return users

def get_setting(key):
    conn = common_db_utils.get_db_connection()
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else ""
    finally:
        conn.close()
    

def set_email(key, value):
    try:
        conn = common_db_utils.get_db_connection()
        cursor = conn.cursor()

        # Check if key exists
        cursor.execute("SELECT 1 FROM settings WHERE key = ?", (key,))
        exists = cursor.fetchone() is not None

        # Insert or update
        cursor.execute("""
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, value))
        conn.commit()
        conn.close()

        if exists:
            messagebox.showinfo("Updated", f"Email Configuration updated successfully.")
        else:
            messagebox.showinfo("Saved", f"Email Configuration saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save Email Configuration.\n\n{str(e)}")