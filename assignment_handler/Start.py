import os
import sys
from itertools import dropwhile

from assignment_handler.Config import GlobalConstants as gc
from assignment_handler.feedback_handler.Correction import init_names, init_folders, Correction


def collect_solution_only_students(ass_number: str) -> list[str]:
    """Collects only students who handed in something for the given assignment"""
    student_names = set()
    for student in [f.path for f in os.scandir(gc.get('source_path')) if f.is_dir()]:
        for directory, _, files in os.walk(student):
            # don't search in ignored folders, then collect students who have done the assignment
            if not any([d for d in [gc.get('concat_folder'), gc.get('feedback_folder')] + gc.get('excluded_folders')
                        if d in directory]) and \
                   any(map(lambda f: ass_number in directory.split(student)[1] or ass_number in f, files)):
                # this students has a file or folder with the ass_number present somewhere
                student_names.add(student)
    return list(student_names)


def handle_cli_args(args: list) -> None:
    """Handles the commandline arguments which are:
        - 1. ass_number (maybe be single digit, will be padded with zeros)
        - 2. optional flag for solutions only: -s or --solution-only (see method above)"""
    try:
        students = None
        # parse ass_number neatly
        ass_number = ''.join(dropwhile(lambda c: c == '0', str(args[1])))
        if len(args) > 2 and args[2] in ['-s', '--solution-only']:
            # solution only flag is present
            students = collect_solution_only_students(ass_number)
        # start the correction by using the source path and the collected students
        Correction(gc.get('source_path'), ass_number.zfill(2), student_names=students).setup()
        exit(0)
    except KeyboardInterrupt:
        print('\nvery understandable, have a nice day! :)')
        exit(1)


if __name__ == '__main__':
    # inserts all given names into the database
    # init_names([name1, name2, name3, ...])

    # creates the needed concat- and feedback-folders for each student, checks against db
    # init_folders()

    # starts the correction programs, handles commandline arguments
    handle_cli_args(sys.argv)
