from assignment_handler.Config import GlobalConstants as gc
from assignment_handler.data_structures.ExercisePointer import ExercisePointer


class PriorityGroups:
    """
    Specialized data structure that manages groups with priorities. In this special case, the priorities
    coincide with the exercise pointer in the form 'task.subtask' of Correction.py.
    The data structure is initialized with a priority scheme (here by ass_number).
    """

    def __init__(self, ass_number: str) -> None:
        self.groups = {}
        self.ass_number = ass_number
        self.exercise_points = gc.get(f'points_{ass_number}')
        self.pointer: ExercisePointer = None
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

    def insert_at_pointer(self, student_name: str, exercise_pointer: ExercisePointer) -> None:
        """Insertion method that puts an object (student_name) in a certain group"""

        # self.pointer is set to the lowest possible priority
        if self.pointer is None or self.pointer.split()[0] > exercise_pointer.split()[0]:
            self.pointer = exercise_pointer.clone()
        self.groups[str(exercise_pointer)].append(student_name)

    def peek_smallest(self) -> list:
        """Retrieves the current lowest priority group"""
        return self.groups[str(self.pointer)]

    def move_up_smallest(self) -> None:
        """Transition between groups. This method elevates all entries with the lowest priority by one group,
         i.e. the previously lowest group is emptied and the 'working' pointer is increased"""

        values = self.peek_smallest()
        # clearing the group
        self.groups[str(self.pointer)] = []
        # getting the pointer of the next main task
        run_pointer = self.pointer.clone()
        while run_pointer.split()[0] == self.pointer.split()[0]:
            run_pointer.increment()
        if int(run_pointer.split()[0]) <= len(self.exercise_points):
            # moving lower values into next higher group
            self.groups[str(run_pointer)].extend(values)
        # incrementing the pointer to the next not empty task
        while int(self.pointer.split()[0]) <= len(self.exercise_points) and not self.groups[str(self.pointer)]:
            self.pointer.increment()
