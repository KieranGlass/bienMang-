import sqlite3
from contextlib import closing


def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_all_children():
    """Fetch all children records from the database."""

    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM children")
        children = cursor.fetchall()
        
    return children