import os
from Utility import tailing_os_sep


def extract_solutions():
    print('not implemented yet')


def create_feedbacks(file_path: str, ass_number: str, corrector: str, exercise_points):
    """Goes through all names in the directory (except fuchs) and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points, corrector)
    for name in [f.path for f in os.scandir(file_path) if f.is_dir()]:
        if 'fuchs' not in name:
            feedback_path = f'{tailing_os_sep(name, True)}feedback{os.path.sep}assignment{ass_number}.txt'
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
