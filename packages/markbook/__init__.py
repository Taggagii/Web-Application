import sqlite3 as sql
from datetime import date


class Markbook:
    def connect(self):
        self.connection = sql.connect(self.db)
        self.cursor = self.connection.cursor()

    def initialize_markbook_tables(self):
        self.connect()
        with open('markbook.sql', 'r') as schema:
            script = schema.read()
            self.cursor.executescript(script)
        self.connection.commit()
        self.connection.close()

    def __init__(self, db_path):
        self.connection = None
        self.cursor = None
        self.db = db_path
        self.error_dict = {0: None,
                           1: "Not a valid course code",
                           2: "Not a valid start date",
                           3: "Not a valid end date",
                           4: "Not a valid grade"}
        self.initialize_markbook_tables()


    '''def class_exists(self, name):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM classes WHERE name = ?', (name,))
        if cursor.fetchall():
            con.commit()
            con.close()
            return 'A class with that name already exists. Please choose another'
        else:
            con.commit()
            con.close()
            return None'''

    def get_user_classes(self, username):
        self.connect()
        self.cursor.execute('SELECT * FROM classes WHERE teacher = ?', (username,))
        data = self.cursor.fetchall()
        self.connection.commit()
        self.connection.close()
        return data

    def add_class(self, name, user, code, grade, start, end):
        self.connect()

        if isinstance(grade, int):
            if not (12 < grade or grade < 9):
                return self.error_dict[4]
        else:
            return self.error_dict[4]
        grade = int(grade)
        if len(code) != 6:
            return self.error_dict[4]
        start = date(start)
        end = date(end)

        self.cursor.execute('INSERT INTO classes (name, teacher, code, grade, start, end) VALUES (?, ?, ?, ?, ?, ?)',
                       (name, user, code, grade, start, end))
        self.connection.commit()
        self.connection.close()
