import re

from peewee import *
import readchar

import formatter
import menu
import main
	
def get_ssn():
	formatter.clear_screen()
	ssn_number = input(f'\nEnter social security number:\n>>> '.strip())
	ssn = formatter.verify_ssn(ssn_number)

	return dict(zip(['ssn'], [ssn]))

def get_employee_data():

    formatter.clear_screen()

    string_matches = re.compile(r'\b\w+')
    print("Provide the following: first name, last name:")

    while True:
        employee_query = input("Employee's name:\n>>> ").title().strip()
        query_result = re.findall(string_matches, employee_query) # '.' is not included with a name suffix for the purpose of line 192 passing; refer to line 184

        if any(not re_string.isalpha() for re_string in query_result) or len(query_result) < 2:
            formatter.clear_screen()
            print("Invalid name provided...First and last names required")
            continue
        break
    db_name = formatter.filter_name(employee_query)
    first_name, last_name = db_name.split()

    return dict(zip(['first_name', 'last_name'], [first_name, last_name]))

def verify_employee(unique):

    try:
        employee = main.Employee.get(main.Employee.ssn == unique['ssn']) # get employee with with a particular ssn
        return employee
    except DoesNotExist: # no employee ssn exists; get all employees with the same first and last name; possible typo in ssn when entered
        person = get_employee_data()
        person['ssn'] = unique['ssn']

        emp_ids = menu.employee_list(person)
        if not emp_ids or emp_ids == 'N':
            print("{first_name} {last_name} - SSN#: {ssn} is added to the database.".format(**person))
            return main.Employee.create(**person)
        while True:
            id_employee = readchar.readkey().upper()
            if id_employee == 'N':
                print("\nExited out of employee records...no change occured.")
                print("{first_name} {last_name} - SSN#: {ssn} is added to the database.".format(**person))
                return main.Employee.create(**person)
 
            elif id_employee not in emp_ids:
                id_listings = ''.join(f' [{n}] ' for n in emp_ids)
                print(f"To switch employees select only from these Employee ID#: {id_listings}")
                continue

            official_name = '{first_name} {last_name}'.format(**person)
            print(f'{official_name} - ID#: {id_employee} has now been selected...')
            return main.Employee.get_by_id(int(id_employee))

        return main.Employee.create(**person)

def store_category():
    while True:
        category = input("\nSpecify what type of task was conducted:\n>>> ").strip().upper()
        if not category:
            print("Category not entered...")
            continue
        return category

def store_note():

    while True:
        note = input("\nProvide details as to what was completed:\n>>> ").strip().upper()
        if not note:
            print("Note not entered...")
            continue
        return note

def store_date():
        date = input("\nProvide the date for which the task was completed - [yyyy-mm-dd]:\n>>> ")
        return formatter.date(date)

def store_duration():
    while True:
        try:
            time_duration = abs(int(input("\nProvide time spent on task (in minutes):\n>>> ")))
        except ValueError:
            print("Invalid time value...")
            continue
        if not time_duration:
            print("No time entered...")
            continue
        return formatter.timeclock(time_duration)