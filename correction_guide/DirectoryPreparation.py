from glob import glob
from Utility import *
from Paths import corrector
import FileDictionary


def extract_solutions(ass_number: str, tutti_names: list, feedbacks: FileDictionary) -> list:
    """Extracting the solutions of the students. Returning a list containing the students who already
    have been corrected in some parts"""

    solution_files = find_solution_files(ass_number, tutti_names)
    corrected_students = []
    for student_name in solution_files:
        solution_content = []
        for file in sorted(solution_files[student_name]):
            if not is_ignored_file(file):
                with open(file, mode='r', errors='replace') as f:
                    solution_content.extend(f.readlines())
                solution_content.append('\n')
        # saving the old file to check for changes
        if os.path.exists(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                          f'{ass_number}.txt'):
            with open(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                      f'{ass_number}.txt', mode='r', errors='replace') as f:
                old_concatenated_solution = f.readlines()
            # if there is no difference between the old solution and the new one
            if os.path.exists(f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{ass_number}.txt'):
                if "".join(solution_content) != "".join(old_concatenated_solution):
                    compare_old_correction_to_new_solution(student_name, ass_number, solution_content,
                                                           old_concatenated_solution, feedbacks)
                corrected_students.append(student_name)
        with open(f'{trailing_os_sep(student_name)}concatenated{os.path.sep}concatenated_assignment'
                  f'{ass_number}.txt', mode='w', errors='replace') as f:
            f.writelines(solution_content)
        print('INFO: wrote to concatenated successfully:', student_name)
    return corrected_students


def compare_old_correction_to_new_solution(student_name: str, ass_number: str, new_solution: list, old_solution: list,
                                           feedbacks: FileDictionary):
    """Helps to correct a partial corrected assignment by cycling through all the tasks and subtasks
    which already have a feedback. If there are changes in the students solution, the solution and the corresponding
    feedback is printed"""

    just_name = str(student_name).rsplit(os.path.sep, 1)[1]
    print('\n-------- ' + just_name + ' --------\n')
    feedback_path = f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{ass_number}.txt'
    with open(feedback_path, mode='r', errors='replace') as f:
        feedback = f.readlines()
    exercise_points = get_configured_exercise_points(ass_number)
    pointer = '1.' if len(exercise_points[0]) == 1 else '1.a'
    # loop while there is still a feedback or no more exercises
    while int(pointer.split('.', 1)[0]) <= len(exercise_points) and feedback[get_index(feedback, pointer) + 1] != '\n':
        (task, subtask) = pointer.split('.', 1)
        # get the maximum possible points for this exercise, either from the subtask or main task
        possible_points = exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
            if len(exercise_points[int(task) - 1]) > 1 else \
            exercise_points[int(task) - 1][0]
        # solution status indicator: 0 = nothing changed, 1 = changes present, 2 = no solution
        solution_status = 0
        # if there is a solution
        if solution_exists(new_solution, pointer, exercise_points):
            new_exercise = get_solution(new_solution, pointer, exercise_points, printing=False)
            old_exercise = get_solution(old_solution, pointer, exercise_points, printing=False) \
                if solution_exists(old_solution, pointer, exercise_points) else []
            # if there is a difference between the two exercises
            if new_exercise != old_exercise:
                for line in new_exercise:
                    print(line)
                solution_status = 1
        # if there is no solution i could have been deleted and therefore we ask if the task is still there
        else:
            for line in new_solution:
                print(line)
            solution_status = 1 if get_input('Is the task ' + pointer + ' in the file? [y/n]') else 2
        # handling the solution status: 1 -> new correction, 2 -> insert 0 points in feedback
        if solution_status > 0:
            points = 0
            comment = 'No solution.'
            if solution_status == 1:
                print('\n-------- feedback for the previous version ---------\n')
                get_solution(feedback, pointer, exercise_points)
                if not get_input('Is the feedback still correct? [y/n]'):
                    # if feedback is not appropriate anymore, a comment is asked for again
                    loaded, comment = load_feedback(feedbacks, pointer)
                    if loaded:
                        points, comment = comment
                    elif get_input('Is the solution correct? [y/n]'):
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
            print('INFO: no solutions by', str(name).rsplit(os.path.sep, 1)[1])
            while True:
                files = get_input('Enter solution file paths (inside the student\'s directory), separated by comma.\n'
                                  'Leave blank if no solution exists.',
                                  input_type='text', text_wrap=False)
                if files.strip() == '':
                    break
                files = list(map(lambda f: trailing_os_sep(name) + str(f).strip(), files.split(',')))
                if all(map(os.path.isfile, files)):
                    solutions_files.extend(files)
                    break
                else:
                    print('INFO: at least one file does not exist, try again')
            print('\n')
        tutti_solutions[name] = solutions_files
    return tutti_solutions


def create_feedback(file_path: str, ass_number: str, exercise_points):
    """Goes through all names in the directory (except ***REMOVED***) and fills in a generated feedback file"""

    empty_feedback = generate_feedback_file(ass_number, exercise_points)
    feedback_path = f'{trailing_os_sep(file_path, True)}feedback{os.path.sep}assignment{ass_number}.txt'
    with open(feedback_path, mode='w', errors='replace') as file:
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


def is_ignored_file(file_path: str) -> bool:
    """Checks whether the file is on the list of ignored files (file_ignore.txt)"""

    file_name = file_path.split(os.path.sep)[-1]
    with open(f'{os.getcwd().rsplit(os.path.sep, 1)[0]}{os.path.sep}file_ignore.txt',
              mode='r', errors='replace') as f:
        reg_ignore = [x.strip() for x in f.readlines()]
    for ig in reg_ignore:
        if re.match(ig, file_name):
            return True
    return False
