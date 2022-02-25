from assignment_handler.Config import GlobalConstants as gc


class ExercisePointer:
    def __init__(self, ass_number: str, maintask: str = '', subtask: str = ''):
        self.ass_number = ass_number
        self.exercise_points = gc.get(f'points_{ass_number}')
        self.maintask = '1' if maintask == '' else maintask
        self.subtask = 'a' if subtask == '' and len(self.exercise_points[0]) > 1 else subtask

    def __str__(self):
        """String representation of an exercise pointer, tasks separated by point"""
        return str(self.maintask) + '.' + str(self.subtask)

    def __repr__(self):
        """Print representation of an exercise pointer, tasks separated by point"""
        return str(self)

    def split(self):
        """Small helper function that splits an exercise pointer into task, subtask without throwing an error"""
        return self.maintask, self.subtask

    def increment(self, inplace=True):
        """Increments the progress pointer by one step, examples for ex_points [[3], [1,1], [4]]:
        1. -> 2.a  /  2.a -> 2.b  /  2.b -> 3."""
        maintask = subtask = ''
        # increment main task when there were no subtasks before or all previous subtasks are done
        if self.subtask == '' or len(self.exercise_points[int(self.maintask) - 1]) <= ord(self.subtask) - 96:
            if inplace:
                self.maintask = str(int(self.maintask) + 1)
                if int(self.maintask) <= len(self.exercise_points):
                    self.subtask = 'a' if len(self.exercise_points[int(self.maintask) - 1]) > 1 else ''
            else:
                maintask = str(int(self.maintask) + 1)
                if int(self.maintask) <= len(self.exercise_points):
                    subtask = 'a' if len(self.exercise_points[int(self.maintask) - 1]) > 1 else ''
        # increment just subtask
        else:
            if inplace:
                self.subtask = chr(ord(self.subtask) + 1)
            else:
                subtask = chr(ord(self.subtask) + 1)
        return ExercisePointer(self.ass_number, maintask, subtask)

    def decrement(self, inplace=True):
        """Decrements the progress pointer by one step, examples for ex_points [[3], [1,1], [4]]:
        1. -> 1.  /  2.b -> 2.a  /  3. -> 2.b"""
        maintask = subtask = ''
        # decrement the main task if the subtask is 'a' or ''
        if (self.subtask == 'a' or self.subtask == '') and self.maintask != '1':
            if inplace:
                self.maintask = str(int(self.maintask) - 1)
                self.subtask = chr(len(self.exercise_points[int(self.maintask) - 1]) + 96) \
                    if len(self.exercise_points[int(self.maintask) - 1]) != 1 else ''
            else:
                maintask = str(int(self.maintask) - 1)
                subtask = chr(len(self.exercise_points[int(self.maintask) - 1]) + 96) \
                    if len(self.exercise_points[int(self.maintask) - 1]) != 1 else ''
        # decrement just subtask
        elif self.subtask != 'a' and self.subtask != '':
            if inplace:
                self.subtask = chr(ord(self.subtask) - 1)
            else:
                subtask = chr(ord(self.subtask) - 1)
        return ExercisePointer(self.ass_number, maintask, subtask)

    def clone(self):
        """Helper method for cloning this object"""
        return ExercisePointer(self.ass_number, self.maintask, self.subtask)