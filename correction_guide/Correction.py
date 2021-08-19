import os

from Utility import tailing_os_sep, create_feedbacks, get_exercise_points, get_solution, insert_at


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
        self.tmp_file = f'{tailing_os_sep(file_path, True)}correct_tmp.txt'
        if not os.path.isfile(self.tmp_file):
            with open(self.tmp_file, 'w') as file:
                file.write('')

    def start(self) -> None:
        """Starts the correction process by checking against the generated tmp save file,
        if it is empty, new feedbacks are generated for that assignment number,
        otherwise the current progress is read from the save and restored"""

        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        tutti_names = [f.path for f in os.scandir(self.file_path) if f.is_dir()]
        if os.stat(self.tmp_file).st_size == 0:
            # TODO checking if the correcting really should be started
            test = str(input("Do you want to start with a new correction? [y/n] \n"))
            if test == 'y':
                create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
                print('all feedback templates generated')
                last_name = tutti_names[0]
                self.pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
                self.write_save(last_name)
                print('initialized progress save')
        else:
            with open(self.tmp_file, 'r') as save:
                (last_name, self.pointer) = save.readline().split(' : ', 1)
        self.correction(tutti_names, last_name)

    def correction(self, tutti_names, last_name: str) -> None:
        """Does the sequential correction process by cycling through each task (and its subtasks)
        for each tutti. This means, first all ex. 01 are corrected, then all ex. 02, ...
        During that, the save file is continually updated to keep track"""

        while int(self.pointer.split('.', 1)[0]) <= len(self.exercise_points):
            for name in tutti_names:
                if last_name == name:
                    path = f'{tailing_os_sep(name, True)}feedback{os.path.sep}assignment{self.assignment_number}.txt'
                    if os.path.isfile(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt'):
                        temp = get_solution(f'{tailing_os_sep(name, True)}assignment{self.assignment_number}.txt',
                                            self.pointer)
                        for line in temp:
                            line = line.replace('\n', '')
                            print(line)
                    # TODO correction
                    correct = str(input('Is the solution correct? [y/n] \n'))
                    comment = str(input('Please enter some comments\n'))
                    (task, subtask) = self.pointer.split('.', 1)
                    possible_points = self.exercise_points[int(task) - 1][ord(subtask) - 96 - 1] \
                        if len(self.exercise_points[int(task) - 1]) > 1 else self.exercise_points[int(task) - 1][0]
                    if correct == 'n':
                        points = possible_points + 1
                        while int(points) > possible_points:
                            points = int(input('How many points should ' + name + ' get for this exercise?\n'
                                               + str(possible_points) + ' are possible!\n'))
                    else:
                        points = possible_points
                    insert_at(path, self.pointer, str(points), comment)
                    last_name = tutti_names[(tutti_names.index(last_name) + 1) % len(tutti_names)]
                    self.write_save(last_name)
                    # insert_at(feedback_path, '3.a', '1', 'Gut gemacht, du Esel!')
                    # TODO circle through subtasks before going to next person
            self.increment_pointer()
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
