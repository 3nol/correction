import mysql.connector


def sql_query(query: str):
    result = []
    try:
        con = mysql.connector.connect(
            user='root',
            password='p\'d3@\'dGwL4e;Yxa',
            host='port.halloibims.com',
            port=7001,
            database='sq')
        cur = con.cursor()
        cur.execute(query)
        result = list(cur.fetchall())
        con.close()
    except mysql.connector.Error as e:
        print(f'Error from MariaDB Platform: {e}')
    return result


if __name__ == '__main__':
    print(sql_query('SELECT student_name, ass_01, ass_02 FROM points_table'))
