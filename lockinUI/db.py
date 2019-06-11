import sqlite3


class DataBase:
    def __init__(self, db_file, records_fields, data_fields):
        self.records_sql = """
        CREATE TABLE IF NOT EXISTS records (
        id integer PRIMARY KEY,
        {}
        );""".format(',\n'.join([i+' '+j for i, j in records_fields.items()]))

        self.data_sql = """
        CREATE TABLE IF NOT EXISTS data (
        id integer PRIMARY KEY,
        records_name integer NOT NULL,
        {},
        FOREIGN KEY (records_name) REFERENCES records (name)
        );""".format(',\n'.join([i+' '+j for i, j in data_fields.items()]))

        self.record_insert_sql = 'INSERT INTO records ({}) VALUES ({})'.format(
            ", ".join(records_fields.keys()), ", ".join(['?']*(len(records_fields))))

        self.datum_insert_sql = 'INSERT INTO data (records_name, {}) VALUES(?, {})'.format(
            ", ".join(data_fields.keys()), ", ".join(['?']*(len(data_fields))))

        """initialize db"""
        try:
            self.conn = sqlite3.connect(db_file)
            with self.conn:
                self.conn.execute(self.records_sql)
                self.conn.execute(self.data_sql)
        except Exception as e:
            print(e)
            raise

    def insert_record(self, record_row):
        with self.conn:
            self.conn.execute(self.record_insert_sql, record_row)

    def insert_datum(self, datum_row):
        with self.conn:
            self.conn.execute(self.datum_insert_sql, datum_row)
