
import unittest
from unittest.mock import patch, MagicMock
from utils.db_utils import admin_db_utils


def normalize_sql(sql):
    return " ".join(sql.split())

class DbTests(unittest.TestCase):

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

if __name__ == "__main__":
    unittest.main()