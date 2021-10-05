from Correction import Correction
from Paths import source_path
import Solution

if __name__ == '__main__':

    # init_tutti_names(['clara_biedermann', 'jannes_mueller', 'leon_wenzler'])
    # Solution.generate_all_solution_templates('01')
    Correction(source_path, '01', 'Clara Biedermann').start()
