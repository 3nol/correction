import os
import sys
from itertools import dropwhile

from assignment_handler.config import GlobalConstants as GC
from assignment_handler.feedback_handler.Correction import Correction

if __name__ == '__main__':
    try:
        ass_number = ''.join(dropwhile(lambda c: c == '0', str(sys.argv[1])))
        if len(sys.argv) > 2 and sys.argv[2] in ['-s', '--solution-only']:
            tutti_names = []
            for student in [f.path for f in os.scandir(GC.get('source_path')) if f.is_dir()]:
                for directory, _, files in os.walk(student):
                    if 'git' not in directory and 'concatenated' not in directory and 'feedback' not in directory:
                        if any(map(lambda f: ass_number in directory.split(student)[1] or ass_number in f, files)):
                            if student not in tutti_names:
                                tutti_names.append(student)
            Correction(GC.get('source_path'), ass_number.zfill(2), tutti_names=list(set(tutti_names))).setup()
        else:
            Correction(GC.get('source_path'), ass_number.zfill(2)).setup()
        exit(0)
    except KeyboardInterrupt:
        print('\nvery understandable, have a nice day! :)')
        exit(1)
