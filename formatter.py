import datetime
import collections
import re
import os
import time

import readchar

import main
import task_functions

def date(emp_date):
    '''Return a date to a specified arrangement'''
    while True:
        try:
            format_check = datetime.datetime.strptime(emp_date, '%Y-%m-%d').date()
        except ValueError:
            emp_date = input("\nDates of the following format are only accepted: [yyyy-mm-dd]\n>>>")
        else:
            return format_check

    print(format_check)

def timeclock(time_worked):
    '''Return a time object'''
    while True:
        if time_worked > 59:
            minutes = time_worked % 60
            hours = (time_worked - minutes) / 60
        else:
            minutes = time_worked
            hours = 0
      
        try:
            time_clocked = datetime.time(hour=int(hours), minute=int(minutes))
        except (ValueError, OverflowError):
            time_clocked = task_functions.store_duration()
        finally:
            return time_clocked

def filter_name(person_name):
    '''Removes excessive/unnecessary characters from a provided name'''

    name_length = person_name.split()

    if person_name.upper().endswith(('JR', 'SR', 'JR.', "SR.")): 
        del name_length[-1]
    if len(name_length) > 2:
        del name_length[1:-1]
    return ' '.join(name_length)

def verify_ssn(ssn_number):
    '''Return SSN in valid real world format'''
    ssn_pattern = re.compile(r'\d{3}-\d{2}-\d{4}')
                
    while True:
        regex_result = re.fullmatch(ssn_pattern, ssn_number)
        if not regex_result:
            ssn_number = input("\nThe SSN provided doesn't match the format required '111-11-1111':\n>>>")
            continue
        break
    return regex_result.group() 

def display_tasks(task_objects):
    '''Menu used to show entries to a user'''
    indexed_tasks = collections.deque(zip(task_objects, range(1, len(task_objects) + 1))) #provides a count of each task in `task_objects`
    
    while True:
        clear_screen()
        i = indexed_tasks[0][1] # Task #__ of len(task_objects)
        show_task = indexed_tasks[0][0]
        by_employee = str(main.Employee.get(main.Employee.id == show_task.employee.id)).upper() # Employee of task

        print(f'***Task #{i} of {len(task_objects)}****')
        print(f'''
Employee: {by_employee}
Task: {show_task.task}
Task Date: {show_task.task_date}
Details : {show_task.note}
Time: {show_task.time_duration}\n''')
        print('*' * 20)

        print('[C] - Next Task Entry\n[P] - Previous Task Entry\n[B] - Back To Previous Menu')

        while True:
            print("Please select one of the above options...")
            user_choice = readchar.readkey().upper()
            if user_choice not in ['C', 'P', 'B']:
                print("Invalid selection...")
                continue
            break
        if user_choice == 'C':
            indexed_tasks.rotate(-1)
            continue
        elif user_choice == 'P':
            indexed_tasks.rotate(1)
            continue
        return # exit loop if user input is `B`

def clear_screen():
    return os.system('cls' if os.name=='nt' else 'clear')

