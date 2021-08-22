import mysql.connector


def sql_query(query: str):
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
        con.close()
    except mysql.connector.Error as e:
        print(f'Error from MariaDB Platform: {e}')
    return result


if __name__ == '__main__':
    print(sql_query('SELECT student_name, ass_01, ass_02 FROM points_table'))
