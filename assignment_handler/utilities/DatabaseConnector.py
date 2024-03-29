import os
import mysql.connector
import requests

from Config import GlobalConstants as gc
from utilities.Utility import trailing_sep, get_input


def initialize_table(assignment_count: int) -> None:
    """Takes an assignment count, e.g. 10, and executes a create table statement.
    Table is in the following format:
        |--------------|--------|--------|--------|-----|--------------|
        | student_name | ass_01 | ass_02 | ass_03 | ... | total_points |
        |--------------|--------|--------|--------|-----|--------------|
    This script assumes this form of the database table.
    The attribute total_points is dependent on the ass_XX attribute, see below (update_total_points)."""

    ddl = 'create table points_table (student_name varchar(50) not null primary key, '
    for i in range(1, assignment_count+1):
        ddl += rf'ass_{str(i).zfill(2)} decimal(4, 1) default 0.0 not null, '
    ddl += 'total_points decimal(4, 1) default 0.0 not null);'
    sql_query(ddl, autocommit=True)


def is_db_available() -> bool:
    """Helper method to check for the database connection"""

    if gc.get('offline_mode'):
        return False
    try:
        requests.get(f'''https://{gc.get('db')['host']}''', timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        print('ERROR: cannot establish connection to database, correction continues offline')
        return False


def sql_query(query: str, autocommit: bool = True) -> list[tuple]:
    """Executes an SQL query on the mariaDB database of this project,
    returns all fetched result attributes"""

    result = []
    try:
        # connection to the database
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
        update_failed_counter(ass_number)
    else:
        print('probably the better choice')


def update_total_points() -> None:
    """Sums up points from all assignments and stores the result in the column totals_points,
    does this for every student in the database"""

    ass_expr = 'ass_' + ' + ass_'.join(gc.get('points_').keys())
    sql_query('UPDATE points_table p SET total_points = ( \
        SELECT ' + ass_expr + ' \
        FROM points_table q \
        WHERE p.student_name = q.student_name)')


def update_failed_counter(ass_number: str) -> None:
    """Scans all points up to the current assignment and count the number that is below the configured value
    an stores the result in the column failed_ass, does this for every student in the database"""

    assignments_counted = list(range(3, int(ass_number) + 1))
    if_queries = ' + '.join(map(lambda a: f'IF (q.ass_{str(a).zfill(2)} < ' + str(gc.get('points_passed')) + ', 1, 0)', assignments_counted))

    sql_query(f'UPDATE points_table p SET failed_ass = ( \
        SELECT {if_queries} \
        FROM points_table q \
        WHERE p.student_name = q.student_name)')
