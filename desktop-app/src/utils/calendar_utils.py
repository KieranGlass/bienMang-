import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime, timedelta
from calendar import monthrange
from datetime import datetime, timedelta
from utils.db_utils import admin_db_utils


def highlight_weekdays(calendar_widget, get_displayed_month_fn):

    """Highlight weekdays and weekends on the calendar_widget"""
    print("Month changed!")
    current_month = get_displayed_month_fn()
    print(f"The month is: {current_month}")

    if isinstance(current_month, tuple) and len(current_month) == 2:
        month, year = current_month
        current_month_str = f"{year:04d}-{month:02d}"
    else:
        raise ValueError("Expected current_month to be a tuple with (year, month)")

    first_day = datetime.strptime(current_month_str + "-01", "%Y-%m-%d")
    print(f"First day is: {first_day.strftime('%Y-%m-%d')}")
    total_days_in_month = get_days_in_month(first_day)

    calendar_widget.calevent_remove("weekday")
    calendar_widget.calevent_remove("weekend")

    try:
        calendar_widget.tag_delete("weekday")
        calendar_widget.tag_delete("weekend")
        print("Deleted existing tags")
    except Exception:
        print("No tags currently present")

    disabled_weekends = set()
    closure_dates = set(admin_db_utils.get_closure_days())

    for day in total_days_in_month:
        day_date = day.date()
        if str(day_date) in closure_dates:
            calendar_widget.calevent_create(day_date, f"{day.day}", "closure")
            calendar_widget.tag_config("closure", background="yellow", foreground="black")
            disabled_weekends.add(day_date)
        elif day.weekday() < 5:
            calendar_widget.calevent_create(day_date, f"{day.day}", "weekday")
            calendar_widget.tag_config("weekday", background="lightgreen", foreground="black")
        else:
            calendar_widget.calevent_create(day_date, f"{day.day}", "weekend")
            calendar_widget.tag_config("weekend", background="pink", foreground="black")
            disabled_weekends.add(day_date)

    return disabled_weekends 

def get_days_in_month(date):
    """ Get all the days in the month for the given date """
    # Get the last day of the current month
    next_month = date.replace(day=28) + timedelta(days=4)  # Go to the next month
    last_day_of_month = next_month - timedelta(days=next_month.day)  # Get the last day of the month

    # Generate all days in the month
    days_in_month = [date.replace(day=d) for d in range(1, last_day_of_month.day + 1)]
    return days_in_month

def on_month_change(calendar_widget, get_displayed_month_fn, set_disabled_weekends_fn=None):
    """Callback to update calendar highlighting on month change."""
    disabled = highlight_weekdays(calendar_widget, get_displayed_month_fn)
    if set_disabled_weekends_fn:
        set_disabled_weekends_fn(disabled)

def on_day_selected(calendar_widget, disabled_weekends, open_day_info_fn):
    
    selected_date_str = calendar_widget.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    if selected_date in disabled_weekends:
        print(f"Date {selected_date} is blocked (weekend or closure).")
        calendar_widget.selection_clear()
        return

    print("Opening day info page for " + selected_date_str)
    open_day_info_fn(selected_date_str)

def on_day_selected_for_button(calendar_widget, disabled_weekends):
    
    selected_date_str = calendar_widget.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    if selected_date in disabled_weekends:
        print(f"Date {selected_date} is blocked (weekend or closure).")
        calendar_widget.selection_clear()
        return

def open_day_info(parent_window, root_app, date_str, day_info_class):
    """Create and display a day info window for the selected date."""
    day_info_window = day_info_class(root_app, root_app, date_str)
    parent_window.destroy()
    day_info_window.grab_set()
    
def get_week_dates(selected_date_str):
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
    # weekday(): Monday=0, Sunday=6
    monday = selected_date - timedelta(days=selected_date.weekday())  # find Monday of that week
    
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def get_month_dates(start_date_str):

    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    days = monthrange(start.year, start.month)[1]
    return [(start.replace(day=1) + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def update_day_label(date):
    """ Update the label in the middle column to show the selected day """
        
    # Format the selected date into the desired format (e.g., "Monday, 2nd June 2025")
    day_name = date.strftime("%A")
    print(f"{day_name}")
    day_number = date.day
    print(f"{day_number}")
    month_name = date.strftime("%B")
    print(f"{month_name}")
    year = date.year
        
    # Handle the suffix for the day number (e.g., 1st, 2nd, 3rd, etc.)
    suffix = 'th'
    if 4 <= day_number <= 20:
        suffix = 'th'
    elif day_number % 10 == 1:
        suffix = 'st'
    elif day_number % 10 == 2:
        suffix = 'nd'
    elif day_number % 10 == 3:
        suffix = 'rd'

    # Format the date string
    formatted_date = f"{day_name} {day_number}{suffix} {month_name} {year}"
    print(f"{formatted_date}")

    return formatted_date