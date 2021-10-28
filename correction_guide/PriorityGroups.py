from Utility import increment_pointer
from Paths import config_path
import ast


class PriorityGroups:
    def __init__(self, ass_number: str):
        self.groups = {}
        self.exercise_points = self.get_task_distribution(ass_number)
        self.pointer = ''
        i = 1
        for maintask in self.exercise_points:
            if len(maintask) == 1:
                self.groups[f'{i}.'] = []
            else:
                j = 'a'
                for subtask in maintask:
                    self.groups[f'{i}.{j}'] = []
                    j = chr(ord(j) + 1)

    def insert_at_pointer(self, student_name: str, exercise_pointer: str):
        if self.pointer > exercise_pointer or self.pointer == '':
            self.pointer = exercise_pointer
        self.groups[exercise_pointer].append(student_name)

    def peek_smallest(self) -> list:
        return self.groups[self.pointer]

    def pop_smallest(self) -> list:
        values = self.peek_smallest()
        self.groups[self.pointer] = []
        self.pointer = increment_pointer(self.pointer, self.exercise_points)
        return values

    def get_task_distribution(self, ass_number: str):
        """Reads the task distribution of a given assignment number from the assignment config file"""

        exercise_points = []
        with open(config_path + 'assignment_config.txt', 'r') as file:
            for line in file.readlines():
                if line.strip().startswith(ass_number):
                    for exercise in line.strip().split(' : ', 1)[1].split(', '):
                        exercise_points.append(ast.literal_eval(exercise))
        return exercise_points
