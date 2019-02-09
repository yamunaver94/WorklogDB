import main

import readchar

import formatter

class MainMenuView:

    def __init__(self, options):
        self.render_main_menu(options)

    def render_main_menu(self, options):
        show_menu = ''.join(['[ {key} ] - {option}\n'.format(key=key, option=value.__doc__) # string of `menu_options`
                    for key, value in options.items()])

        menu_ids = options.keys()
        
        while True:
            formatter.clear_screen()
            print(show_menu + "\nSelect from one of the above options")
            option = readchar.readkey().upper()

            while option not in menu_ids and option:
                print(f'Cannot perform selection -> ID entered: [{option}]')
                option = readchar.readkey().upper()

            action_taken = options[option]()
            if action_taken or not action_taken:
                continue
            sys.exit()

def employee_list(person):
    '''Menu showing employees with the same first and last name'''
    name_results = main.Employee.select().where(main.Employee.first_name == person['first_name'], 
                                                main.Employee.last_name == person['last_name'])
    if name_results:
        official_name = '{first_name} {last_name}'.format(**person)
        print(f'\nThere are {len(name_results)} employees with the name: {official_name}')
        while True:
            print('To review other matches: [Y]es / [N]o')

            lookup = readchar.readkey().upper()
            if lookup not in ['Y', 'N']:
                print('Cannot process request...')
                continue
            break
        if lookup == 'N':
            return lookup # if the employee does not exist; add a new employee with the same first and last name

        print('\nSelected -->> Employee Name: {first_name} {last_name} - SSN#: {ssn}'.format(**person))

        ids = []
        menu_results =  '*' * 20
        for n in name_results:
            ids.append(str(n.id))
            menu_results += f'\nID#: {n.id}\nEmployee Name: {str(n)}\nSSN#: {n.ssn}\n'
        menu_results += '*' * 20 + '\nPress [N] to not modify the employee record and EXIT menu.'
        print(menu_results)
        return ids
    return None