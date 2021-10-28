import os
import re
from glob import glob

from Utility import trailing_os_sep


def extract_solutions(ass_number: str, tutti_names: list) -> list:
    """ method extracting the solutions of the students. Returning a list containing the students who already
    have been corrected in some parts."""
    solution_files = find_solution_files(ass_number, tutti_names)
    corrected_students = []
    for student_name in solution_files:
        solution_content = []
        old_concatenated_solution = ''
        # saving the old file to check for changes
        if os.path.exists(
                f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment{ass_number}.txt'):
            with open(
                    f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment{ass_number}.txt',
                    'r') as f:
                old_concatenated_solution = f.readlines()
        for file in solution_files[student_name]:
            with open(file, 'r') as f:
                solution_content.extend(f.readlines())
            solution_content.append('\n')
        # if there is no difference between the old solution and the new one
        if "".join(solution_content) == "".join(old_concatenated_solution):
            corrected_students.append(student_name)
        else:
            with open(
                    f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment{ass_number}.txt',
                    'w') as f:
                f.writelines(solution_content)
    return corrected_students


def find_solution_files(ass_number: str, tutti_names: list) -> dict:
    tutti_solutions = {}
    for name in tutti_names:
        potential_folders = [f for f in glob(f'{trailing_os_sep(name)}assignments{os.path.sep}'
                                             f'*{str(int(ass_number))}*') if os.path.isdir(f)]
        solutions_files = []
        if len(potential_folders) > 0:
            if len(potential_folders) > 1:
                print('INFO: multiple solutions folders for', name)
                for folder in potential_folders:
                    print(potential_folders.index(folder), folder)
                i = -1
                while not 0 <= i < len(potential_folders):
                    index = input('Input the index for the correct folder: ')
                    if re.match('\d+', index):
                        i = int(index)
            else:
                i = 0

            for path, _, file_list in os.walk(potential_folders[i]):
                solutions_files.extend(map(lambda file: trailing_os_sep(path) + file, file_list))
        else:
            print('INFO: no solutions by', name)
        tutti_solutions[name] = solutions_files
    return tutti_solutions


def create_feedback(file_path: str, ass_number: str, corrector: str, exercise_points):
    """Goes through all names in the directory (except fuchs) and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points, corrector)
    feedback_path = f'{trailing_os_sep(file_path, True)}feedback{os.path.sep}assignment{ass_number}.txt'
    with open(feedback_path, 'w') as file:
        file.writelines(empty_feedback)
    print('generated file ' + feedback_path)


def generate_feedback_file(ass_number: str, exercise_points, corrector: str):
    """Does the feedback generation, using the assignment number, the exercise point distribution
    and the name of the corrector"""

    lines = ['Feedback Assignment ' + ass_number + '\n', '[0/10]\n', 'Tutor: ' + corrector + '\n', '\n', '\n']
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

# def generate_all_solution_templates(ass_number: str):
#     """Generates an empty solution for every student"""
#
#     ending = '.txt'
#     tutti_names = [f.path for f in os.scandir(source_path) if f.is_dir()]
#     for name in tutti_names:
#         if 'fuchs' not in name:
#             just_name = str(name).split(os.path.sep)
#             empty_solution_file = create_empty_solution(just_name[len(just_name) - 1], ass_number)
#             solution_path = f'{tailing_os_sep(name, True)}assignment{ass_number}{ending}'
#             with open(solution_path, 'w') as file:
#                 file.writelines(empty_solution_file)
#             print('generated file' + solution_path)
#
#
# def create_empty_solution(student: str, number: str):
#     """ creating a list of lines containing an empty template for the solution of a given
#     assigment number by using the assignment_config.txt"""
#
#     exercise_points = get_exercise_points(number)
#     lines = ['# Assignment ' + number + '\n', '# ' + student + '\n', '\n']
#     task_counter = 1
#     for exercise in exercise_points:
#         lines.append('\n')
#         if len(exercise) > 1:
#             lines.append('Task ' + str(task_counter) + ':\n')
#             subtask_counter = 'a'
#             for _ in exercise:
#                 lines.append('' + subtask_counter + ')\n')
#                 lines.append('\n')
#                 subtask_counter = chr(ord(subtask_counter) + 1)
#         else:
#             lines.append('Task ' + str(task_counter) + ':\n')
#         lines.append('\n')
#         task_counter += 1
#     return lines
