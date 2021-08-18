import os

from Utility import tailing_os_sep, create_feedbacks, get_exercise_points


class Correction:
    def __init__(self, file_path: str, assignment_number: str, corrector: str):
        self.file_path = file_path
        self.assignment_number = assignment_number
        self.corrector = corrector
        self.pointer = ''
        self.exercise_points = get_exercise_points(self.assignment_number)
        self.tmp_file = tailing_os_sep(file_path, True) + 'correct_tmp.txt'
        if not os.path.isfile(self.tmp_file):
            with open(self.tmp_file, 'w') as file:
                file.write('')

    def start(self):
        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        tutti_names = [f.path for f in os.scandir(self.file_path) if f.is_dir()]
        if os.stat(self.tmp_file).st_size == 0:
            create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
            print('all feedback templates generated')
            self.pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
            with open(self.tmp_file, 'w') as file:
                last_name = tutti_names[0]
                file.write(last_name + '\n' + self.pointer)
                print('initialized progress save')
        else:
            with open(self.tmp_file, 'r') as save:
                last_name = save.readlines()[0]
                self.pointer = save.readlines()[1]
        self.correction(tutti_names, last_name)

    def correction(self, tutti_names: list[str], last_name: str):
        while int(self.pointer.split('.', 1)[0]) <= len(self.exercise_points):
            for name in tutti_names:
                if last_name == name:
                    feedback_path = tailing_os_sep(name, True) + 'feedback/assignment' + self.assignment_number + '.txt'
                    # TODO correction
                    last_name = tutti_names[tutti_names.index(last_name) + 1]
                    self.write_save(last_name)
                    # insert_at(feedback_path, '3.a', '1', 'Gut gemacht, du Esel!')
            self.increment_pointer()
            self.write_save(last_name)

    def increment_pointer(self):
        (task, subtask) = self.pointer.split('.', 1)
        if subtask == '' or len(self.exercise_points[int(task) - 1]) <= ord(subtask) - 96:
            task = str(int(task) + 1)
            subtask = 'a' if len(self.exercise_points[int(task) - 1]) > 1 else ''
        else:
            subtask = chr(ord(subtask) + 1)
        self.pointer = task + '.' + subtask

    def write_save(self, last_name: str):
        with open(self.tmp_file, 'w') as save:
            save.write(last_name + '\n' + self.pointer)
