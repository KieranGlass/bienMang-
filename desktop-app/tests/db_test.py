import unittest
from unittest.mock import patch, MagicMock

from datetime import datetime

from utils.db_utils import common_db_utils, admin_db_utils, children_db_utils, registers_db_utils, menus_db_utils

def normalize_sql(sql):
    return " ".join(sql.split())

class DbTests(unittest.TestCase):
    # Test submit admin method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_submit_admin_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Act
        result, message = admin_db_utils.submit_admin("admin", "pass123", "Admin", 1)

        # Assert
        self.assertTrue(result)
        self.assertIn("Admin created", message)
        # Check that the INSERT was called with the expected SQL and params, ignoring whitespace formatting
        calls = mock_cursor.execute.call_args_list

        expected_insert_sql = """
            INSERT INTO users (username, password, role, is_admin, is_active)
            VALUES (?, ?, ?, 1, 1)
        """
        expected_insert_params = ("admin", "pass123", "Admin")

        found_insert = False
        for call in calls:
            sql_arg = call[0][0]
            params_arg = call[0][1]
            if normalize_sql(sql_arg) == normalize_sql(expected_insert_sql) and params_arg == expected_insert_params:
                found_insert = True
                break
        self.assertTrue(found_insert, "Expected INSERT SQL call not found with correct parameters.")

        # Also check the UPDATE call
        mock_cursor.execute.assert_any_call(
            "UPDATE users SET is_active = 0, is_admin = 0 WHERE username = 'master'"
        )

        # Check commit and close
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
    # Test Delete User method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_delete_user_executes_delete_and_commits(self, mock_get_conn):
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        selected_user = ("john_doe",)

        admin_db_utils.delete_user(selected_user)

        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("DELETE FROM users WHERE username=?", ("john_doe",))
        mock_conn.commit.assert_called_once()

    # Test get all staff method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_get_all_staff_returns_users(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        expected_users = [
            ("john_doe", "John", "Doe", "john@example.com"),
            ("jane_smith", "Jane", "Smith", "jane@example.com")
        ]
        mock_cursor.fetchall.return_value = expected_users

        result = admin_db_utils.get_all_staff()

        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, expected_users)
        
    # Test get all children method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_get_all_children_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
    
        fake_children = [
            (1, "Alice", "2020-05-01", "F"),
            (2, "Bob", "2019-08-15", "M")
        ]
        mock_cursor.fetchall.return_value = fake_children
    
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn


        result = common_db_utils.get_all_children()

        mock_cursor.execute.assert_called_once_with("SELECT * FROM children")
        self.assertEqual(result, fake_children)
        mock_conn.close.assert_called_once()

    # Test get child by id method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_get_child_success(self, mock_get_conn):
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Simulated DB return for a child with ID 5
        fake_child = (
            "Alice", None, "Smith", "2020-05-01", "Year 2",
            "Jane", "Smith", "1234567890", "jane@example.com",
            "John", "Smith", "0987654321"
        )
        mock_cursor.fetchone.return_value = fake_child

        # Hook mocks into the connection
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        result = children_db_utils.get_child(5)

        # Assert
        mock_cursor.execute.assert_called_once_with(
            "SELECT first_name, middle_name, last_name, birth_date, year_group, guardian_one_fname, guardian_one_lname, guardian_one_contact_no, guardian_one_email, guardian_two_fname, guardian_two_lname, guardian_two_contact_no FROM children WHERE id=?",
            (5,)
        )
        self.assertEqual(result, fake_child)
        mock_conn.close.assert_called_once()
     
    # Test Add child method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_add_child_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        

        # Sample child data
        children_db_utils.add_child(
            "Alice", "Marie", "Smith", "2020-05-01", "Year 1",
            "Jane", "Smith", "1234567890", "jane@example.com",
            "08:00", "15:00",
            "08:00", "15:00",
            "08:00", "15:00",
            "08:00", "15:00",
            "08:00", "15:00",
            guardian_two_fname="John", guardian_two_lname="Smith", guardian_two_contact_no="0987654321"
        )

        # Check the INSERT statement
        self.assertTrue(mock_cursor.execute.called)
        sql, params = mock_cursor.execute.call_args[0]

        self.assertIn("INSERT INTO children", sql)
        self.assertEqual(len(params), 22)
        self.assertEqual(params[0], "Alice")  # Spot check first name

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
    # Test Delete Child Method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_delete_child_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        children_db_utils.delete_child_from_db(7)

        mock_cursor.execute.assert_called_once_with("DELETE FROM Children WHERE id=?", (7,))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
    # Test search existing register method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_search_existing_register_inserts_when_missing(self, mock_get_conn):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Simulate register does not exist
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        register_date = "2024-06-07"  # Friday
        child = (
            1, "Alice", "", "Smith", "", "", "", "", "", "", "", "",
            "", "08:00", "15:00", "08:00", "15:00", "08:00", "15:00", "08:00", "15:00", "08:30", "14:30"
        )

        registers_db_utils.search_existing_register(register_date, [child])

        # Check for register existence
        mock_cursor.execute.assert_any_call('SELECT 1 FROM registers WHERE date = ?', (register_date,))
    
        # Should insert for each child
        mock_cursor.execute.assert_any_call(
            '''INSERT INTO registers (date, child_id, adjusted_start_time, adjusted_end_time)
                                VALUES (?, ?, ?, ?)''',
            (register_date, 1, "08:30", "14:30")
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
    # Test search adjusted schedule method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_search_adjusted_schedule_returns_correct_times(self, mock_get_conn):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = ("09:00", "16:00")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        date = "2024-06-07"
        child_id = 1

        result = registers_db_utils.search_adjusted_schedule(date, child_id)

        mock_cursor.execute.assert_called_once_with(
            'SELECT adjusted_start_time, adjusted_end_time FROM registers WHERE date = ? AND child_id = ?', 
            (date, child_id)
        )
        self.assertEqual(result, ("09:00", "16:00"))
        mock_conn.close.assert_called_once()
        
    # Test search menu method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_search_existing_menu_returns_data(self, mock_get_conn):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("2024-06-07", "Pasta", "Fruit", "Soup", "Chicken", "Cake")

        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = menus_db_utils.search_existing_menu("2024-06-07")

        mock_cursor.execute.assert_called_once_with('SELECT * FROM menus WHERE date = ?', ("2024-06-07",))
        self.assertEqual(result, ("2024-06-07", "Pasta", "Fruit", "Soup", "Chicken", "Cake"))
        mock_conn.close.assert_called_once()
        
    # Test create menu method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_create_new_menu_success(self, mock_get_conn):
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        menus_db_utils.create_new_menu("2024-06-07", "Mashed Potatoes", "Apple Sauce", "Salad", "Fish", "Pudding")

        expected_sql = '''
            INSERT INTO menus (date, baby_main, baby_dessert, grands_starter, grands_main, grands_dessert)
            VALUES (?, ?, ?, ?, ?, ?)
        '''

        actual_sql = mock_cursor.execute.call_args[0][0]
        actual_params = mock_cursor.execute.call_args[0][1]

        assert normalize_sql(actual_sql) == normalize_sql(expected_sql)
        assert actual_params == ("2024-06-07", "Mashed Potatoes", "Apple Sauce", "Salad", "Fish", "Pudding")
        mock_conn.commit.assert_called_once()
        
    # Test update menu method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_update_menu_success(self, mock_get_conn):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        menus_db_utils.update_menu(5, "Veg Mash", "Fruit Yogurt", "Soup", "Beef Stew", "Ice Cream")

        expected_sql = '''
            UPDATE menus
            SET baby_main = ?, baby_dessert = ?, grands_starter = ?, grands_main = ?, grands_dessert = ?
            WHERE menu_id = ?
        '''

        actual_sql = mock_cursor.execute.call_args[0][0]
        actual_params = mock_cursor.execute.call_args[0][1]

        assert normalize_sql(actual_sql) == normalize_sql(expected_sql)
        assert actual_params == ("Veg Mash", "Fruit Yogurt", "Soup", "Beef Stew", "Ice Cream", 5)
        mock_conn.commit.assert_called_once()
        
    # Test get menu by date method
    @patch("utils.db_utils.common_db_utils.get_db_connection")
    def test_get_menu_by_date_returns_correct_menu(self, mock_get_conn):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("Pasta", "Fruit", "Soup", "Chicken", "Cake")

        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = menus_db_utils.get_menu_by_date("2024-06-07")

        mock_cursor.execute.assert_called_once_with(
            'SELECT baby_main, baby_dessert, grands_starter, grands_main, grands_dessert FROM menus WHERE date = ?',
            ("2024-06-07",)
        )
        self.assertEqual(result, ("Pasta", "Fruit", "Soup", "Chicken", "Cake"))
        mock_conn.close.assert_called_once()
    
if __name__ == "__main__":
    unittest.main()