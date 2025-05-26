import sqlite3
from contextlib import closing

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