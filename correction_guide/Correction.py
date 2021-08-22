import os

from Solution import create_empty_solution
from Utility import tailing_os_sep, create_feedbacks, get_exercise_points, get_solution, insert_at, get_index


class Correction:
    """Controls the entire correction process. Keeps track of who was already corrected
    and which exercise the corrector it at.
    - Init-process: generation of template feedback files for all tuttis
    - Correction-process: sequential go-through of exercises of all tuttis
    A progress save file is written to the filepath/correct_tmp.txt"""

    def __init__(self, file_path: str, assignment_number: str, corrector: str) -> None:
        """Sets all class variables, mainly the assignment number, the progress pointer and the tmp save path"""

        self.file_path = file_path
        self.assignment_number = assignment_number
        self.corrector = corrector
        self.pointer = ''
        self.exercise_points = get_exercise_points(self.assignment_number)
        self.tutti_names = [f.path for f in os.scandir(self.file_path) if f.is_dir()]
        self.tmp_file = f'{tailing_os_sep(file_path, True)}correct_tmp.txt'
        if not os.path.isfile(self.tmp_file):
            with open(self.tmp_file, 'w') as file:
                file.write('')

    def start(self) -> None:
        """Starts the correction process by checking against the generated tmp save file,
        if it is empty, new feedbacks are generated for that assignment number,
        otherwise the current progress is read from the save and restored"""

        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        if os.stat(self.tmp_file).st_size == 0:
            verify = str(input(f"Do you want to start with a new correction of {self.assignment_number}? [y/n] \n"))
            if verify == 'y':
                create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
                print('all feedback templates generated')
                last_name = self.tutti_names[0]
                self.pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
                self.write_save(last_name)
                print('initialized progress save')
            else:
                print('no correct_tmp.txt was found!')
                exit(1)
        else:
            with open(self.tmp_file, 'r') as save:
                (last_name, self.pointer) = save.readline().split(' : ', 1)
        self.correction(last_name)

    def correction(self, last_name: str) -> None:
        """Does the sequential correction process by cycling through each task (and its subtasks)
        for each tutti. This means, first all ex. 01 are corrected, then all ex. 02, ...
        During that, the save file is continually updated to keep track"""

        while int(self.pointer.split('.', 1)[0]) <= len(self.exercise_points):

            # TODO: update every given point in database
            # TODO: update total points in exercise (maybe use DB to get?)

            for name in self.tutti_names:
                if last_name == name:
                    just_name = str(name).rsplit(os.path.sep, 1)[1]
                    print('\n-------- ' + just_name + ' --------\n')
                    t = self.pointer.split('.', 1)[0]
                    # saving the pointer for the next person
                    temp_pointer = self.pointer
                    while t == self.pointer.split('.', 1)[0]:
                        path = f'{tailing_os_sep(name, True)}feedback{os.path.sep}assignment{self.assignment_number}.txt'
                        # checking if there is a solution -> later checking if there is
                        # a difference to the empty solution sheet
                        if self.solution_exists(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt'):
                            get_solution(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt',
                                         self.pointer)
                            comment = str(input('Please enter some comments\n'))
                            (task, subtask) = self.pointer.split('.', 1)
                            possible_points = self.exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
                                if len(self.exercise_points[int(task) - 1]) > 1 else \
                                self.exercise_points[int(task) - 1][0]
                            if str(input('Is the solution correct? [y/n] \n')) == 'n':
                                while True:
                                    points = float(
                                        input('How many points should ' + just_name + ' get for this exercise?\n'
                                              + str(possible_points) + ' are possible!\n'))
                                    if 0.0 <= points <= possible_points:
                                        break
                            else:
                                points = possible_points
                        else:
                            points = 0
                            comment = 'no solution'
                        insert_at(path, self.pointer, str(points), comment)
                        self.increment_pointer()
                        self.write_save(last_name)
                    last_name = self.tutti_names[(self.tutti_names.index(last_name) + 1) % len(self.tutti_names)]
                    if last_name != self.tutti_names[0]:
                        self.pointer = temp_pointer
                    self.write_save(last_name)

    def increment_pointer(self) -> None:
        """Increments the progress pointer by one step, examples for ex_points [[3], [1,1], [4]]:
        1. -> 2.a  /  2.a -> 2.b  /  2.b -> 3."""

        (task, subtask) = self.pointer.split('.', 1)
        if subtask == '' or len(self.exercise_points[int(task) - 1]) <= ord(subtask) - 96:
            task = str(int(task) + 1)
            if int(task) <= len(self.exercise_points):
                subtask = 'a' if len(self.exercise_points[int(task) - 1]) > 1 else ''
        else:
            subtask = chr(ord(subtask) + 1)
        self.pointer = f'{task}.{subtask}'

    def write_save(self, last_name: str) -> None:
        """Save the last_name edited as well as the progress points to the save file"""

        with open(self.tmp_file, 'w') as save:
            save.write(last_name + ' : ' + self.pointer)
        # TODO update total points in database

    def solution_exists(self, filepath: str):
        """ Checking if the person made the exercise which means there is a different to the empty
        solution from the beginning. Checking every task on it's own to minimize the correcting"""

        with open(filepath, 'r') as file:
            current_file = file.readlines()
        names = filepath.split(os.path.sep)
        empty_solution = create_empty_solution(names[len(names) - 2], self.assignment_number)
        index1 = get_index(current_file, self.pointer)
        index2 = get_index(empty_solution, self.pointer)
        safe1 = index1
        while index1 >= 0 and current_file[index1 - 1].startswith('#'):
            index1 -= 1
        while index2 >= 0 and empty_solution[index2 - 1].startswith('#'):
            index2 -= 1
        while index1 < len(current_file) and (index1 <= safe1 or not current_file[index1].startswith('#')):
            if current_file[index1] != empty_solution[index2]:
                return True
            else:
                index1 += 1
                index2 += 1
        return False
