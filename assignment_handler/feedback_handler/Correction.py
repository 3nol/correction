import os
import re

from Config import GlobalConstants as gc
from data_structures.ExercisePointer import ExercisePointer
from data_structures.FileDictionary import FileDictionary
from data_structures.PriorityGroups import PriorityGroups
from feedback_handler.DirectoryPreparation import extract_solutions, create_feedback
from utilities.DatabaseConnector import \
    is_db_available, sql_query, insert_single_student, update_total_points
from utilities.Utility import \
    trailing_sep, sum_sublist_lengths, get_input, get_index, insert_in_file, sol_exists, get_solution, load_feedback


def init_names(names: list, filepath=None) -> None:
    """Takes in a list parameter, either a list with names for which each entry is pushed to the database.
    If filepath is given and the list holds one entry, its content is used as a filepath to retrieves the names there"""

    if filepath is not None:
        with open(filepath, mode='r', errors='replace', encoding='utf-8') as f:
            names.extend([str(name).strip() for name in f.readlines()])
    # inserting only non-excluded names into database
    for name in filter(lambda x: x not in gc.get('excluded_names'), names):
        sql_query(f"INSERT INTO points_table (student_name) VALUES ('{name}')")
        print('inserted student:', name)


def init_folders() -> None:
    """Initializes both the concatenated and feedback folder for each folder whose name is present in the database"""

    dbnames = list(map(lambda x: x[0], sql_query(f"SELECT student_name FROM points_table")))
    source_path, dirnames, _ = list(os.walk(gc.get('source_path')))[0]
    for name in dirnames:
        c_path = trailing_sep(source_path) + trailing_sep(name) + gc.get('concat_folder')
        f_path = trailing_sep(source_path) + trailing_sep(name) + gc.get('feedback_folder')
        if name in dbnames and not os.path.exists(c_path) and not os.path.exists(f_path):
            os.mkdir(c_path)
            os.mkdir(f_path)
            print(f'INFO: generated folders for {name}')
        else:
            print(f'ERROR: folders could not be generated for {name}')


