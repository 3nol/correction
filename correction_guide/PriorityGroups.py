from Utility import increment_pointer, trailing_os_sep, get_index
from Paths import config_path
import ast
import os


class PriorityGroups:
    def __init__(self, ass_number: str):
        self.groups = {}
        self.exercise_points = self.get_task_distribution(ass_number)
        self.pointer = ''
        i = 1
        for main_task in self.exercise_points:
            if len(main_task) == 1:
                self.groups[f'{i}.'] = []
                i += 1
            else:
                j = 'a'
                for subtask in main_task:
                    self.groups[f'{i}.{j}'] = []
                    j = chr(ord(j) + 1)

    def insert_at_pointer(self, student_name: str, exercise_pointer: str):
        if self.pointer > exercise_pointer or self.pointer == '':
            self.pointer = exercise_pointer
        self.groups[exercise_pointer].append(student_name)

    def peek_smallest(self) -> list:
        return self.groups[self.pointer]

    def move_smallest_up(self):
        values = self.peek_smallest()
        self.groups[self.pointer] = []
        # getting the pointer of the next main task
        point = self.pointer
        while point.split('.', 1) == self.pointer.split('.', 1):
            point = increment_pointer(point, self.exercise_points)
        if int(point.split('.')[0]) <= len(self.exercise_points):
            self.groups[point].extend(values)
        # incrementing the pointer to the next not empty task
        while int(self.pointer.split('.')[0]) <= len(self.exercise_points) and not self.groups[self.pointer]:
            self.pointer = increment_pointer(self.pointer, self.exercise_points)

    def get_task_distribution(self, ass_number: str):
        """Reads the task distribution of a given assignment number from the assignment config file"""

        exercise_points = []
        with open(config_path + 'assignment_config.txt', 'r') as file:
            for line in file.readlines():
                if line.strip().startswith(ass_number):
                    for exercise in line.strip().split(' : ', 1)[1].split(', '):
                        exercise_points.append(ast.literal_eval(exercise))
        return exercise_points

    def get_exercise_points(self) -> list:
        return self.exercise_points

    def get_exercise_pointer(self) -> str:
        return self.pointer

    def get_exercise_pointer_from_feedback(self, student_name: str, ass_number: str):
        pointer = '1.' if len(self.exercise_points[0]) == 1 else '1.a'
        feedback = []
        with open(f'{trailing_os_sep(student_name)}feedback{os.path.sep}assignment{ass_number}.txt',
                  'r') as f:
            feedback = f.readlines()
        while True:
            # already finished with correction of this student
            if get_index(feedback, pointer) == -1:
                return -1
            # there is no correction for this pointer in the feedback
            elif feedback[get_index(feedback, pointer) + 1] == '\n':
                return pointer
            else:
                pointer = increment_pointer(pointer, self.exercise_points)

