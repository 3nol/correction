import os


class GlobalConstants:
    """
    Stores all constant configurations of this program, includes:
        - the correcting person, the source directory and point distribution
        - database connection credentials
        - folder names and excluded ones
        - main- and subtask frequent prefixes for detection
    """

    # dictionary which stores everything
    __conf = {
        'corrector': 'Leon Wenzler',
        'source_path': f'{os.getcwd().rsplit(os.path.sep, 2)[0]}{os.path.sep}students{os.path.sep}',
        'points_': {
            '01': [[3, 2], [3], [2]],
            '02': [[10], [0]],
            '03': [[2, 1, 2, 2], [3]],
            '04': [[1, 1], [1, 1, 2, 2, 2]],
            '05': [[1], [3, 3, 3]],
            '06': [[3], [3], [2, 2]],
            '07': [[5, 5]],
            '08': [[1, 1, 1, 3], [0.5, 2, 0.5, 1]],
            '09': [[1, 1, 1], [1, 1, 1, 1, 2, 1]],
            '10': [[1, 1, 1], [1, 1, 1], [4]],
            '11': [[1, 3, 6]]
        },

        'db': {
            'user': 'root',
            'password': 'p\'d3@\'dGwL4e;Yxa',
            'host': 'port.halloibims.com',
            'port': 7001,
            'database': 'sq'
        },

        'concat_folder': 'concatenated',
        'feedback_folder': 'feedback',
        'excluded_names': ['clara.biedermann', 'leon.wenzler', 'johannes.fuchs'],
        'excluded_filetypes': [
            '.gitkeep', '.*docx', '.*odt', '.*pdf', '.*jpe?g', '.*png', '.*zip', '.*html'
        ],
        'excluded_folders': ['.git', '.svn', '.idea'],

        'maintask_prefixes': [
            'Task', 'task', 'TASK', 'Aufgabe', 'aufgabe', 'AUFGABE', 'Lösung', 'lösung', 'LÖSUNG',
            'Loesung', 'loesung', 'LOESUNG', 'Solution', 'solution', 'SOLUTION', 'Sol', 'sol', 'SOL',
            'Exercise', 'exercise', 'EXERCISE', r'Ex\.?', r'ex\.?', r'EX\.?', 'Number', 'number', 'NUMBER',
            r'No\.?', r'no\.?', r'NO\.?', 'Nummer', 'nummer', 'NUMMER', r'Nr\.?', r'nr\.?', r'NR\.?'
        ],
        'subtask_prefixes': [
            'SubTask', 'subtask', 'SUBTASK', 'Aufgabe', 'aufgabe', 'AUFGABE', r'Ex\.?', r'ex\.?', r'EX\.?',
            r'No\.?', r'no\.?', r'NO\.?', r'Nr\.?', r'nr\.?', r'NR\.?'
        ]
    }

    @staticmethod
    def get(key: str) -> any:
        """Static getter method which retrieves the constants,
        has an in-built shortcut for getting the points per assignments"""
        try:
            if key.startswith('points_'):
                return GlobalConstants.__conf['points_'][key.split('points_', 1)[1].zfill(2)]
            return GlobalConstants.__conf[key]
        except KeyError:
            print(f'GlobalConstant not found: {key}')
            exit(1)
