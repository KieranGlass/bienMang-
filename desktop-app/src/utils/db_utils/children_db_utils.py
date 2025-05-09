from contextlib import closing

from tkinter import messagebox

from . import common_db_utils

def get_child(ID):
    """Fetch a complete child record from the database using the child's ID."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT first_name, middle_name, last_name, birth_date, year_group, guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, guardian_two_fname, guardian_two_lname, guardian_two_contact_no FROM children WHERE id=?", (ID,))
        child_data = cursor.fetchone() 
    return child_data

def get_child_by_id(child_id):
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM children WHERE id =?', (child_id,))
        child = cursor.fetchone()
    
    return child

def add_child(
    first_name, middle_name, last_name, birth_date, year_group,
    guardian_one_fname, guardian_one_lname, guardian_one_contact_no, 
    guardian_one_email, monday_arrival, monday_finish, 
    tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, 
    thursday_arrival, thursday_finish, friday_arrival, friday_finish,
    guardian_two_fname=None, guardian_two_lname=None,
    guardian_two_contact_no=None):

    """Add a child to the database with all required fields."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            INSERT INTO children (
                first_name, middle_name, last_name, birth_date, year_group,
                guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
                guardian_one_email, guardian_two_fname, guardian_two_lname,
                guardian_two_contact_no, monday_arrival, monday_finish, tuesday_arrival, 
                tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, 
                thursday_finish, friday_arrival, friday_finish
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            first_name, middle_name, last_name, birth_date, year_group,
            guardian_one_fname, guardian_one_lname, guardian_one_contact_no,
            guardian_one_email, guardian_two_fname, guardian_two_lname,
            guardian_two_contact_no, monday_arrival, monday_finish, 
            tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, 
            thursday_arrival, thursday_finish, friday_arrival, friday_finish
        ))
        conn.commit()

def delete_child_from_db(ID):
    print(f"Deleting child with ID: {ID}")
    conn = common_db_utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Children WHERE id=?", (ID,))
    conn.commit()

def get_child_count():
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT COUNT(*) FROM Children")
        total = cursor.fetchone()[0]
    return total

def get_age_group_petits():
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT COUNT(*) FROM Children WHERE year_group = 'Petits'")
        total = cursor.fetchone()[0]
    return total

def get_age_group_moyens():
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT COUNT(*) FROM Children WHERE year_group = 'Moyens'")
        total = cursor.fetchone()[0]
    return total

def get_age_group_grands():
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT COUNT(*) FROM Children WHERE year_group = 'Grands'")
        total = cursor.fetchone()[0]
    return total

def get_schedule(ID):
    """Fetch a complete child schedule record from the database using the child's ID."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT monday_arrival, monday_finish, tuesday_arrival, tuesday_finish, wednesday_arrival, wednesday_finish, thursday_arrival, thursday_finish, friday_arrival, friday_finish FROM children WHERE id=?", (ID,))
        schedule_data = cursor.fetchone()
    return schedule_data

def save_edited_child_info(id,
    first_name, middle_name, last_name, birth_date, year_group, 
    guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, 
    guardian_two_fname, guardian_two_lname, guardian_two_contact_no):
    """Save the edited child information into the database."""
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            UPDATE children
            SET first_name=?, middle_name=?, last_name=?, birth_date=?, year_group=?,
                guardian_one_fname=?, guardian_one_lname=?, guardian_one_contact_no=?, guardian_one_email=?,
                guardian_two_fname=?, guardian_two_lname=?, guardian_two_contact_no=?
            WHERE id=?
        ''', (first_name, middle_name, last_name, birth_date, year_group, 
              guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, 
              guardian_two_fname, guardian_two_lname, guardian_two_contact_no, id))
        conn.commit()
    
    messagebox.showinfo("Success", "Child info updated successfully.")

def save_edited_child_schedule(id, 
    monday_arrival, monday_finish, tuesday_arrival, tuesday_finish, 
    wednesday_arrival, wednesday_finish, thursday_arrival, thursday_finish, 
    friday_arrival, friday_finish):

    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
            UPDATE children
            SET monday_arrival=?, monday_finish=?, tuesday_arrival=?, tuesday_finish=?, wednesday_arrival=?, 
                wednesday_finish=?, thursday_arrival=?, thursday_finish=?, friday_arrival=?, friday_finish=?
            WHERE id=?
        ''', (monday_arrival, monday_finish, tuesday_arrival, tuesday_finish, wednesday_arrival, 
            wednesday_finish, thursday_arrival, thursday_finish, friday_arrival, friday_finish, id))
        conn.commit()

    messagebox.showinfo("Success", "Child schedule updated successfully.")

