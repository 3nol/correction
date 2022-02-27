import os
import re
from ast import literal_eval
from glob import glob

from Config import GlobalConstants as gc
from data_structures.ExercisePointer import ExercisePointer
from data_structures.FileDictionary import FileDictionary
from utilities.DatabaseConnector import is_db_available, insert_single_student, update_total_points
from utilities.Tree import print_tree
from utilities.Utility import \
    trailing_sep, get_input, get_index, insert_in_file, sol_exists, get_solution, load_feedback, delete_old_feedback


# -- FINDING SOLUTIONS --

def extract_solutions(ass_number: str, student_names: list, feedbacks: FileDictionary) -> list[str]:
    """Extracting the solutions of the students. Returning a list containing the students who already
    have been corrected in some parts"""

    # storing lambda functions for generating the individual path names
    c_path = lambda x: f'''{trailing_sep(x) + trailing_sep(gc.get('concat_folder'))}c_assignment{ass_number}.txt'''
    f_path = lambda x: f'''{trailing_sep(x) + trailing_sep(gc.get('feedback_folder'))}assignment{ass_number}.txt'''

    if feedbacks.get('_solution_files') is None \
            or not get_input('Do you want to use previously selected solution files? [y/n]'):
        # let script find solution files automatically, you have to select the correct ones
        solution_files = find_solution_files(ass_number, student_names)
        feedbacks.insert('_solution_files', str(solution_files))
    else:
        # use the previously defined ones
        solution_files = literal_eval(feedbacks.get('_solution_files'))
    corrected_students = []
    for student_name in solution_files:
        solution_content = []
        for file in sorted(solution_files[student_name]):
            if not is_ignored_file(file):
                with open(file, mode='r', errors='replace', encoding='utf-8') as f:
                    # get all solution content, someone has created for an assignment
                    solution_content.extend(f.readlines())
        # saving the old file to check for changes
        if os.path.exists(c_path(student_name)):
            with open(c_path(student_name), mode='r', errors='replace', encoding='utf-8') as f:
                old_concatenated_solution = f.readlines()
            # if there is no difference between the old solution and the new one
            if os.path.exists(f_path(student_name)):
                if "".join(solution_content) != "".join(old_concatenated_solution):
                    compare_old_correction_to_new_solution(student_name, ass_number, solution_content,
                                                           old_concatenated_solution, feedbacks)
                corrected_students.append(student_name)
        # updated the c_assignment file
        with open(c_path(student_name), mode='w', errors='replace', encoding='utf-8') as f:
            f.writelines(solution_content)
        print('INFO: wrote to concatenated successfully:', student_name)
    return corrected_students


def find_solution_files(ass_number: str, student_names: list) -> dict[str, list[str]]:
    """Super smart method for detecting solutions in almost any folder structure. If multiple options are possible,
    the tutor is asked to decide which one to pick"""

    solutions = {}
    for name in student_names:
        potential_folders = [f for f in glob(f'{trailing_sep(name)}**{os.path.sep}*{str(int(ass_number))}*',
                                             recursive=True) if os.path.isdir(f)]
        solutions_files = []
        if len(potential_folders) > 0:
            if len(potential_folders) > 1:
                print('INFO: multiple solutions folders for', name)
                for folder in potential_folders:
                    print(potential_folders.index(folder), folder)
                i = -1
                while not 0 <= i < len(potential_folders):
                    index = input('Input the index for the correct folder: ')
                    if re.match(r'\d+', index):
                        i = int(index)
            else:
                i = 0
            for path, _, file_list in os.walk(potential_folders[i]):
                solutions_files.extend(map(lambda file: trailing_sep(path) + file, file_list))
        else:
            print_tree(name, exclude=gc.get('excluded_filetypes'), relative_path=True, show_hidden=False)
            print('INFO: no solutions by', str(name).rsplit(os.path.sep, 1)[1])
            while True:
                files = get_input('Enter solution file paths (inside the student\'s directory), separated by comma.\n'
                                  'Leave blank if no solution exists.',
                                  input_type='text', text_wrap=False)
                if files.strip() == '':
                    break
                files = list(map(lambda f: trailing_sep(name) + str(f).strip(), files.split(',')))
                if all(map(os.path.isfile, files)):
                    solutions_files.extend(files)
                    break
                else:
                    print('INFO: at least one file does not exist, try again')
            print('\n')
        solutions[name] = solutions_files
    return solutions


# -- ANALYZE CHANGES IN SOLUTIONS --

