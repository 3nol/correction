import os
import re
from glob import glob
from Utility import *
from Paths import corrector


def extract_solutions(ass_number: str, tutti_names: list) -> list:
    """Extracting the solutions of the students. Returning a list containing the students who already
    have been corrected in some parts"""

    solution_files = find_solution_files(ass_number, tutti_names)
    corrected_students = []
    for student_name in solution_files:
        solution_content = []
        old_concatenated_solution = ''
        for file in solution_files[student_name]:
            with open(file, 'r') as f:
                solution_content.extend(f.readlines())
            solution_content.append('\n')
        # saving the old file to check for changes
        if os.path.exists(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                          f'{ass_number}.txt'):
            with open(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                      f'{ass_number}.txt', 'r') as f:
                old_concatenated_solution = f.readlines()
            # if there is no difference between the old solution and the new one
            if "".join(solution_content) == "".join(old_concatenated_solution):
                corrected_students.append(student_name)
            elif os.path.exists(f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{ass_number}.txt'):
                compare_old_correction_to_new_solution(student_name, ass_number, solution_content, old_concatenated_solution)
                corrected_students.append(student_name)
        with open(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                    f'{ass_number}.txt', 'w') as f:
            f.writelines(solution_content)
    return corrected_students


def compare_old_correction_to_new_solution(student_name: str, ass_number: str, solution_content: list, old_solution: list):
    """Helps to correct a partial corrected assignment by cycling through all the tasks and subtasks
    which already have a feedback. If there are changes in the students solution, the solution and the corresponding
    feedback is printed"""

    feedback_path = f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{ass_number}.txt'
    with open(feedback_path, 'r') as f:
        feedback = f.readlines()
    exercise_points = get_configured_exercise_points(ass_number)
    just_name = str(student_name).rsplit(os.path.sep, 1)[1]
    pointer = '1.' if len(exercise_points[0]) == 1 else '1.a'
    # loop while there is still a feedback or no more exercises
    while int(pointer.split('.', 1)[0]) <= len(exercise_points) and feedback[get_index(feedback, pointer) + 1] != '\n':
        # if there is a solution
        if solution_exists(solution_content, pointer):
            new_exercise = get_solution(solution_content, pointer, exercise_points, printing=False)
            old_exercise = get_solution(old_solution, pointer, exercise_points, printing=False)
            (task, subtask) = pointer.split('.', 1)
            # get the maximum possible points for this exercise, either from the subtask or main task
            possible_points = exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
                if len(exercise_points[int(task) - 1]) > 1 else \
                exercise_points[int(task) - 1][0]
            # if there is a difference between the two exercises
            if new_exercise != old_exercise:
                for line in new_exercise:
                    print(line)
                print('-------- feedback for the old exercise ---------')
                get_solution(feedback, pointer, exercise_points)
                while True:
                    correctness = str(input('Is the feedback still correct? [y/n] \n'))
                    if correctness.lower() in ['n', 'y']:
                        break
                    else:
                        print('Invalid input, try again.')
                if correctness.lower() == 'n':
                    comment = str(input('Please enter some comments (without newlines!)\n'))
                    while True:
                        points = float(
                            input('How many points should get ' + just_name + ' for this exercise?\n'
                                  + str(possible_points) + ' are possible!\n'))
                        # check validity of inputted points
                        if 0.0 <= points <= possible_points:
                            break
                    delete_old_feedback(feedback_path, pointer, exercise_points)
                    new_total_points = insert_in_file(feedback_path, pointer, str(points), comment)
                    insert_in_db(just_name, ass_number, new_total_points)
                    update_db()
        # if there is no solution i could have been deleted and therefore we just give 0 points
        else:
            points = 0
            comment = 'no solution'
            delete_old_feedback(feedback_path, pointer, exercise_points)
            new_total_points = insert_in_file(feedback_path, pointer, str(points), comment)
            insert_in_db(just_name, ass_number, new_total_points)
            update_db()
        pointer = increment_pointer(pointer, exercise_points)


def find_solution_files(ass_number: str, tutti_names: list) -> dict:
    """Super smart method for detecting solutions in almost any folder structure. If multiple options are possible,
    the tutor is asked to decide which one to pick"""

    tutti_solutions = {}
    for name in tutti_names:
        potential_folders = [f for f in glob(f'{trailing_os_sep(name)}**{os.path.sep}*{str(int(ass_number))}*',
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
                solutions_files.extend(map(lambda file: trailing_os_sep(path) + file, file_list))
        else:
            print('INFO: no solutions by', name)
        tutti_solutions[name] = solutions_files
    return tutti_solutions


def create_feedback(file_path: str, ass_number: str, exercise_points):
    """Goes through all names in the directory (except ***REMOVED***) and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points)
    feedback_path = f'{trailing_os_sep(file_path, True)}feedback{os.path.sep}assignment{ass_number}.txt'
    with open(feedback_path, 'w') as file:
        file.writelines(empty_feedback)
    print('generated file ' + feedback_path)


def generate_feedback_file(ass_number: str, exercise_points):
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
