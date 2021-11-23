from Utility import *
from PriorityGroups import PriorityGroups
from DirectoryPreparation import extract_solutions, create_feedback


def init_tutti_names(names: list, filepath=False):
    """Takes in a list parameter, either a list with names for which each entry is pushed to the database.
    If filepath=True and the list holds one entry, its content is used as a filepath to retrieves the names there"""

    if filepath:
        with open(names[0], mode='r', errors='replace') as f:
            names = list(filter(lambda x: x not in ['***REMOVED***', '***REMOVED***', '***REMOVED***'],
                            map(lambda x: str(x).strip(), f.readlines())))
    for name in names:
        sql_query(f"INSERT INTO points_table (student_name) VALUES ('{name}')")
        print('inserted tutti:', name)


class Correction:
    """Controls the entire correction process. Keeps track of who was already corrected
    and which exercise the corrector it at.
    - Init-process: generation of template feedback files for all tuttis
    - Correction-process: sequential go-through of exercises of all tuttis
    A progress save file is written to the filepath/correct_tmp.txt"""

    def __init__(self, file_path: str, assignment_number: str):
        """Sets all class variables, mainly the assignment number, the progress pointer and the tmp save path"""

        self.file_path: str = file_path
        self.assignment_number: str = assignment_number
        self.offline: bool = not check_internet_connection()
        # PriorityGroups objects to manage remaining students (to be corrected)
        self.task_queue: PriorityGroups = PriorityGroups(assignment_number)
        # getting points distribution from config file 'assignment_config.txt'
        self.exercise_points: list = get_configured_exercise_points(self.assignment_number)
        # flat-mapping all names of tutorial attendants
        self.tutti_names: list = [f.path for f in os.scandir(self.file_path) if f.is_dir() and '***REMOVED***' not in f.path]
        # tracking the status of the corrected tasks
        self.corrected_task_amount: int = 0

    def get_status(self) -> str:
        # calculates the ratio between corrected tasks and all tasks in total, then formats it as percentage
        fraction_corrected = self.corrected_task_amount / (count_sublists(self.exercise_points) * len(self.tutti_names))
        return f'''{str(fraction_corrected)[2:4].ljust(2, '0')}.{str(fraction_corrected)[4:6].ljust(2, '0')}%'''

    def get_just_names(self) -> list:
        # splits the student's name from the file path and returns only it
        return list(map(lambda name: str(name).rsplit(os.path.sep, 1)[1], self.tutti_names))

    def setup(self):
        """Starts the correction process by checking against the generated tmp save file,
        if it is empty, new feedbacks are generated for that assignment number,
        otherwise the current progress is read from the save and restored"""

        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        # extract all solution files to one file per student
        corrected_students = extract_solutions(self.assignment_number, self.tutti_names)
        # create templates for feedbacks in every attendant's directory who needs a correction
        start_pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
        for student in self.tutti_names:
            # if the student has a valid correction
            if student in corrected_students:
                corrected_pointer = self.__get_exercise_pointer_from_feedback(student)
                # if there is still something left so correct
                if corrected_pointer != -1:
                    self.task_queue.insert_at_pointer(student, corrected_pointer)
                    c_task, c_subtask = corrected_pointer.split('.', 1)
                    self.corrected_task_amount += count_sublists(self.exercise_points[:(int(c_task) - 1)])
                    if c_subtask != '':
                        self.corrected_task_amount += ord(c_subtask) - 97
                else:
                    self.corrected_task_amount += count_sublists(self.exercise_points)
            # else create a new template
            else:
                create_feedback(student, self.assignment_number, self.exercise_points)
                print('new feedback templates generated for' + student)
                self.task_queue.insert_at_pointer(student, start_pointer)
        if self.task_queue.pointer != '':
            if not self.offline:
                self.sync_all_feedbacks()
            self.start_correction()
        else:
            print("There is no one left to correct!")

    def start_correction(self):
        """Does the sequential correction process by cycling through each task (and its subtasks)
        for each tutti. This means, first all ex. 01 are corrected, then all ex. 02, ...
        During that, the save file is continually updated to keep track"""

        # go through all (main) exercises X.a
        while int(self.task_queue.pointer.split('.', 1)[0]) <= len(self.exercise_points):
            # go through every student in the smallest task group
            for name in self.task_queue.peek_smallest():
                # check if it actually worked and the correct student is selected
                just_name = str(name).rsplit(os.path.sep, 1)[1]
                print('\n-------- ' + just_name + ' @ ' + str(self.get_status()) + ' --------\n')
                t = self.task_queue.pointer.split('.', 1)[0]
                # saving the pointer for the next person
                temp_pointer = self.task_queue.pointer
                # go through all subtasks 1.X
                while t == temp_pointer.split('.', 1)[0]:
                    path = f'{trailing_os_sep(name, True)}feedback{os.path.sep}assignment{self.assignment_number}.txt'
                    # checking if there is a solution -> later checking if there is
                    # a difference to the empty solution sheet
                    solution_path = f'{trailing_os_sep(name, True)}concatenated{os.path.sep}concatenated_assignment' \
                                    f'{self.assignment_number}.txt'
                    with open(solution_path, mode='r', errors='replace') as f:
                        current_file = f.readlines()
                    if solution_exists(current_file, temp_pointer, self.exercise_points):
                        get_solution(current_file, temp_pointer, self.exercise_points)
                        comment, points = self.__correct_single_solution(temp_pointer, just_name)
                    else:
                        for line in current_file:
                            print(line.strip())
                        if get_input('Is the task ' + temp_pointer + ' in the file? [y/n]'):
                            # start correction here
                            comment, points = self.__correct_single_solution(temp_pointer, just_name)
                        else:
                            points = 0
                            comment = 'no solution'
                    # write task correction to feedback file and to database
                    new_total_points = insert_in_file(path, temp_pointer, str(points), comment)
                    if not self.offline:
                        insert_in_db(just_name, self.assignment_number, new_total_points)
                        update_db()
                    # increase corrected tasks
                    self.corrected_task_amount += 1
                    # count to next task and save
                    temp_pointer = increment_pointer(temp_pointer, self.exercise_points)
            self.task_queue.move_up_smallest()

    def __get_exercise_pointer_from_feedback(self, student_name: str):
        """Detects how far feedback has been giving by analyzing the feedback file and returning a corresponding
        task pointer in the form 'task.subtask'. This is used to determine the starting point for the correction"""

        feedback_pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
        with open(f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{self.assignment_number}.txt',
                  mode='r', errors='replace') as f:
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
            feedback_pointer = increment_pointer(feedback_pointer, self.exercise_points)

    def __correct_single_solution(self, temp_pointer: str, just_name: str) -> (str, str):
        """Correction of a single student. The student's concatenated content file is opened,
        the right task is extracted and the tutor is asked for a comment, correctness and points.
        Returns the comment and the received points"""

        comment = get_input('Please enter some comments (without newlines!)', 'text')
        (task, subtask) = temp_pointer.split('.', 1)
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
        return comment, points

    def sync_all_feedbacks(self):
        """Helper methods to synchronize all feedbacks with the database. Only works if the client has a connection"""

        if not self.offline:
            for name in self.tutti_names:
                with open(f'{trailing_os_sep(name)}feedback{os.path.sep}assignment{self.assignment_number}.txt',
                          mode='r', errors='replace') as f:
                    insert_in_db(str(name).rsplit(os.path.sep, 1)[1], self.assignment_number,
                                 str(float(f.readlines()[1][1:].split('/', 1)[0])).split('.0', 1)[0])
            update_db()
        else:
            print('ERROR: you have to be online to sync all feedbacks!')
