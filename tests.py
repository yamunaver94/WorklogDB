import datetime
import unittest  
from unittest.mock import patch

from peewee import *  

import main
import retrieve_data 
import formatter 

test_db = SqliteDatabase(':memory:')
DB_MODELS = (main.Employee, main.Task)

class TestEntries(unittest.TestCase):

    def setUp(self):
        db_is_closed = test_db.is_closed()
        if db_is_closed:
            test_db.connect(reuse_if_open=True)
        test_db.bind(DB_MODELS)
        test_db.create_tables(DB_MODELS)
        self.data_plug()
        self.database_tester = main.Database(show_menu=False)
        
    def data_plug(self):

        test_employees = {
            'id1' : {'first_name' : 'George', 'last_name' : 'Washington', 'ssn' : '000-01-1000'},
            'id2' : {'first_name' : 'Thomas', 'last_name' : 'Jefferson', 'ssn' : '000-02-2000'},
            'id3' : {'first_name' : 'John', 'last_name' : 'Adams', 'ssn' : '000-03-3000'}
        }

        test_tasks = [
            ('id1', 
                {
                'task' : 'Task_01', 
                'task_date' : datetime.date(year=2018, month=1, day=23), 
                'time_duration' : datetime.time(hour=0, minute=25), 
                'note' : "Note_A"
                }
            ),
            ('id2', 
                {
                'task' : 'Task_02', 
                'task_date' : datetime.date(year=2018, month=4, day=12), 
                'time_duration' : datetime.time(hour=1, minute=10), 
                'note' : "Note_B"
                }
            ),
            ('id2', 
                {
                'task' : 'Task_03', 
                'task_date' : datetime.date(year=2018, month=2, day=16), 
                'time_duration' : datetime.time(hour=0, minute=50), 
                'note' : "Note_B"
                }
            ),
            ('id1', 
                {'task' : 'Task_04', 
                'task_date' : datetime.date(year=2018, month=2, day=5), 
                'time_duration' : datetime.time(hour=0, minute=50), 
                'note' : "Note_D"
                }
            ),
            ('id3', 
                {'task' : 'Task_05', 
                'task_date' : datetime.date(year=2018, month=1, day=10), 
                'time_duration' : datetime.time(hour=2, minute=5), 
                'note' : "Note_F"
                }
            ),
            ('id2',
                {
                'task' : 'Task_06', 
                'task_date' : datetime.date(year=2018, month=2, day=13), 
                'time_duration' : datetime.time(hour=1, minute=10), 
                'note' : "Note_B"
                }
            )
        ]

        for task in test_tasks:
            emp_id = task[0]
            emp_ssn = test_employees[emp_id]['ssn']
            try:
                db_emp = main.Employee.get(main.Employee.ssn == emp_ssn)
            except DoesNotExist:
                db_emp = main.Employee.create(**test_employees[emp_id])

            task[1].update({'employee' : db_emp})
            main.Task.create(**task[1])

    def test_verify_employee(self):
        with patch('builtins.input', side_effect=['James Madison']):
            with patch('builtins.print', return_value=None):
                with patch('readchar.readkey', side_effect=['N']):
                    mock_ssn = {'ssn' : '000-04-4000'}
                    get_db_emp = retrieve_data.verify_employee(mock_ssn)
                self.assertEqual(get_db_emp.first_name, 'James')
                self.assertEqual(get_db_emp.last_name, 'Madison')

    def test_verify_employee_changed(self):
        with patch('builtins.input', side_effect=['Thomas Jefferson']):
            with patch('builtins.print', return_value=None):
                with patch('readchar.readkey', side_effect=['Y', '2']):
                    mock_ssn = {'ssn' : '000-05-0000'}
                    test_emp_id = retrieve_data.verify_employee(mock_ssn)
                    test_emp = main.Employee.get(main.Employee.id == test_emp_id)
                    self.assertNotEqual(mock_ssn, test_emp.ssn)  

    def test_delete_entry_no_tasks(self):
        with patch('builtins.input', side_effect=['100-20-3000']):
            with patch('builtins.print', return_value=None):
                db_ssn = self.database_tester.delete_entry()
                self.assertFalse(db_ssn)

    def test_delete_entry(self):
        with patch('builtins.input', side_effect=['000-01-1000']):
            with patch('builtins.print', return_value=None):
                with patch('readchar.readkey', side_effect=[1]):
                    task_removed = self.database_tester.delete_entry()
                self.assertEqual(task_removed, 1)

    def test_search_dates_order(self):
        with patch('builtins.input', side_effect=['2019-02-05', '14']):
            with patch('builtins.print', return_value=None):
                get_test_dates = self.database_tester.search_dates()
                for i, date in enumerate(get_test_dates[:len(get_test_dates) -1]):
                    self.assertLessEqual(date, date[i + 1])

    def test_search_notes(self):
        with patch('builtins.input', side_effect=['B']):
            with patch('builtins.print', return_value=None):
                get_phrases = self.database_tester.search_notes()
                self.assertEqual(len(get_phrases), 3)

    def test_add_entry(self):
        with patch('builtins.input', side_effect=['008-00-0000', 'Ulysses Grant', 'Inauguration Speech', 
                                                    '1869-03-04', '35', 'Became 18th US President']):
            with patch('builtins.print', return_value=None):
                with patch('readchar.readkey', side_effect=['B']):
                    entry_added = self.database_tester.add_entry()
                    self.assertTrue(entry_added)

    def test_filter_name(self):
        self.assertEqual(formatter.filter_name('George Herbert Walker Bush'), "George Bush")

    def tearDown(self):
        test_db.drop_tables(DB_MODELS)

if __name__ == '__main__':
    unittest.main()

