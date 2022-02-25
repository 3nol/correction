from assignment_handler.config import GlobalConstants as GC
from assignment_handler.utilities.Utility import increment_pointer


class PriorityGroups:
    """Specialized data structure that manages groups with priorities. In this special case, the priorities
    coincide with the exercise pointer in the form 'task.subtask' of Correction.py.
    The data structure is initialized with a priority scheme (here by ass_number)."""

    def __init__(self, ass_number: str):
        self.groups = {}
        self.exercise_points = GC.get(f'points_{ass_number}')
        self.pointer = ''
        i = 1
        # initializing all empty priority groups
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
        """Insertion method that puts an object (student_name) in a certain group"""

        # self.pointer is set to the lowest possible priority
        if self.pointer > exercise_pointer or self.pointer == '':
            self.pointer = exercise_pointer
        self.groups[exercise_pointer].append(student_name)

    def peek_smallest(self) -> list:
        # retrieves the current lowest priority group
        return self.groups[self.pointer]

    def move_up_smallest(self):
        """Transition between groups. This method elevates all entries with the lowest priority by one group,
         i.e. the previously lowest group is emptied and the 'working' pointer is increased"""

        values = self.peek_smallest()
        # clearing the group
        self.groups[self.pointer] = []
        # getting the pointer of the next main task
        point = self.pointer
        while point.split('.', 1)[0] == self.pointer.split('.', 1)[0]:
            point = increment_pointer(point, self.exercise_points)
        if int(point.split('.')[0]) <= len(self.exercise_points):
            # moving lower values into next higher group
            self.groups[point].extend(values)
        # incrementing the pointer to the next not empty task
        while int(self.pointer.split('.')[0]) <= len(self.exercise_points) and not self.groups[self.pointer]:
            self.pointer = increment_pointer(self.pointer, self.exercise_points)