def compare_old_correction_to_new_solution(student_name: str, ass_number: str, new_solution: list, old_solution: list,
                                           feedbacks: FileDictionary) -> None:
    """Helps to correct a partial corrected assignment by cycling through all the tasks and subtasks
    which already have a feedback. If there are changes in the students solution, the solution and the corresponding
    feedback is printed"""

    just_name = str(student_name).rsplit(os.path.sep, 1)[1]
    feedback_path = f'''{trailing_sep(student_name) + trailing_sep(gc.get('feedback_folder'))
                         }assignment{ass_number}.txt'''
    exercise_points = gc.get(f'points_{ass_number}')
    pointer = ExercisePointer(ass_number)

    with open(feedback_path, mode='r', errors='replace', encoding='utf-8') as f:
        feedback = f.readlines()

    # loop while there is still a feedback or no more exercises
    while int(pointer.split()[0]) <= len(exercise_points) and feedback[get_index(feedback, pointer) + 1] != '\n':
        task, subtask = pointer.split()
        # get the maximum possible points for this exercise, either from the subtask or main task
        possible_points = exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
            if len(exercise_points[int(task) - 1]) > 1 else \
            exercise_points[int(task) - 1][0]
        # solution status indicator: 0 = nothing changed, 1 = changes present, 2 = no solution
        solution_status = 0
        # if there is a solution
        if sol_exists(new_solution, pointer):
            new_exercise = get_solution(new_solution, pointer, exercise_points, printing=False)
            old_exercise = get_solution(old_solution, pointer, exercise_points, printing=False) \
                if sol_exists(old_solution, pointer) else []
            # if there is a difference between the two exercises
            if new_exercise != old_exercise:
                print('\n')
                for line in new_exercise:
                    print(str(line).strip())
                solution_status = 1
        # if there is no solution i could have been deleted and therefore we ask if the task is still there
        else:
            for line in new_solution:
                print(str(line).strip())
            solution_status = 1 if get_input('Is the task ' + str(pointer) + ' in the file? [y/n]') else 2
        print('\n-------- ' + just_name + ' --------\n')
        # handling the solution status: 1 -> new correction, 2 -> insert 0 points in feedback
        points = 0
        comment = 'No solution.'
        if solution_status == 1:
            print('\nFeedback for the previous version:\n')
            get_solution(feedback, pointer, exercise_points)
            if not get_input('Is the feedback still correct? [y/n]'):
                # if feedback is not appropriate anymore, a comment is asked for again
                loaded, comment = load_feedback(feedbacks, pointer, new_solution)
                if loaded:
                    points, comment = comment
                elif not get_input('Is the solution correct? [y/n]'):
                    while True:
                        points = get_input('How many points should ' + just_name + ' get for this exercise?\n'
                                           + str(possible_points) + ' are possible!', 'numeric')
                        # check validity of inputted points
                        if 0.0 <= points <= possible_points:
                            break
                    feedbacks.insert('', str(points) + ', ' + comment.replace('\n', ' '), prefix=pointer + '_')
                else:
                    # solution is correct -> give max. points
                    points = possible_points
            else:
                solution_status = 0
        if solution_status > 0:
            delete_old_feedback(feedback_path, pointer, exercise_points)
            new_total_points = insert_in_file(feedback_path, pointer, str(points), comment)
            if is_db_available():
                insert_single_student(just_name, ass_number, new_total_points)
                update_total_points()
        pointer.increment()


# -- FEEDBACK GENERATION --

def create_feedback(file_path: str, ass_number: str, exercise_points) -> None:
    """Goes through all names in the directory and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points)
    feedback_path = f'''{trailing_sep(file_path, True) + trailing_sep(gc.get('feedback_folder'))
                         }assignment{ass_number}.txt'''
    with open(feedback_path, mode='w', errors='replace', encoding='utf-8') as file:
        file.writelines(empty_feedback)
    print('generated file ' + feedback_path)


def generate_feedback_file(ass_number: str, exercise_points) -> list[str]:
    """Does the feedback generation, using the assignment number, the exercise point distribution
    and the name of the corrector"""

    lines = ['Feedback Assignment ' + ass_number + '\n', '[0/10]\n', 'Tutor: ' + gc.get('corrector') + '\n', '\n', '\n']
    task_counter = 1
    for exercise in exercise_points:
        if len(exercise) > 1:
            lines.append('Task ' + str(task_counter) + ':\n')
            subtask_counter = 'a'
            for subtask in exercise:
                lines.append(subtask_counter + ') [0/' + str(subtask) + ']\n')
                lines.append('\n')
                subtask_counter = chr(ord(subtask_counter) + 1)
        else:
            lines.append('Task ' + str(task_counter) + ': [0/' + str(exercise[0]) + ']\n')
            lines.append('\n')
        lines.append('\n')
        task_counter += 1
    return lines


def is_ignored_file(file_path: str) -> bool:
    """Checks whether the file is on the list of ignored files, see Config.py"""

    file_name = file_path.split(os.path.sep)[-1]
    for ignore in gc.get('excluded_filetypes'):
        if re.match(ignore, file_name):
            return True
    return False
