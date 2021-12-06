import os
import sys

from Correction import Correction
from Paths import source_path

if __name__ == '__main__':
    try:
        ass_number = str(sys.argv[1]).rsplit('0', 1)[1]
        if len(sys.argv) > 2 and sys.argv[2] in ['-s', '--solution-only']:
            tutti_names = []
            for student in [f.path for f in os.scandir(source_path) if f.is_dir() and '***REMOVED***' not in f.path]:
                for directory, _, files in os.walk(student):
                    if 'git' not in directory and 'concatenated' not in directory and 'feedback' not in directory:
                        if any(list(map(lambda f: ass_number in directory.split(student)[1] or ass_number in f, files))):
                            if student not in tutti_names:
                                tutti_names.append(student)
            Correction(source_path, ass_number.zfill(2), tutti_names=list(set(tutti_names))).setup()
        else:
            Correction(source_path, ass_number.zfill(2)).setup()
        exit(0)
    except KeyboardInterrupt:
        print('\nVery understandable, have a nice day! :)')
        exit(1)
