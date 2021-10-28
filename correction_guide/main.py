from Correction import Correction, init_tutti_names
from Paths import source_path


if __name__ == '__main__':
    # init_tutti_names(['clara.biedermann', 'jannes.mueller', 'leon.wenzler'])
    Correction(source_path, '01', 'Clara Biedermann').setup()
