import collections 
import datetime
import re
import sys
import time

from peewee import *
import readchar

import formatter
import menu
import retrieve_data
import task_functions

db = SqliteDatabase('task_logger.db', pragmas={'foreign_keys': 1})

class Database:

    def __init__(self, show_menu=True):
        try:
            db.connect(reuse_if_open="True")
        except:
            print("Database disconnected")
            sys.exit()
        db.create_tables([Employee, Task])
        if show_menu:
            database_options = {
                'A' : self.add_entry,
                'D' : self.delete_entry,
                'S' : self.search_entries
            }
            menu.MainMenuView(database_options)

    def add_entry(self):
        '''Add data to the database'''

        while True:
            ssn = retrieve_data.get_ssn() #input
            work_employee = retrieve_data.verify_employee(ssn) #input

            time.sleep(1)
            formatter.clear_screen()
            task_data = {
                'task' : task_functions.store_category(),
                'task_date' : task_functions.store_date(),
                'time_duration' : task_functions.store_duration(),
                'note' : task_functions.store_note(),
                'employee' : work_employee
            }
            formatter.clear_screen()
            print("Task Stored...")
            work_task = Task.create(**task_data)

            print('Please select from the following:\n[ N ] - Add another entry\n[ B ] - Back to the previous menu')

            while True:
                prompt_new_entry = readchar.readkey().upper() # invokes program flow via keystroke
                if prompt_new_entry not in ['N', 'B']:
                    print("Invalid option. Please enter [N]ew entry; [B]ack to the previous menu:")
                    continue
                break
            if prompt_new_entry == 'N':
                continue
            else:
                return (all(isinstance(model[0], model[1]) for model in [(work_employee, Employee), (work_task,Task)]))
            

    def delete_entry(self):
        '''Remove an employee from the database'''

        record_ssn = retrieve_data.get_ssn()
        previous_tasks = Task.select().join(Employee).where(Employee.ssn == record_ssn['ssn']).dicts(as_dict=True)

        if not previous_tasks:
            print(f"No entrys are stored under SSN {record_ssn['ssn']}.")
            time.sleep(2)
            return False
        task_ids = []

        print('*' * 20)
        task_choices = ''
        for t in previous_tasks:
            task_ids.append(t['id'])
            task_choices += '\nTask ID: {id}\nTask: {task}\nDate: {task_date}\nNote: {note}\n'.format(**t)
        task_choices += '\n'
        print(task_choices)
        print('*' * 20)
        print("\nChoose an entry to delete...")

        while True:

            task_num = int(readchar.readkey())
            if task_num not in task_ids:
                print("Cannot delete entry. Enter ID# again.")
                continue
            break
        del_task = Task.get_by_id(task_num)
        print(f'Deleted Task ID# {task_num}')
        return del_task.delete_instance()

    def search_entries(self):
        '''Search database'''
      
        search_options = {
            '1' : self.search_employee,
            '2' : self.search_dates,
            '3' : self.search_minutes,
            '4' : self.search_notes
        }
        
        while True:
            formatter.clear_screen()
             
            print("Specify how you want to search the database")
            search_menu_str = ''.join(f'{key} - {value.__doc__}\n' for key, value in search_options.items())    
            print(search_menu_str)  

            search_input = readchar.readkey() 
            if search_input not in search_options:
                print("That functionality does not exist. Please select only from the options listed above.")
                time.sleep(1)
                continue

            search_results = search_options[search_input]()
            if search_results:
                formatter.display_tasks(search_results)
            else:
                formatter.clear_screen()
                print("No results can be generated.")

            print("\nWould you like to perform another search...\n[N]ew search\n[M]ain Menu")

            while True:
                search = readchar.readkey().upper()
                if search not in ['N', 'M']:
                    print('Command unknown...please press [N] or [M]')
                    continue
                break
            if search == 'N':
                continue
            return

    def search_employee(self):
        """Find database entries by employee"""

        formatter.clear_screen()
        task_dict = {}

        stored_employees = Employee.select()
        employee_menu = ''

        for emp in stored_employees:
            employee_menu_id = f'{emp.id}-{emp.ssn[-4:]}'
            employee_menu += employee_menu_id + f') {str(emp)}\n'

            task_dict.setdefault(employee_menu_id, [])
            task_dict[employee_menu_id].append(emp)

        print("Employees in Database:\n" +employee_menu)

        while True:
            select_emp = input('Enter an employee id followed by the last four of their SSN# [X-XXXX]:\n>>> ').strip()
            if select_emp not in task_dict:
                print("An invalid reference was entered...")
                continue
            break

        real_id = int(select_emp[:1])   
        all_emp_tasks = Task.select().where(Task.employee == real_id).order_by(Task.task_date)

        return all_emp_tasks

    def search_dates(self):
        """Find database entries by date"""
        formatter.clear_screen()

        provided_date = formatter.date(input("Provide a base date to begin searching entries\n>>>"))

        while True:
            try:
                day_range = int(input(f"Establish how many days to look before and after {provided_date}:\n>>>"))
            except TypeError:
                print("Could not compute the search...only provide a number for the range.")
            else:
                if not day_range:
                    print('A minimum of 1 day must be provided to initiate a date search...')
                    continue
                break
        try:
            search_start = provided_date - datetime.timedelta(days=day_range)
        except OverflowError:
            this_year = provided_date.year
            search_start = datetime.date(year=this_year, month=1, day=1)
        else:
            try:
                search_end = provided_date + datetime.timedelta(days=day_range)
            except OverflowError:
                this_year = provided_date.year
                search_end = datetime.date(year=this_year, month=12, day=31)

            collect_date_range = Task.select().join(Employee).where(Task.task_date >= search_start, 
                                                                    Task.task_date <= search_end).order_by(Task.task_date)

            return collect_date_range

    def search_minutes(self):
        """Find database entries by time spent"""
        formatter.clear_screen()

        while True:
            try:
                search_time = abs(int(input("Search tasks by the number of minutes it took to finish:\n>>>")))
            except (TypeError, ValueError):
                print("Tasks searched by time are only searched by minutes...")
            else:
                if not search_time:
                    print("No time was entered to search by...")
                    continue
                
            search_time = formatter.timeclock(search_time)
            tasks_by_mins = Task.select().where(Task.time_duration == search_time).order_by(Task.task_date)
            return tasks_by_mins

    def search_notes(self):
        """Find database entries by string matches"""
        formatter.clear_screen()

        while True:
            phrase = input("Search tasks by a given phrase:\n>>>").title().strip()
            if not phrase:
                print("Empty strings cannot be used to search tasks...")
                continue
            break

        tasks_by_phrase = Task.select().where((Task.task.contains(phrase)) | (Task.note.contains(phrase))).order_by(Task.task_date).order_by(Task.task_date)

        return tasks_by_phrase



class BaseModel(Model):
    class Meta:
        database = db


class Employee(BaseModel):
    first_name = CharField(max_length=15)
    last_name = CharField(max_length=15)
    ssn = CharField(max_length=12, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
        

class Task(BaseModel):
    task = CharField(max_length=15)
    task_date = DateField(formats=['%Y-%m-%d'])
    time_duration = TimeField(formats=['%H:%M'])
    note = CharField(max_length=15)
    employee = ForeignKeyField(model=Employee)


if __name__ == '__main__':
    Database()





