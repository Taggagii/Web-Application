import sqlite3 as sql


class Markbook:
    def connect(self):
        return sql.connect(self.db)

    def initialize_markbook_tables(self):
        con = self.connect()
        cursor = con.cursor()
        with open('markbook.sql', 'r') as schema:
            script = schema.read()
            cursor.executescript(script)
        con.commit()
        con.close()

    def __init__(self, db_path):
        self.db = db_path
        self.initialize_markbook_tables()

    def new_class(self):
        con = self.connect()
        cursor = con.cursor()
