import os
import re
import textwrap
from typing import Any

from assignment_handler.Config import GlobalConstants as gc
from assignment_handler.data_structures.ExercisePointer import ExercisePointer
from assignment_handler.data_structures.FileDictionary import FileDictionary


# -- INDEX MAGIC --

def get_index(current_file, exercise_pointer: ExercisePointer, start_index: int = 0) -> int:
    """Super magic method to get the start index of an exercise in the feedback or solution file"""

    # defining match encasing, such as 1.)
    encase_match = lambda m: r'^[#%/(\t+-]* *' + str(m) + ' *[:.) \n+-]{1,3}'

    index = 0
    task, subtask = exercise_pointer.split()
    # defining task and subtask identifier structure
    task_match = rf'''({'|'.join(gc.get('maintask_prefixes'))})? *0?{task}'''
    subtask_match = rf'''({'|'.join(gc.get('subtask_prefixes'))})? *({subtask}|{str(subtask).upper()})'''
    identifier_match = task_match
    found = False
    # detecting separate task and subtask identifier
    for line in current_file:
        # if a task match occurs, match is changed to subtask match, if it matches again, the loop is exited
        if re.match(encase_match(identifier_match), line):
            # index -4 corresponds to the subtask value in subtask_match
            if subtask != identifier_match[-4] and subtask != '':
                identifier_match = rf'''({task_match})? *{subtask_match}'''
                if re.match(encase_match(identifier_match), line):
                    found = True
                    break
            elif index >= start_index:
                found = True
                break
        index += 1
    # detecting task and subtask identifier on the same line
    if index >= len(current_file) - 1 and not found:
        index = 0
        for line in current_file:
            # if a task match occurs, the loop is exited
            if re.match(encase_match(rf'''{task_match} *{subtask_match}'''), line) and index >= start_index:
                found = True
                break
            index += 1
    if index >= len(current_file) - 1 and not found:
        index = -1
    return index


# -- SOLUTION & FEEDBACK HANDLING --

def get_solution(current_file: list, exercise_pointer: ExercisePointer, exercise_points: list,
                 printing=True) -> list[str]:
    """Method to get the solution of an exercise of a person.
    Getting to the end of the exercise before and taking then
    everything to the end of the current task"""

    solution = []
    if printing:
        pp = str(exercise_pointer)
        print(f'''\n┌{len(pp) * '─'}┐\n│{pp}│\n└{len(pp) * '─'}┘''')
    task, subtask = exercise_pointer.split()
    prev_index = 0 if task == '1' and subtask in ['', 'a'] \
        else get_index(current_file, exercise_pointer.decrement(inplace=False))
    index = get_index(current_file, exercise_pointer, start_index=prev_index)
    next_index = -1
    while int(exercise_pointer.split()[0]) <= len(exercise_points) and next_index < 0:
        exercise_pointer = exercise_pointer.increment(inplace=False)
        next_index = get_index(current_file, exercise_pointer, start_index=index)
    if next_index == -1:
        next_index = len(current_file)
    while index < next_index:
        if printing:
            print(current_file[index].strip())
        solution.append(current_file[index].strip())
        index += 1
    return solution


def insert_in_file(file_path: str, exercise_pointer: ExercisePointer, points: str, text: str) -> str:
    """Method to edit/ fill in the correction into a pre-generated feedback file.
    This includes the points and a text for a given exercise."""

    with open(file_path, mode='r', errors='replace', encoding='utf-8') as file:
        current_file = file.readlines()
    # preparing point amounts
    new_total = str(float(current_file[1][1:].split('/', 1)[0]) + float(points)).split('.0', 1)[0]
    points = points.split('.0', 1)[0]
    index = get_index(current_file, exercise_pointer)
    current_file[index] = current_file[index].replace('[0/', '[' + points + '/', 1)
    current_file.insert(index + 1, text + '\n')
    current_file[1] = current_file[1].replace(current_file[1].split('/', 1)[0], '[' + new_total)
    with open(file_path, mode='w', errors='replace', encoding='utf-8') as file:
        file.writelines(current_file)
    return new_total


