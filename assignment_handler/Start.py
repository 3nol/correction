import os
import sys
from itertools import dropwhile

from assignment_handler.Config import GlobalConstants as gc
from assignment_handler.feedback_handler.Correction import Correction


def collect_solution_only_students():
    tutti_names = set()
    for student in [f.path for f in os.scandir(gc.get('source_path')) if f.is_dir()]:
        for directory, _, files in os.walk(student):
            # don't search in ignored folders, then collect students who have done the assignment
            if not any([d for d in [gc.get('concat_folder'), gc.get('feedback_folder')] + gc.get('excluded_folders')
                        if d in directory]) and \
                   any(map(lambda f: ass_number in directory.split(student)[1] or ass_number in f, files)):
                tutti_names.add(student)
    return list(tutti_names)


if __name__ == '__main__':
    try:
        students = None
        ass_number = ''.join(dropwhile(lambda c: c == '0', str(sys.argv[1])))
        if len(sys.argv) > 2 and sys.argv[2] in ['-s', '--solution-only']:
            students = collect_solution_only_students()
        Correction(gc.get('source_path'), ass_number.zfill(2), student_names=students).setup()
        exit(0)
    except KeyboardInterrupt:
        print('\nvery understandable, have a nice day! :)')
        exit(1)
