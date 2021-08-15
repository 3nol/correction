import os, string

from jellyfish import levenshtein_distance

from .SSHConnector import TitanConnector





class AutoFeedback(TitanConnector):
    """Handles executing assignment files and generating an output file"""

    def __init__(self, pop: str, pw: str, server: str, port: int = 22, local_location: str = ""):
        super().__init__(pop, pw, server, port, local_location)

    def split_tasks(self, solution_file: str):
        """Splits a solution file in the connector.local_location into individual task files"""
        with open(self.local_location + solution_file, 'r') as file:
            content = file.readlines()
        sol = solution_file.rsplit('.', 1)
        tasks = []
        for line in content:
            if re.match('[^\n#].*', line.strip()):
                task_path = f'{sol[0]}_task{len(tasks) + 1}.{sol[1]}'
                with open(self.local_location + task_path, 'w') as task:
                    task.write(line.strip())
                tasks.append(task_path)
        print('generated', len(tasks), 'task files')
        return tasks

    def evaluate_solution(self, solution_file: str, compare_file: str, operation: str) -> tuple[int, str]:
        """Compares solution and comparison file in local directory with Levenshtein (-1 if error)"""
        if operation == 'execute':
            self.put_file(self.local_location + solution_file, 'solution.sh')
            i = self.run_sh_file('solution.sh', logfile=True, copy_log_file=False, auto_close=False)
            self.run_command('rm solution.sh', close_connection=True)
            with open(i['local'], 'r') as f:
                out = f.read()
                if out.split('---', 1)[1]:
                    return -1, out.split('---', 1)[1]
                output = out.split('---', 1)[0].strip()
            os.remove(i['local'])   # removing local logfile
        elif operation == 'compare':
            with open(self.local_location + solution_file, 'r') as f:
                output = f.read().strip()
        else:
            raise NotImplementedError

        with open(self.local_location + compare_file, 'r') as f:
            comparison = f.read().strip()
        distance = levenshtein_distance(output, comparison)
        if distance == 0:
            return distance, 'exact match'
        else:
            return distance, '>solution_file:\n' + output + '\n---\n>comparison_file:\n' + comparison

    def generate_feedback_file(self):
        """Generates the feedback file based on a template and on the evaluation"""
        # TODO template file
        return True
