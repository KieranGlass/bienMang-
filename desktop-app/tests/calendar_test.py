import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from utils import calendar_utils

class CalendarUtilsTests(unittest.TestCase):

    # Test get days in month method
    def test_get_days_in_month_april(self):
        date = datetime(2024, 4, 1)  # April 2024 (30 days)
        days = calendar_utils.get_days_in_month(date)
        self.assertEqual(len(days), 30)
        self.assertEqual(days[0].day, 1)
        self.assertEqual(days[-1].day, 30)
        
    # Test get week dates method
    def test_get_week_dates(self):
        # Wednesday 2024-06-05, Monday should be 2024-06-03
        week = calendar_utils.get_week_dates("2024-06-05")
        self.assertEqual(week[0], "2024-06-03")
        self.assertEqual(week[-1], "2024-06-09")
        self.assertEqual(len(week), 7)
    
    # Test get month dates method
    def test_get_month_dates_january(self):
        month_dates = calendar_utils.get_month_dates("2024-01-15")
        self.assertEqual(month_dates[0], "2024-01-01")
        self.assertEqual(month_dates[-1], "2024-01-31")
        self.assertEqual(len(month_dates), 31)
        
    # Test Highlight weekdays
    @patch("utils.db_utils.admin_db_utils.get_closure_days", return_value=["2024-06-05"])
    def test_highlight_weekdays(self, mock_get_closure_days):
        # Mock calendar widget
        calendar_widget = MagicMock()

        # Mock get_displayed_month_fn returns (6, 2024)
        get_displayed_month_fn = MagicMock(return_value=(6, 2024))

        disabled = calendar_utils.highlight_weekdays(calendar_widget, get_displayed_month_fn)

        # It should return set with closure and weekend dates
        self.assertIn(datetime(2024, 6, 1).date(), disabled)  # 1 June 2024 is Saturday (weekend)
        self.assertIn(datetime(2024, 6, 5).date(), disabled)  # closure day

        # Check that tags are configured
        calendar_widget.tag_config.assert_any_call("closure", background="yellow", foreground="black")
        calendar_widget.tag_config.assert_any_call("weekday", background="lightgreen", foreground="black")
        calendar_widget.tag_config.assert_any_call("weekend", background="pink", foreground="black")

        # Check that calendar events are created for closure days
        calendar_widget.calevent_create.assert_any_call(datetime(2024, 6, 5).date(), "5", "closure")
        
    
    def test_on_day_selected_blocked_date(self):
        calendar_widget = MagicMock()
        disabled_weekends = {datetime(2024, 6, 1).date()}
        calendar_widget.get_date.return_value = "2024-06-01"

        open_day_info_fn = MagicMock()

        calendar_utils.on_day_selected(calendar_widget, disabled_weekends, open_day_info_fn)

        calendar_widget.selection_clear.assert_called_once()
        open_day_info_fn.assert_not_called()

    def test_on_day_selected_allowed_date(self):
        calendar_widget = MagicMock()
        disabled_weekends = {datetime(2024, 6, 1).date()}
        calendar_widget.get_date.return_value = "2024-06-03"

        open_day_info_fn = MagicMock()

        calendar_utils.on_day_selected(calendar_widget, disabled_weekends, open_day_info_fn)

        calendar_widget.selection_clear.assert_not_called()
        open_day_info_fn.assert_called_once_with("2024-06-03")