def load_feedback(feedbacks: FileDictionary, exercise_pointer: ExercisePointer,
                  solution_file: list) -> tuple[bool, Any]:
    """Helper method that asks for a feedback comment. Alternatively a feedback can also be loaded with the id
    Additionally, with '>s' the entire solution can be printed out."""

    pp = str(exercise_pointer)
    while True:
        comment = get_input('Please enter some comments (without newlines).\n'
                            'You can also load a stored feedback using \'>feedback_id\'.', 'text')
        if comment.startswith('>'):
            if comment.strip() == '>s':
                for line in solution_file:
                    print(str(line).strip())
                print(f'''\n┌{len(pp) * '─'}┐\n│{pp}│\n└{len(pp) * '─'}┘''')
                continue
            else:
                if feedbacks.get(pp + '_' + comment[1:]) is not None:
                    # feedback is loaded and split into 2 components: points and comment
                    print('INFO: feedback was loaded successfully')
                    p, c = feedbacks.get(pp + '_' + comment[1:]).split(', ', 1)
                    return True, (p, textwrap.fill(c, 80))
                else:
                    print('INFO: feedback was not found, try again')
                    continue
        return False, comment


def delete_old_feedback(file_path: str, exercise_pointer: ExercisePointer, exercise_points: list) -> None:
    """To delete the feedback of a task or subtask from a feedback_file. Removing the previous given
    points from the total points and setting the points from the task to 0 """

    with open(file_path, mode='r', errors='replace', encoding='utf-8') as file:
        current_file = file.readlines()
    index = get_index(current_file, exercise_pointer)
    next_pointer = exercise_pointer.increment(inplace=False)
    next_index = get_index(current_file, next_pointer)
    next_index = len(current_file) + 1 if next_index == -1 else next_index

    points = float(current_file[index].split('/', 1)[0].split('[', 1)[1])
    total = str(float(current_file[1][1:].split('/', 1)[0]) - points).split('.0', 1)[0]
    current_file[index] = re.sub(r'\[[0-9](.5)?/', '[0/', current_file[index])
    index += 1
    # there is always 1 blank line between subtasks and 2 blank lines between tasks (3 because of Task X headline)
    blanks = 1 if exercise_pointer.split()[0] == next_pointer.split()[0] or \
                  int(exercise_pointer.split()[0]) == len(exercise_points) else 3
    while index < next_index - blanks and index < len(current_file):
        current_file[index] = ''
        index += 1
    current_file[1] = current_file[1].replace(current_file[1].split('/', 1)[0], '[' + total)
    with open(file_path, mode='w', errors='replace', encoding='utf-8') as file:
        file.writelines(current_file)


# -- HELPER METHODS --

def trailing_sep(path: str, should_have_sep: bool = True) -> str:
    """Small helper function that ensures that there is or is not a tailing path separator"""

    if path[-1] != os.sep and should_have_sep:
        return path + os.sep
    elif path[-1] == os.sep and not should_have_sep:
        return path[0:-1]
    return path


def sum_sublist_lengths(some_list: list) -> int:
    """Helper function for summing up all lengths, lists inside a list have"""
    return sum(map(lambda x: len(x), some_list))


def sol_exists(file: list, exercise_pointer: ExercisePointer):
    """Checks if the person solved the exercise, i.e. there exists an exercise for the current pointer"""
    return get_index(file, exercise_pointer,
                     start_index=get_index(file, exercise_pointer.decrement(inplace=False))) >= 0


def get_input(message: str, input_type: str = 'boolean', text_wrap=True) -> Any:
    """Retrieves an input from the console in a failsafe way"""

    while True:
        inp = str(input(message + '\n'))
        if input_type == 'boolean' and inp.lower() in ['n', 'y']:
            # boolean values for being a 'yes'
            return inp.lower() == 'y'
        elif input_type == 'numeric' and re.match(r'\d+([.,]5)?', inp):
            # parse points, make sure to use points, not commas
            return float(inp.replace(',', '.'))
        elif input_type == 'text':
            # normal string input, but can be wrapped at length 80
            if text_wrap:
                return textwrap.fill(str(inp), 80) if inp != '' else ' '
            return str(inp)
        else:
            print('Invalid input, try again.')
