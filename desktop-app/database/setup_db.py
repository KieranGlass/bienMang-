from database import create_tables

def initialize_database():
    """
    Initializes the database by creating necessary tables.
    """
    print("Initializing database...")
    create_tables()  # This function will create the tables in the database.
    print("Database initialized successfully.")

if __name__ == '__main__':
    initialize_database()  # Run the database setup when the script is executed