
class GlobalConstants:

    __conf = {
        'corrector': 'Chuck Norris',
        'source_path': '../assignments',
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
            'user': ***REMOVED***,
            'password': ***REMOVED***,
            'host': ***REMOVED***,
            'port': ***REMOVED***,
            'database': ***REMOVED***
        },
        'concat_folder': 'concatenated',
        'feedback_folder': 'feedback',
        'excluded_names': ['Chuck Norris', 'Bruce Lee']
    }

    @staticmethod
    def get(key: str) -> any:
        try:
            if key.startswith('points_'):
                return GlobalConstants.__conf['points_'][key.split('points_', 1)[1].zfill(2)]
            return GlobalConstants.__conf[key]
        except KeyError:
            print(f'GlobalConstant not found: {key}')
        return None
