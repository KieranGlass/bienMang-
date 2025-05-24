import sqlite3

from . import common_db_utils


def submit_admin(username, password):
    if username and password:
        conn = common_db_utils.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password, is_admin, is_active)
                VALUES (?, ?, 1, 1)
            """, (username, password))
            cursor.execute("UPDATE users SET is_active = 0 WHERE username = 'master'")
            conn.commit()
            return True, "Admin created and master disabled."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        finally:
            conn.close()
    else:
        return False, "Username and password required."