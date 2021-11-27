import sys
from Correction import Correction
from Paths import source_path


if __name__ == '__main__':
    Correction(source_path, '04').setup()
    # Correction(source_path, sys.argv[1].zfill(2)).setup()
