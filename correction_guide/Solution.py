import os
from Utility import get_exercise_points, tailing_os_sep
from Private import source_path

# to generate empty solutions for every student


def create_empty_solution(student: str, number: str):
    """ creating a list of lines containing an empty template for the solution of a given
    assigment number by using the assignment_config.txt"""

    exercise_points = get_exercise_points(number)
    lines = ['# Assignment ' + number + '\n', '# ' + student + '\n', '#\n']
    task_counter = 1
    for exercise in exercise_points:
        lines.append('#\n')
        lines.append('#\n')
        if len(exercise) > 1:
            lines.append('# Task ' + str(task_counter) + ':\n')
            subtask_counter = 'a'
            for subtask in exercise:
                lines.append('#\n')
                lines.append('# ' + subtask_counter + ')\n')
                lines.append('\n')
                subtask_counter = chr(ord(subtask_counter) + 1)
        else:
            lines.append('# Task ' + str(task_counter) + ':\n')
        lines.append('\n')
        task_counter += 1
    return lines


if __name__ == '__main__':
    ass_number = '01'
    ending = '.txt'
    tutti_names = [f.path for f in os.scandir(source_path) if f.is_dir()]
    for name in tutti_names:
        if '***REMOVED***' not in name:
            just_name = str(name).split(os.path.sep)
            empty_solution_file = create_empty_solution(just_name[len(just_name) - 1], ass_number)
            solution_path = f'{tailing_os_sep(name, True)}assignment{ass_number}{ending}'
            with open(solution_path, 'w') as file:
                file.writelines(empty_solution_file)
            print('generated file' + solution_path)


