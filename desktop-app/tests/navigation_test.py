import unittest
from unittest.mock import MagicMock, patch
from utils import navigation_utils


class TestNavigation(unittest.TestCase):

    def setUp(self):
        self.mock_window = MagicMock()
        self.mock_window.root_app = MagicMock()

    @patch("utils.navigation_utils.Dashboard")
    def test_show_dashboard(self, mock_dashboard):
        navigation_utils.show_dashboard(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_dashboard.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    @patch("utils.navigation_utils.Children")
    def test_show_children(self, mock_children):
        navigation_utils.show_children(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_children.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    @patch("utils.navigation_utils.Registers")
    def test_show_registers_no_date(self, mock_registers):
        navigation_utils.show_registers(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_registers.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    @patch("utils.navigation_utils.Registers")
    def test_show_registers_with_date(self, mock_registers):
        navigation_utils.show_registers(self.mock_window, "2025-06-07")
        self.mock_window.withdraw.assert_called_once()
        mock_registers.assert_called_once_with(self.mock_window, self.mock_window.root_app, "2025-06-07")

    @patch("utils.navigation_utils.Menus")
    def test_show_menus(self, mock_menus):
        navigation_utils.show_menus(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_menus.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    @patch("utils.navigation_utils.Reports")
    def test_show_reports(self, mock_reports):
        navigation_utils.show_reports(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_reports.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    @patch("utils.navigation_utils.Setting")
    def test_show_settings(self, mock_setting):
        navigation_utils.show_settings(self.mock_window)
        self.mock_window.withdraw.assert_called_once()
        mock_setting.assert_called_once_with(self.mock_window, self.mock_window.root_app)

    def test_log_out(self):
        navigation_utils.log_out(self.mock_window)
        self.mock_window.destroy.assert_called_once()
        self.mock_window.root_app.deiconify.assert_called_once()

    @patch("utils.navigation_utils.Dashboard")
    def test_on_close(self, mock_dashboard):
        navigation_utils.on_close(self.mock_window)
        self.mock_window.destroy.assert_called_once()
        mock_dashboard.assert_called_once_with(self.mock_window.root_app, self.mock_window.root_app)
        mock_dashboard.return_value.lift.assert_called_once()


if __name__ == "__main__":
    unittest.main()