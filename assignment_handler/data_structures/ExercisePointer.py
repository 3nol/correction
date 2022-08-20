from Config import GlobalConstants as gc


class ExercisePointer:
    """
    Data structure for managing the correction progress in the exercises.
    The pointer consists of a main- and subtask, and is represented as 'main.sub'.
    It takes the assignment number as main argument, because the point/exercise distribution can be retrieved from it.
    These four methods are implemented:
        - split() returns a tuple of main-/ subtask
        - increment() makes pointer jump up by one step, regulated by the exercise point distribution
        - decrement() bring pointer down by one step, regulated by the exercise point distribution
        - clone() copies the object, useful for manipulating the copy without affecting the orignal.
    """

    def __init__(self, ass_number: str, maintask: str = None, subtask: str = None) -> None:
        self.ass_number = ass_number
        self.exercise_points = gc.get(f'points_{ass_number}')
        self.maintask = '1' if maintask is None else maintask
        if len(self.exercise_points[0]) > 1:
            self.subtask = 'a' if subtask is None else subtask
        else:
            # subtask is empty string if none exists in this maintask
            self.subtask = '' if subtask is None else subtask

    def __str__(self) -> str:
        """String representation of an exercise pointer, tasks separated by point"""
        return str(self.maintask) + '.' + str(self.subtask)

    def __repr__(self) -> str:
        """Print representation of an exercise pointer, tasks separated by point"""
        return str(self)

    def split(self) -> tuple[str, str]:
        """Small helper function that splits an exercise pointer into task, subtask without throwing an error"""
        return self.maintask, self.subtask

    def increment(self, inplace=True) -> 'ExercisePointer':
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
                if int(maintask) <= len(self.exercise_points):
                    subtask = 'a' if len(self.exercise_points[int(maintask) - 1]) > 1 else ''
        # increment just subtask
        else:
            if inplace:
                self.subtask = chr(ord(self.subtask) + 1)
            else:
                maintask = self.maintask
                subtask = chr(ord(self.subtask) + 1)
        return ExercisePointer(self.ass_number, maintask, subtask)

    def decrement(self, inplace=True) -> 'ExercisePointer':
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
                subtask = chr(len(self.exercise_points[int(maintask) - 1]) + 96) \
                    if len(self.exercise_points[int(maintask) - 1]) != 1 else ''
        # decrement just subtask
        elif self.subtask != 'a' and self.subtask != '':
            if inplace:
                self.subtask = chr(ord(self.subtask) - 1)
            else:
                maintask = self.maintask
                subtask = chr(ord(self.subtask) - 1)
        return ExercisePointer(self.ass_number, maintask, subtask)

    def clone(self) -> 'ExercisePointer':
        """Helper method for cloning this object"""
        return ExercisePointer(self.ass_number, self.maintask, self.subtask)
