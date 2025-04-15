import sqlite3
from contextlib import closing

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


def get_db_connection():
    conn = sqlite3.connect('/database/bien-manger.db')
    return conn

def get_child_by_id(child_id):
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM children WHERE id =?', (child_id,))
        child = cursor.fetchone()
    
    return child

class ChildDayInfoPage (tk.Toplevel):
    def __init__(self, parent, child_id, selected_date):
        super().__init__(parent)
        self.selected_date = selected_date
        self.child_id = child_id
        self.geometry("1400x900")

        child = get_child_by_id(child_id)
        print(f"{child}")

        fname = child[1]
        lname = child[3]

        self.title_label = tk.Label(self, text=f"Day info for {fname} {lname}", font=("Helvetica", 14, "bold"))
        self.title_label.grid(row=0, column=0, sticky="nsew", padx=10)