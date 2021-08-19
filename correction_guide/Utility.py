import ast
import os

from Private import config_path


def tailing_os_sep(path: str, should_have_sep: bool = True) -> str:
    """Small helper function that ensures that there is or is not a tailing path separator"""

    if path[-1] != os.sep and should_have_sep:
        return path + os.sep
    elif path[-1] == os.sep and not should_have_sep:
        return path[0:-1]
    return path


def get_exercise_points(ass_number: str):
    """Reads the points distribution of a given assignment number from the assignment config file"""

    exercise_points = []
    with open(config_path + 'assignment_config.txt', 'r') as file:
        for line in file.readlines():
            if line.strip().startswith(ass_number):
                for exercise in line.strip().split(' : ', 1)[1].split(', '):
                    exercise_points.append(ast.literal_eval(exercise))
    return exercise_points


def create_feedbacks(file_path: str, ass_number: str, corrector: str, exercise_points):
    """Goes through all names in the directory (except ***REMOVED***) and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points, corrector)
    for name in [f.path for f in os.scandir(file_path) if f.is_dir()]:
        if '***REMOVED***' not in name:
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


def insert_at(file_path: str, exercise_pointer: str, points: str, text: str) -> None:
    """Method to edit/ fill in the correction into a pre-generated feedback file.
    This includes the points and a text for a given exercise."""

    with open(file_path, 'r') as file:
        current_file = file.readlines()
    index = 0
    (task, subtask) = exercise_pointer.split('.', 1)
    match = 'Task ' + task
    for line in current_file:
        if line.startswith(match):
            if match != subtask and subtask != '':
                match = subtask
            else:
                break
        index += 1
    current_file[index] = current_file[index].replace('[0/', '[' + points + '/', 1)
    current_file.insert(index + 1, text + '\n')
    with open(file_path, 'w') as file:
        file.writelines(current_file)
