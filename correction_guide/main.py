from Correction import Correction, init_tutti_names
from Paths import source_path


if __name__ == '__main__':
    # init_tutti_names(['***REMOVED***', '***REMOVED***', '***REMOVED***'])
    Correction(source_path, '01').setup()
