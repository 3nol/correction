from DirectoryPreparation import extract_solutions, create_feedbacks
from Utility import *
from PriorityGroups import PriorityGroups


def init_tutti_names(names: list):
    for name in names:
        sql_query(f"INSERT INTO points_table (student_name) VALUES ('{name}')")
        print('inserted tutti:', name)


class Correction:
    """Controls the entire correction process. Keeps track of who was already corrected
    and which exercise the corrector it at.
    - Init-process: generation of template feedback files for all tuttis
    - Correction-process: sequential go-through of exercises of all tuttis
    A progress save file is written to the filepath/correct_tmp.txt"""

    def __init__(self, file_path: str, assignment_number: str, corrector: str):
        """Sets all class variables, mainly the assignment number, the progress pointer and the tmp save path"""

        self.file_path = file_path
        self.assignment_number = assignment_number
        self.corrector = corrector
        self.offline = not check_internet_connection()
        self.task_queue = PriorityGroups(assignment_number)
        # self.pointer = ''
        # getting points distribution from config file 'assignment_config.txt'
        self.exercise_points = get_configured_exercise_points(self.assignment_number)
        # flat-mapping all names of tutorial attendants
        self.tutti_names = [f.path for f in os.scandir(self.file_path) if f.is_dir() and '***REMOVED***' not in f.path]
        # laying out path to temporary progress save in 'correct_tmp.txt'
        # self.tmp_file = f'{trailing_os_sep(file_path, True)}correct_tmp.txt'
        # if not os.path.isfile(self.tmp_file):
        #    with open(self.tmp_file, 'w') as file:
        #        file.write('')  # if file not exists, create a new one -> NEW correction

    def get_just_names(self):
        return list(map(lambda name: str(name).rsplit(os.path.sep, 1)[1], self.tutti_names))

    def setup(self):
        """Starts the correction process by checking against the generated tmp save file,
        if it is empty, new feedbacks are generated for that assignment number,
        otherwise the current progress is read from the save and restored"""

        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        if os.stat(self.tmp_file).st_size == 0:
            # 'correct_tmp.txt' is empty -> asking whether a new correction should be initialized
            verify = str(input(f"Do you want to start with a new correction of {self.assignment_number}? [y/n] \n"))
            if verify == 'y':
                # extract all solution files to one file per student
                corrected_students = extract_solutions(self.assignment_number, self.tutti_names)
                # create templates for feedbacks in every attendant's directory
                pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
                for student in self.tutti_names:
                    # if the student has a valid correction
                    if student in corrected_students:
                        corrected_pointer = self.task_queue.get_exercise_pointer_from_feedback(student,
                                                                                               self.assignment_number)
                        # if there is still something left so correct
                        if corrected_pointer != -1:
                            self.task_queue.insert_at_pointer(student, corrected_pointer)
                    # else create a new template
                    else:
                        create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
                        print('new feedback templates generated for' + student)
                        self.task_queue.insert_at_pointer(student, pointer)
                # last_name = self.tutti_names[0]
                # self.pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
                # writing progress to tmp file
                # self.write_save(last_name)
                print('initialized progress save')
            else:
                print('no correct_tmp.txt was found!')
                exit(1)
        else:
            # otherwise, sync previous progress if internet is available
            if not self.offline:
                self.sync_all_feedbacks()
            # then, restart correction from last session based on 'correct_tmp.txt'
            with open(self.tmp_file, 'r') as save:
                (last_name, self.pointer) = save.readline().split(' : ', 1)
        self.start_correction(last_name)

    def start_correction(self, last_name: str):
        """Does the sequential correction process by cycling through each task (and its subtasks)
        for each tutti. This means, first all ex. 01 are corrected, then all ex. 02, ...
        During that, the save file is continually updated to keep track"""

        # go through all (main) exercises X.a
        while int(self.pointer.split('.', 1)[0]) <= len(self.exercise_points):
            # go through every student
            for name in self.tutti_names:
                # check if it actually worked and the correct student is selected
                if last_name == name:
                    just_name = str(name).rsplit(os.path.sep, 1)[1]
                    print('\n-------- ' + just_name + ' --------\n')
                    t = self.pointer.split('.', 1)[0]
                    # saving the pointer for the next person
                    temp_pointer = self.pointer
                    # go through all subtasks 1.X
                    while t == self.pointer.split('.', 1)[0]:
                        path = f'{trailing_os_sep(name, True)}feedback{os.path.sep}assignment{self.assignment_number}.txt'
                        # checking if there is a solution -> later checking if there is
                        # a difference to the empty solution sheet
                        solution_path = f'{trailing_os_sep(name, True)}concatenated{os.path.sep}concatenated_assignment{self.assignment_number}.txt'
                        if self.solution_exists(solution_path):
                            get_solution(solution_path, self.pointer, self.exercise_points)
                            comment = str(input('Please enter some comments (without newlines!)\n'))
                            (task, subtask) = self.pointer.split('.', 1)
                            # get the maximum possible points for this exercise, either from the subtask or main task
                            possible_points = self.exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
                                if len(self.exercise_points[int(task) - 1]) > 1 else \
                                self.exercise_points[int(task) - 1][0]
                            if str(input('Is the solution correct? [y/n] \n')) == 'n':
                                while True:
                                    points = float(
                                        input('How many points should ' + just_name + ' get for this exercise?\n'
                                              + str(possible_points) + ' are possible!\n'))
                                    # check validity of inputted points
                                    if 0.0 <= points <= possible_points:
                                        break
                            else:
                                # solution is correct -> give max. points
                                points = possible_points
                        else:
                            # solution does not exists -> 0 points
                            points = 0
                            comment = 'no solution'
                        # write task correction to feedback file and to database
                        new_total_points = insert_in_file(path, self.pointer, str(points), comment)
                        if not self.offline:
                            insert_in_db(just_name, self.assignment_number, new_total_points)
                        # count to next task and save
                        self.pointer = increment_pointer(self.pointer, self.exercise_points)
                        self.write_save(last_name)
                    last_name = self.tutti_names[(self.tutti_names.index(last_name) + 1) % len(self.tutti_names)]
                    # continue as long as where not back at the first student
                    if last_name != self.tutti_names[0]:
                        self.pointer = temp_pointer
                    self.write_save(last_name)

    def write_save(self, last_name: str):
        """Save the last_name edited as well as the progress points to the save file"""

        with open(self.tmp_file, 'w') as save:
            save.write(last_name + ' : ' + self.pointer)
        if not self.offline:
            update_db()

    def solution_exists(self, filepath: str):
        """ Checking if the person made the exercise which means there is a exercise for the current pointer"""

        with open(filepath, 'r') as file:
            current_file = file.readlines()
        return get_index(current_file, self.pointer) > 0

    def sync_all_feedbacks(self):
        if not self.offline:
            for name in self.tutti_names:
                with open(f'{trailing_os_sep(name)}feedback{os.path.sep}assignment{self.assignment_number}.txt') as f:
                    insert_in_db(str(name).rsplit(os.path.sep, 1)[1], self.assignment_number,
                                 str(float(f.readlines()[1][1:].split('/', 1)[0])).split('.0', 1)[0])
            update_db()
        else:
            print('ERROR: you have to be online to sync all feedbacks!')