class Correction:
    """
    Controls the entire correction process. Keeps track of who was already corrected
    and which exercise the corrector it at.
    - Init-process: generation of template feedback files for all students
    - Correction-process: sequential go-through of exercises of all students
    """

    def __init__(self, file_path: str, assignment_number: str, student_names=None) -> None:
        """Sets all class variables, mainly the assignment number, the progress pointer and the tmp save path"""

        self.file_path: str = file_path
        self.assignment_number: str = assignment_number
        # PriorityGroups objects to manage remaining students (to be corrected)
        self.task_queue: PriorityGroups = PriorityGroups(assignment_number)
        # getting points distribution from config file 'assignment_config.txt'
        self.exercise_points: list = gc.get(f'points_{self.assignment_number}')
        # flat-mapping all names of tutorial attendants
        self.student_names: list = student_names if student_names is not None \
            else [f.path for f in os.scandir(self.file_path) if f.is_dir()]
        # tracking the status of the corrected tasks
        self.corrected_task_amount: int = 0
        # storing feedbacks that were given
        feedback_file_path: str = trailing_sep(gc.get('feedback_filepath')) + f'{self.assignment_number}_feedbacks.dict'
        # initializing feedback file
        if not os.path.isfile(feedback_file_path):
            # creating an empty file
            open(feedback_file_path, mode='w', encoding='utf-8').close()
        # setting up the FileDictionary and ensuring the correct assignment's feedbacks are selected
        self.feedbacks = FileDictionary(feedback_file_path)
        if self.feedbacks.get('.ass_number') != assignment_number:
            if get_input(f'Should feedbacks.dict be overridden? [y/n]'):
                # erasing all content from file
                open(feedback_file_path, mode='w', encoding='utf-8').close()
                self.feedbacks.insert('.ass_number', assignment_number)
            else:
                exit(1)

    def get_status(self) -> str:
        # calculates the ratio between corrected tasks and all tasks in total, then formats it as percentage
        fraction_corrected = self.corrected_task_amount / \
                             (sum_sublist_lengths(self.exercise_points) * len(self.student_names))
        return f'''{str(fraction_corrected)[2:4].ljust(2, '0')}.{str(fraction_corrected)[4:6].ljust(2, '0')}%'''

    def get_just_names(self) -> list[str]:
        # splits the student's name from the file path and returns only it
        return list(map(lambda name: str(name).rsplit(os.path.sep, 1)[1], self.student_names))

    def setup(self) -> None:
        """Starts the correction process by checking against the generated tmp save file,
        if it is empty, new feedbacks are generated for that assignment number,
        otherwise the current progress is read from the save and restored"""

        print('--- STARTING CORRECTION OF ASSIGNMENT ' + str(self.assignment_number) + ' ---')
        # extract all solution files to one file per student
        corrected_students = extract_solutions(self.assignment_number, self.student_names, self.feedbacks)
        # create templates for feedbacks in every attendant's directory who needs a correction
        start_pointer = ExercisePointer(self.assignment_number)
        for student in self.student_names:
            # if the student has a valid correction
            if student in corrected_students:
                corrected_pointer = self.__get_exercise_pointer_from_feedback(student)
                # if there is still something left so correct
                if corrected_pointer != -1:
                    self.task_queue.insert_at_pointer(student, corrected_pointer)
                    c_task, c_subtask = corrected_pointer.split()
                    self.corrected_task_amount += sum_sublist_lengths(self.exercise_points[:(int(c_task) - 1)])
                    if c_subtask != '':
                        self.corrected_task_amount += ord(c_subtask) - 97
                else:
                    self.corrected_task_amount += sum_sublist_lengths(self.exercise_points)
            # else create a new template
            else:
                create_feedback(student, self.assignment_number, self.exercise_points)
                print('new feedback templates generated for', student)
                self.task_queue.insert_at_pointer(student, start_pointer)
        if self.task_queue.pointer is not None:
            self.start_correction()
        else:
            print("There is no one left to correct!")
        print('--- CORRECTION DONE ---')
        self.__recalculate_points()
        print('--- POINT RECALCULATION DONE ---')
        if self.sync_all_feedbacks():
            print('--- DATABASE UPDATE DONE ---')

    def start_correction(self) -> None:
        """Does the sequential correction process by cycling through each task (and its subtasks)
        for each student. This means, first all ex. 01 are corrected, then all ex. 02, ...
        During that, the save file is continually updated to keep track"""

        # go through all (main) exercises X.a
        while int(self.task_queue.pointer.split()[0]) <= len(self.exercise_points):
            # go through every student in the smallest task group
            for name in self.task_queue.peek_smallest():
                # check if it actually worked and the correct student is selected
                just_name = str(name).rsplit(os.path.sep, 1)[1]
                t = self.task_queue.pointer.split()[0]
                # saving the pointer for the next person
                temp_pointer = self.task_queue.pointer.clone()
                # go through all subtasks 1.X
                while t == temp_pointer.split()[0]:
                    path = f'''{trailing_sep(name) + trailing_sep(gc.get('feedback_folder'))
                                }assignment{self.assignment_number}.txt'''
                    # checking if there is a solution -> later checking if there is
                    # a difference to the empty solution sheet
                    solution_path = f'''{trailing_sep(name) + trailing_sep(gc.get('concat_folder'))
                                         }c_assignment{self.assignment_number}.txt'''
                    with open(solution_path, mode='r', errors='replace', encoding='utf-8') as f:
                        current_file = f.readlines()
                    if sol_exists(current_file, temp_pointer):
                        get_solution(current_file, temp_pointer, self.exercise_points, printing=True)
                        points, comment = self.__correct_single_solution(temp_pointer, just_name, current_file)
                    else:
                        for line in current_file:
                            print(str(line).strip())
                        if ''.join(current_file).strip() != '' and \
                                get_input('Is the task ' + str(temp_pointer) + ' in the file? [y/n]'):
                            # start correction here
                            points, comment = self.__correct_single_solution(temp_pointer, just_name, current_file)
                        else:
                            points = 0
                            comment = 'No solution.'
                    # write task correction to feedback file and to database
                    new_total_points = insert_in_file(path, temp_pointer, str(points), comment)
                    if is_db_available():
                        insert_single_student(just_name, self.assignment_number, new_total_points)
                        update_total_points()
                    # increase corrected tasks
                    self.corrected_task_amount += 1
                    # count to next task and save
                    temp_pointer.increment()
            self.task_queue.move_up_smallest()

    def __get_exercise_pointer_from_feedback(self, student_name: str) -> ExercisePointer:
        """Detects how far feedback has been giving by analyzing the feedback file and returning a corresponding
        task pointer in the form 'task.subtask'. This is used to determine the starting point for the correction"""

        feedback_pointer = ExercisePointer(self.assignment_number)
        with open(f'''{trailing_sep(student_name) + trailing_sep(gc.get('feedback_folder'))
                       }assignment{self.assignment_number}.txt''',
                  mode='r', errors='replace', encoding='utf-8') as f:
            feedback = f.readlines()
        while True:
            index = get_index(feedback, feedback_pointer)
            # already finished with correction of this student
            if index == -1:
                return index
            # there is no correction for this feedback_pointer in the feedback
            elif feedback[index + 1] == '\n':
                return feedback_pointer
            # continue search
            feedback_pointer.increment()

    def __correct_single_solution(self, temp_pointer: ExercisePointer, just_name: str,
                                  solution_file: list) -> tuple[float, str]:
        """Correction of a single student. The student's concatenated content file is opened,
        the right task is extracted and the tutor is asked for a comment, correctness and points.
        Returns the comment and the received points"""

        print('\n-------- ' + just_name + ' @ ' + str(self.get_status()) + ' --------\n')
        loaded, comment = load_feedback(self.feedbacks, temp_pointer, solution_file)
        if loaded:
            return comment
        task, subtask = temp_pointer.split()
        # get the maximum possible points for this exercise, either from the subtask or main task
        possible_points = self.exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
            if len(self.exercise_points[int(task) - 1]) > 1 else \
            self.exercise_points[int(task) - 1][0]
        if not get_input('Is the solution correct? [y/n]'):
            while True:
                points = get_input('How many points should ' + just_name + ' get for this exercise?\n'
                                   + str(possible_points) + ' are possible!', 'numeric')
                # check validity of inputted points
                if 0.0 <= points <= possible_points:
                    break
        else:
            # solution is correct -> give max. points
            points = possible_points
        self.feedbacks.insert('', str(points).split('.0', 1)[0] + ', ' + comment.replace('\n', ' '),
                              prefix=str(temp_pointer) + '_')
        return points, comment

    def __recalculate_points(self) -> None:
        """Goes again through all generated feedback files, and sums up all given points for total points.
        Has the advantage of being able to correct points mid-correction and the script picks it up in the
        end and updates the feedback file."""

        for name in self.student_names:
            total_points = 0
            with open(f'''{trailing_sep(name) + trailing_sep(gc.get('feedback_folder'))
                           }assignment{self.assignment_number}.txt''',
                      mode='r', errors='replace', encoding='utf-8') as f:
                file = f.readlines()
            # go through every points specification, except for the total
            for i in range(3, len(file)):
                points = re.compile(r'\[\d{1,2}\.?5?/\d{1,2}\.?5?]')
                if points.findall(file[i]):
                    # add them together
                    total_points += float(str(points.findall(file[i])[0]).split('/', 1)[0][1:])
            # format it nicely
            total_points = str(total_points).split('.0', 1)[0]
            file[1] = f'[{total_points}/10]\n'
            with open(f'''{trailing_sep(name) + trailing_sep(gc.get('feedback_folder'))
                           }assignment{self.assignment_number}.txt''',
                      mode='w', errors='replace', encoding='utf-8') as f:
                f.writelines(file)
            print('INFO: wrote feedback points successfully:', str(name).rsplit(os.path.sep, 1)[1], total_points)

    def sync_all_feedbacks(self) -> bool:
        """Helper methods to synchronize all feedbacks with the database. Only works if the client has a connection"""

        if is_db_available():
            for name in self.student_names:
                with open(f'''{trailing_sep(name) + trailing_sep(gc.get('feedback_folder'))
                               }assignment{self.assignment_number}.txt''',
                          mode='r', errors='replace', encoding='utf-8') as f:
                    insert_single_student(str(name).rsplit(os.path.sep, 1)[1], self.assignment_number,
                                          str(float(f.readlines()[1][1:].split('/', 1)[0])).split('.0', 1)[0])
            update_total_points()
            return True
        else:
            print('ERROR: you have to be online to sync all feedbacks!')
            return False
