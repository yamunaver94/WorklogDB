import formatter

def store_category():

    formatter.clear_screen()
    while True:
        category = input("\nSpecify what type of task was conducted:\n>>> ").strip().upper()
        if not category:
            print("Category not entered...")
            continue
        return category

def store_note():

    formatter.clear_screen()
    while True:
        note = input("\nProvide details as to what was completed:\n>>> ").strip().upper()
        if not note:
            print("Note not entered...")
            continue
        return note

def store_date():

        formatter.clear_screen()
        date = input("\nProvide the date for which the task was completed - [yyyy-mm-dd]:\n>>> ")
        return formatter.date(date)

def store_duration():

    formatter.clear_screen()
    while True:
        try:
            time_duration = abs(int(input("\nProvide time spent on task (in minutes):\n>>> ")))
        except ValueError:
            print("Invalid time value...")
            continue
        if not time_duration:
            print("No time entered...")
            continue

        stored_time = formatter.timeclock(time_duration)

        return stored_time