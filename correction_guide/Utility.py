import ast
import os
import re
import requests
from DB import *
from Paths import config_path, source_path


taskString = ['Task', 'task', 'Aufgabe', 'aufgabe', 'Lösung', 'lösung', 'Loesung', 'loesung', 'Solution', 'solution',
              'Exercise', 'exercise', r'Ex\.?', r'ex\.?', 'Number', 'number', r'No\.?', r'no\.?', 'Nummer', 'nummer',
              r'Nr\.?', r'nr\.?']


def trailing_os_sep(path: str, should_have_sep: bool = True):
    """Small helper function that ensures that there is or is not a tailing path separator"""

    if path[-1] != os.sep and should_have_sep:
        return path + os.sep
    elif path[-1] == os.sep and not should_have_sep:
        return path[0:-1]
    return path


def get_configured_exercise_points(ass_number: str):
    """Reads the points distribution of a given assignment number from the assignment config file"""

    exercise_points = []
    with open(config_path + 'assignment_config.txt', 'r') as file:
        for line in file.readlines():
            if line.strip().startswith(ass_number):
                for exercise in line.strip().split(' : ', 1)[1].split(', '):
                    exercise_points.append(ast.literal_eval(exercise))
    return exercise_points


def increment_pointer(current_pointer: str, exercise_points: list):
    """Increments the progress pointer by one step, examples for ex_points [[3], [1,1], [4]]:
    1. -> 2.a  /  2.a -> 2.b  /  2.b -> 3."""

    (task, subtask) = current_pointer.split('.', 1)
    # increment main task when there were no subtasks before or all previous subtasks are done
    if subtask == '' or len(exercise_points[int(task) - 1]) <= ord(subtask) - 96:
        task = str(int(task) + 1)
        if int(task) <= len(exercise_points):
            subtask = 'a' if len(exercise_points[int(task) - 1]) > 1 else ''
    # increment just subtask
    else:
        subtask = chr(ord(subtask) + 1)
    return f'{task}.{subtask}'


def insert_in_file(file_path: str, exercise_pointer: str, points: str, text: str):
    """Method to edit/ fill in the correction into a pre-generated feedback file.
    This includes the points and a text for a given exercise."""

    with open(file_path, 'r') as file:
        current_file = file.readlines()
    # preparing point amounts
    total = str(float(current_file[1][1:].split('/', 1)[0]) + float(points)).split('.0', 1)[0]
    points = points.split('.0', 1)[0]
    index = get_index(current_file, exercise_pointer)
    current_file[index] = current_file[index].replace('[0/', '[' + points + '/', 1)
    current_file.insert(index + 1, text + '\n')
    current_file[1] = current_file[1].replace(current_file[1].split('/', 1)[0], '[' + total)
    with open(file_path, 'w') as file:
        file.writelines(current_file)
    return total


def delete_old_feedback(file_path: str, pointer: str, exercise_points: list):
    """ to delete the feedback of a task or subtask from a feedback_file. Removing the previous given
    points from the total points and setting the points from the task to 0 """
    with open(file_path, 'r') as file:
        current_file = file.readlines()
    index = get_index(current_file, pointer)
    next_index = get_index(current_file, increment_pointer(pointer, exercise_points))
    points = float(current_file[index].split('/', 1)[0].split('[', 1)[1])
    total = str(float(current_file[1][1:].split('/', 1)[0]) - points).split('.0', 1)[0]
    current_file[index] = re.sub('\[[0-9](.5)?/', '[0/', current_file[index])
    index += 1
    # - 2 because there are always blank lines
    while index < next_index - 2:
        current_file[index] = ''
        index += 1
    current_file[1] = current_file[1].replace(current_file[1].split('/', 1)[0], '[' + total)
    with open(file_path, 'w') as file:
        file.writelines(current_file)


def insert_total_in_db(ass_number: str, tutti_names: list = [f.path for f in os.scandir(source_path) if f.is_dir()]):
    if input('you sure? (y/n)\n') == 'y':
        print('inserting points for assignment', ass_number + ':')
        for name in tutti_names:
            with open(f'{trailing_os_sep(name, True)}feedback{os.path.sep}assignment{ass_number}.txt', 'r') as f:
                total = str(float(f.readlines()[1][1:].split('/', 1)[0]))
            insert_in_db(str(name).rsplit(os.path.sep, 1)[1], ass_number, total)
            print('-', str(name).rsplit(os.path.sep, 1)[1], total)
        update_db()
    else:
        print('probably the better choice')


def insert_in_db(student_name: str, ass_number: str, total_points: str):
    sql_query(f"UPDATE points_table SET ass_{ass_number} = {total_points} WHERE student_name = '{student_name}'")


def get_index(current_file, exercise_pointer: str):
    """Method to get the start index of an exercise in the feedback or solution file"""

    index: int = 0
    (task, subtask) = exercise_pointer.split('.', 1)
    match = '(' + '|'.join(taskString) + ')? *' + task
    for line in current_file:
        if re.match('^#?%* *' + match + ' *[:.)].*', line):
            if subtask != match[-2].lower() and subtask != '':
                match = '(' + match + ')?(' + subtask + '|' + str(subtask).upper() + ')'
            else:
                break
        index += 1
    if index == len(current_file):
        index = -1
    return index


def get_solution(current_file: list, exercise_pointer: str, exercise_points: list, printing=True):
    """Method to get the solution of an exercise of a person.
    Getting to the end of the exercise before and taking then
    everything to the end of the current task"""

    solution = []
    if printing:
        print(exercise_pointer)
    index = get_index(current_file, exercise_pointer)
    next_index = -1
    while int(exercise_pointer.split('.', 1)[0]) <= len(exercise_points) and next_index < 0:
        exercise_pointer = increment_pointer(exercise_pointer, exercise_points)
        next_index = get_index(current_file, exercise_pointer)
    if next_index == -1:
        next_index = len(current_file)
    while index < next_index:
        if printing:
            print(current_file[index].strip())
        else:
            solution.append(current_file[index].strip())
        index += 1
    return solution


def solution_exists(file: list, pointer):
    """ Checking if the person made the exercise which means there is a exercise for the current pointer"""

    return get_index(file, pointer) > 0


def check_internet_connection() -> bool:
    try:
        requests.get('https://port.halloibims.com', timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        print('ERROR: not connected to the internet, correction starts in offline mode!')
        return False


def get_input(message: str):
    while True:
        inp = str(input(message + ' [y/n] \n'))
        if inp.lower() in ['n', 'y']:
            if inp == 'y':
                return True
            return False
        else:
            print('Invalid input, try again.')