import sqlite3
import bcrypt
from contextlib import closing

DB_PATH = '/database/bien-manger.db'  # This is where SQLite database will be created


def get_db_connection():
    """
    Returns a connection object to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)  # Connect to the SQLite database
    return conn


def create_tables():
    """
    Creates the necessary tables in the database.
    This function should be run once to initialize the database.
    """
    conn = get_db_connection()
    try:
        with closing(conn.cursor()) as cursor:
            # Create the users table for login/authentication
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            ''')

            # Insert a user (for development purposes)
            cursor.execute('''
            INSERT OR IGNORE INTO users (username, password)
                VALUES ('master', '1')
            ''')

            # Create the children table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                middle_name TEXT,
                last_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                year_group TEXT NOT NULL,
                guardian_one_fname TEXT NOT NULL,
                guardian_one_lname TEXT NOT NULL,
                guardian_one_contact_no TEXT NOT NULL,
                guardian_one_email TEXT NOT NULL,
                guardian_two_fname TEXT,
                guardian_two_lname TEXT,
                guardian_two_contact_no TEXT,
                monday_arrival TEXT,
                monday_finish TEXT,
                tuesday_arrival TEXT,
                tuesday_finish TEXT,
                wednesday_arrival TEXT,
                wednesday_finish TEXT,
                thursday_arrival TEXT,
                thursday_finish TEXT,
                friday_arrival TEXT,
                friday_finish TEXT,
                
                UNIQUE(first_name, last_name, birth_date)
            )
            ''')

            # Insert fake children for development
            cursor.execute('''
            INSERT OR IGNORE INTO Children (first_name, middle_name, last_name, birth_date, year_group, 
    guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, 
    guardian_two_fname, guardian_two_lname, guardian_two_contact_no,
    monday_arrival, monday_finish, tuesday_arrival, tuesday_finish, 
    wednesday_arrival, wednesday_finish, thursday_arrival, thursday_finish, 
    friday_arrival, friday_finish)
                VALUES 
    ('Harry', 'James', 'Potter', '2022-02-10', 'Petits', 'James', 'Potter', '555-1234', 'james.potter@email.com', NULL, NULL, NULL, 
    '07:30', '16:00', '08:00', '16:30', '07:30', '16:00', '08:00', '16:00', '07:30', '16:00'),
                           
    ('Hermione', 'Jean', 'Granger', '2022-04-15', 'Petits', 'Daniel', 'Granger', '555-2345', 'daniel.granger@email.com', NULL, NULL, NULL, 
    '08:00', '15:00', '08:30', '16:00', '08:00', '16:00', '08:30', '15:30', '07:30', '16:00'),
    
    ('Ronald', 'Bilius', 'Weasley', '2022-07-12', 'Petits', 'Arthur', 'Weasley', '555-3456', 'arthur.weasley@email.com', 'Molly', 'Weasley', '555-4567', 
    '07:30', '16:00', '08:00', '15:00', '07:30', '16:00', '08:00', '16:30', '07:30', '15:30'),
    
    ('Neville', NULL, 'Longbottom', '2022-01-11', 'Petits', 'Alice', 'Longbottom', '555-5678', 'alice.longbottom@email.com', 'Frank', 'Longbottom', '555-6789',
    'N/A', 'N/A', 'N/A', 'N/A', '08:00', '16:00', 'N/A', 'N/A', '08:00', '15:00'),
    
    ('Ginny', 'Molly', 'Weasley', '2023-04-09', 'Moyens', 'Arthur', 'Weasley', '555-7890', 'arthur.weasley@email.com', 'Molly', 'Weasley', '555-8901', 
    'N/A', 'N/A', 'N/A', 'N/A', '07:30', '16:00', 'N/A', 'N/A', 'N/A', 'N/A'),
    
    ('Luna', NULL, 'Lovegood', '2022-09-19', 'Petits', 'Xenophilius', 'Lovegood', '555-9012', 'xenophilius.lovegood@email.com', NULL, NULL, NULL, 
    '07:30', '15:30', '07:30', '15:00', 'N/A', 'N/A', '07:30', '16:00', '08:00', '16:30'),
    
    ('Fred', NULL, 'Weasley', '2022-01-02', 'Grands', 'Arthur', 'Weasley', '555-1122', 'arthur.weasley@email.com', 'Molly', 'Weasley', '555-2233',
    '07:30', '16:00', 'N/A', 'N/A', '08:00', '15:00', '07:30', '16:00', '08:00', '15:00'),
    
    ('George', NULL, 'Weasley', '2022-01-02', 'Grands', 'Arthur', 'Weasley', '555-3344', 'arthur.weasley@email.com', 'Molly', 'Weasley', '555-4455',
    '07:30', '15:30', '08:00', '15:30', '08:00', '16:00', '08:00', '16:00', '08:30', '15:30'),
    
    ('Draco', 'Lucius', 'Malfoy', '2022-07-24', 'Petits', 'Lucius', 'Malfoy', '555-5566', 'lucius.malfoy@email.com', 'Narcissa', 'Malfoy', '555-6677',
    '08:00', '16:00', 'N/A', 'N/A', '07:30', '16:00', '08:00', '16:00', '07:30', '15:30'),
    
    ('Cedric', NULL, 'Diggory', '2022-11-29', 'Grands', 'Amos', 'Diggory', '555-7788', 'amos.diggory@email.com', 'Mandy', 'Diggory', '555-8899',
    '07:30', '16:00', '08:00', '16:00', 'N/A', 'N/A', '08:00', '15:30', '08:00', '16:00'),
    
    ('Cho', NULL, 'Chang', '2022-12-10', 'Grands', 'Julien', 'Chang', '555-9900', 'mr.chang@email.com', NULL, NULL, NULL, 
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', '08:00', '16:00')
                    ''')
            
            # Create the registers table
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS registers (
                register_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                child_id INTEGER NOT NULL,
                adjusted_start_time TEXT,
                adjusted_end_time TEXT,
                FOREIGN KEY (child_id) REFERENCES children(id),
                           
                UNIQUE(date, child_id)
            )
            ''')

            # Commit the changes and leave the connection open for further operations
            conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection after operations are done
        conn.close()


def create_user(username, password):
    """
    Create a new user and save to the users table with a hashed password.
    """
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()


def authenticate_user(username, password):
    """
    Authenticate a user by comparing hashed passwords.
    """
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_pw = cursor.fetchone()

    if stored_pw and bcrypt.checkpw(password.encode('utf-8'), stored_pw[0]):
        return True  # Authentication successful
    return False  # Authentication failed


def get_all_children():
    """
    Fetch all children records from the database.
    This can be used for the mobile app or any future features.
    """
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM children")
        children = cursor.fetchall()
    return children


# Inserting a new child record
def add_child(first_name, last_name, birth_date, admission_date, notes):
    """
    Add a child to the database.
    """
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
        INSERT INTO children (first_name, last_name, birth_date, admission_date, notes)
        VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, birth_date, admission_date, notes))
        conn.commit()
        conn.close()


# Function to print database contents for testing
def print_all_users():
    """
    This function will print all the users, for testing purposes.
    """
    conn = get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            print(dict(user))


if __name__ == '__main__':
    create_tables()  # Set up tables on first run (this can also be done in your Docker entrypoint)
    print("Database setup completed.")