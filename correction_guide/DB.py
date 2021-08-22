import mysql.connector


def sql_query(query: str, autocommit: bool = True):
    """Executes an SQL query on the mariaDB database of this project,
    returns all fetched result attributes"""

    result = []
    try:
        con = mysql.connector.connect(
            user=***REMOVED***,
            password=***REMOVED***,
            host=***REMOVED***,
            port=***REMOVED***,
            database=***REMOVED***)
        cur = con.cursor()
        cur.execute(query)
        result = list(cur.fetchall())
        if autocommit:
            con.commit()
        con.close()
    except mysql.connector.Error as e:
        print(f'Error from MariaDB Platform: {e}')
    return result


def update_db():
    sql_query('UPDATE points_table p SET total_points = ( \
    SELECT ass_01 +  ass_02 + ass_03 + ass_04 + ass_05 + ass_06 + ass_07 + ass_08 + ass_09 + ass_10 + ass_11 \
    FROM points_table q \
    WHERE p.student_name = q.student_name)')
