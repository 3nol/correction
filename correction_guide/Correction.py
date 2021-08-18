import os

from Utility import tailing_os_sep, create_feedbacks, get_exercise_points


class Correction:
    def __init__(self, file_path: str, assignment_number: str, corrector: str):
        self.file_path = file_path
        self.assignment_number = assignment_number
        self.corrector = corrector
        self.exercise_points = get_exercise_points(self.assignment_number)
        self.tmp_file = tailing_os_sep(file_path, True) + 'correct_tmp.txt'
        if not os.path.isfile(self.tmp_file):
            with open(self.tmp_file, 'w') as file:
                file.write('')

    def start(self):
        print('-- starting correction of assignment ' + str(self.assignment_number) + ' --')
        if os.stat(self.tmp_file).st_size == 0:
            create_feedbacks(self.file_path, self.assignment_number, self.corrector, self.exercise_points)
            print('all feedback templates generated')
        with open(self.tmp_file, 'w') as file:
            file.write(self.file_path + '\n\n')
            print('initialized progress save')
        for name in [f.path for f in os.scandir(self.file_path) if f.is_dir()]:
            feedback_path = tailing_os_sep(name, True) + 'feedback/assignment' + self.assignment_number + '.txt'
            if os.path.isfile(feedback_path):
                assert True
                # insert_at(feedback_path, '3.a', '1', 'Gut gemacht, du Esel!')
