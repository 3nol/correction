from Utility import increment_pointer, get_configured_exercise_points


class PriorityGroups:
    def __init__(self, ass_number: str):
        self.groups = {}
        self.exercise_points = get_configured_exercise_points(ass_number)
        self.pointer = ''
        i = 1
        for main_task in self.exercise_points:
            if len(main_task) == 1:
                self.groups[f'{i}.'] = []
            else:
                j = 'a'
                for _ in main_task:
                    self.groups[f'{i}.{j}'] = []
                    j = chr(ord(j) + 1)
            i += 1


    def insert_at_pointer(self, student_name: str, exercise_pointer: str):
        if self.pointer > exercise_pointer or self.pointer == '':
            self.pointer = exercise_pointer
        self.groups[exercise_pointer].append(student_name)

    def peek_smallest(self) -> list:
        return self.groups[self.pointer]

    def move_up_smallest(self):
        values = self.peek_smallest()
        self.groups[self.pointer] = []
        # getting the pointer of the next main task
        point = self.pointer
        while point.split('.', 1)[0] == self.pointer.split('.', 1)[0]:
            point = increment_pointer(point, self.exercise_points)
        if int(point.split('.')[0]) <= len(self.exercise_points):
            self.groups[point].extend(values)
        # incrementing the pointer to the next not empty task
        while int(self.pointer.split('.')[0]) <= len(self.exercise_points) and not self.groups[self.pointer]:
            self.pointer = increment_pointer(self.pointer, self.exercise_points)
