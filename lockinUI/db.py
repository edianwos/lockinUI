import sqlite3


def init_db(db_file: str, records_fields: dict, data_fields: dict):
    """initialize db"""

    records_sql = """
    CREATE TABLE IF NOT EXISTS records (
    id integer PRIMARY KEY,
    {}
    );""".format(',\n'.join([i+' '+j for i, j in records_fields.items()]))

    data_sql = """
    CREATE TABLE IF NOT EXISTS data (
    id integer PRIMARY KEY,
    records_name integer NOT NULL,
    {},
    FOREIGN KEY (records_name) REFERENCES records (name)
    );""".format(',\n'.join([i+' '+j for i, j in data_fields.items()]))
    print(records_sql)
    print(data_sql)
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            conn.execute(records_sql)
            conn.execute(data_sql)
    except Exception as e:
        print(e)
    return conn


def insert_record(conn, record: tuple):
    sql = 'INSERT INTO records (name) VALUES (?)'
    conn.execute(sql, record)


def insert_datum(conn, datum: tuple):
    sql = 'INSERT INTO data (records_name, amplitude, phase, TC, ST, timestamp)\
                 VALUES(?, ?, ?, ?, ?, ?)'
    conn.execute(sql, datum)

