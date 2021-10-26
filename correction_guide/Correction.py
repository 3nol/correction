from Solution import create_empty_solution
from Utility import *


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
        self.pointer = ''
        # getting points distribution from config file 'assignment_config.txt'
        self.exercise_points = get_exercise_points(self.assignment_number)
        # flat-mapping all names of tutorial attendants
        self.tutti_names = [f.path for f in os.scandir(self.file_path) if f.is_dir()]
        # laying out path to temporary progress save in 'correct_tmp.txt'
        self.tmp_file = f'{tailing_os_sep(file_path, True)}correct_tmp.txt'
        if not os.path.isfile(self.tmp_file):
            with open(self.tmp_file, 'w') as file:
                file.write('')  # if file not exists, create a new one -> NEW correction

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
                # create templates for feedbacks in every attendant's directory
                create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
                print('all feedback templates generated')
                last_name = self.tutti_names[0]
                self.pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
                # writing progress to tmp file
                self.write_save(last_name)
                print('initialized progress save')
            else:
                print('no correct_tmp.txt was found!')
                exit(1)
        else:
            # otherwise, restart correction from last session based on 'correct_tmp.txt'
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
                        path = f'{tailing_os_sep(name, True)}feedback{os.path.sep}assignment{self.assignment_number}.txt'
                        # checking if there is a solution -> later checking if there is
                        # a difference to the empty solution sheet
                        if self.solution_exists(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt'):
                            get_solution(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt',
                                         self.pointer)
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
                        insert_in_db(just_name, self.assignment_number, new_total_points)
                        # count to next task and save
                        self.increment_pointer()
                        self.write_save(last_name)
                    last_name = self.tutti_names[(self.tutti_names.index(last_name) + 1) % len(self.tutti_names)]
                    # continue as long as where not back at the first student
                    if last_name != self.tutti_names[0]:
                        self.pointer = temp_pointer
                    self.write_save(last_name)

    def increment_pointer(self):
        """Increments the progress pointer by one step, examples for ex_points [[3], [1,1], [4]]:
        1. -> 2.a  /  2.a -> 2.b  /  2.b -> 3."""

        (task, subtask) = self.pointer.split('.', 1)
        # increment main task when there were no subtasks before or all previous subtasks are done
        if subtask == '' or len(self.exercise_points[int(task) - 1]) <= ord(subtask) - 96:
            task = str(int(task) + 1)
            if int(task) <= len(self.exercise_points):
                subtask = 'a' if len(self.exercise_points[int(task) - 1]) > 1 else ''
        # increment just subtask
        else:
            subtask = chr(ord(subtask) + 1)
        self.pointer = f'{task}.{subtask}'

    def write_save(self, last_name: str):
        """Save the last_name edited as well as the progress points to the save file"""

        with open(self.tmp_file, 'w') as save:
            save.write(last_name + ' : ' + self.pointer)
        update_db()

    def solution_exists(self, filepath: str):
        """ Checking if the person made the exercise which means there is a exercise for the current pointer"""

        with open(filepath, 'r') as file:
            current_file = file.readlines()
        return get_index(current_file, self.pointer) > 0
