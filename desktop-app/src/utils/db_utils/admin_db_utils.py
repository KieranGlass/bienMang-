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
                conn.commit()
                return True, "New User Created"
            except sqlite3.IntegrityError:
                return False, "Username already exists."
            finally:
                conn.close()
    else:
            return False, "Invalid username and password"
    
def edit_user(old_username, new_username, new_password, new_role, user_type):
    
    try:
        conn = common_db_utils.get_db_connection()
        with closing(conn.cursor()) as cursor:
            # You may want to hash the password before saving (optional):
            # hashed_password = hash_password(new_password)

            # Example check to prevent editing of the 'master' user
            if new_username.lower() == 'master':
                return False, "Cannot edit the master user."

            # Check if the user exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (old_username,))
            if cursor.fetchone() is None:
                return False, f"User '{new_username}' does not exist."

            # Update user details
            cursor.execute("""
                UPDATE users
                SET username = ?, password = ?, role = ?, is_admin = ?
                WHERE username = ?
            """, (new_username, new_password, new_role, int(user_type), old_username))

            conn.commit()
            return True, f"User '{new_username}' updated successfully."
        
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()



def delete_user(selected_user):

    username = selected_user[0]
    conn = common_db_utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()

    
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