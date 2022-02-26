import os
import mysql.connector
import requests

from Config import GlobalConstants as gc
from utilities.Utility import trailing_sep, get_input


def is_db_available() -> bool:
    """Helper method to check for the database connection"""

    try:
        requests.get(f'''https://{gc.get('db')['host']}''', timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        print('ERROR: not connected to the internet, correction starts in offline mode!')
        return False


def sql_query(query: str, autocommit: bool = True) -> list[tuple]:
    """Executes an SQL query on the mariaDB database of this project,
    returns all fetched result attributes"""

    result = []
    try:
        # connection to Jannes database <3
        con = mysql.connector.connect(
            user=gc.get('db')['user'],
            password=gc.get('db')['password'],
            host=gc.get('db')['host'],
            port=gc.get('db')['port'],
            database=gc.get('db')['database'])
        cur = con.cursor()
        cur.execute(query)
        result = list(cur.fetchall())
        if autocommit:
            con.commit()
        con.close()
    except mysql.connector.Error as e:
        # something went shit
        print(f'error from MariaDB platform: {e}')
    return result


def insert_single_student(student_name: str, ass_number: str, total_points: str) -> None:
    """Inserts the points per assignment for a certain student into the database"""
    sql_query(f"UPDATE points_table SET ass_{ass_number} = {total_points} WHERE student_name = '{student_name}'")


def write_students_to_db(ass_number: str, student_names=None) -> None:
    """Rescans all feedbacks for a specific assignment, picks out the points and writes them to the DB"""

    if student_names is None:
        student_names = [f.path for f in os.scandir(gc.get('source_path')) if f.is_dir()]

    if get_input('Are you sure? [y/n]'):
        print('inserting points for assignment', ass_number + ':')
        for name in student_names:
            with open(f'''{trailing_sep(name) + trailing_sep(gc.get('feedback_folder'))}assignment{ass_number}.txt''',
                      mode='r', errors='replace', encoding='utf-8') as f:
                total = str(float(f.readlines()[1][1:].split('/', 1)[0]))
            insert_single_student(str(name).rsplit(os.path.sep, 1)[1], ass_number, total)
            print('-', str(name).rsplit(os.path.sep, 1)[1], total)
        update_total_points()
    else:
        print('probably the better choice')


def update_total_points() -> None:
    """Sums up all points form assignment 01 to 11 and stores the result in the column totals_points,
    does this for every student in the database"""

    sql_query('UPDATE points_table p SET total_points = ( \
        SELECT ass_01 +  ass_02 + ass_03 + ass_04 + ass_05 + ass_06 + ass_07 + ass_08 + ass_09 + ass_10 + ass_11 \
        FROM points_table q \
        WHERE p.student_name = q.student_name)')
