import os
from Utility import get_exercise_points, tailing_os_sep
from Private import source_path


def create_empty_solution(student: str):
    exercise_points = get_exercise_points(ass_number)
    lines = ['# Assignment ' + ass_number + '\n', '# ' + student, '\n', '#\n']
    task_counter = 1
    for exercise in exercise_points:
        lines.append('#\n')
        lines.append('#\n')
        if len(exercise) > 1:
            lines.append('# Task ' + str(task_counter) + ':\n')
            subtask_counter = 'a'
            for subtask in exercise:
                lines.append('#\n')
                lines.append('# ' + subtask_counter + ')')
                lines.append('\n\n')
                subtask_counter = chr(ord(subtask_counter) + 1)
        else:
            lines.append('# Task ' + str(task_counter) + ':')
            lines.append('\n')
        lines.append('\n')
        task_counter += 1
    return lines


if __name__ == '__main__':
    ass_number = '05'
    ending = '.txt'
    tutti_names = [f.path for f in os.scandir(source_path) if f.is_dir()]
    for name in tutti_names:
        if 'fuchs' not in name:
            just_name = str(name).split(os.path.sep)
            empty_solution_file = create_empty_solution(just_name[len(just_name) - 1])
            solution_path = f'{tailing_os_sep(name, True)}assignment{ass_number}{ending}'
            with open(solution_path, 'w') as file:
                file.writelines(empty_solution_file)
            print('generated file' + solution_path)


