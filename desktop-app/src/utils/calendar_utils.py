from datetime import datetime, timedelta

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

    for day in total_days_in_month:
        day_date = day.date()
        if day.weekday() < 5:
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
        print(f"Weekend selected: {selected_date}. Selection disabled.")
        calendar_widget.selection_clear()
        return

    print("Opening day info page for " + selected_date_str)
    open_day_info_fn(selected_date_str)

def on_day_selected_for_button(calendar_widget, disabled_weekends):
    
    selected_date_str = calendar_widget.get_date()
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    if selected_date in disabled_weekends:
        print(f"Weekend selected: {selected_date}. Selection disabled.")
        calendar_widget.selection_clear()
        return

def open_day_info(parent_window, root_app, date_str, day_info_class):
    """Create and display a day info window for the selected date."""
    day_info_window = day_info_class(root_app, root_app, date_str)
    parent_window.destroy()
    day_info_window.grab_set()
    