from contextlib import closing
from . import common_db_utils

DEFAULT_MENUS = {
        "monday": ("Beef and Carrot Puree", "Apple Compote", "Vegetable Soup", "Sautéed Beef and Potatoes", "Natural Yogurt"),
        "tuesday": ("Chicken and Broccoli Puree", "Fromage Blanc", "Pasta Salad", "Roasted Chicken and Broccoli", "Cheese and Crackers"),
        "wednesday": ("Lentil and Celeri Puree", "Banana Compote", "Cherry Tomatoes", "Lentil and Vegetable Curry", "Clementines"),
        "thursday": ("Haddock and Green Bean Puree", "Pear Compote", "Green Bean Salad", "Haddock and Sweet Potato", "Rice Pudding"),
        "friday": ("Pork and Cauliflower Puree", "Natural Yogurt", "Beetroot Salad", "Roasted Pork and Cauliflower", "Gateau au Chocolat")
}

def search_existing_menu(date):
    with closing(common_db_utils.get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menus WHERE date = ?', (date,))
        return cursor.fetchone()

def create_new_menu(date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(common_db_utils.get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menus (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert)
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert))
        conn.commit()

def update_menu(menu_id, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert):
    with closing(common_db_utils.get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE menus
            SET baby_main = ?, baby_dessert = ?, grands_starter = ?, grands_main = ?, grands_dessert = ?
            WHERE menu_id = ?''',
            (baby_main, baby_dessert, grands_starter, grands_main, grands_dessert, menu_id))
        conn.commit()

def get_menu_by_date(selected_date):
    conn = common_db_utils.get_db_connection()
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT baby_main, baby_dessert, grands_starter, grands_main, grands_dessert FROM menus WHERE date = ?', (selected_date,))
        menu = cursor.fetchone()
    conn.close()
    return menu