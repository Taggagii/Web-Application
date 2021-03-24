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
        con = self.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM classes WHERE teacher = ?', (username,))
        data = cursor.fetchall()
        con.commit()
        con.close()
        return data

    def add_class(self, name, user, code, grade, start, end):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute('INSERT INTO classes (name, teacher, code, grade, start, end) VALUES (?, ?, ?, ?, ?, ?)',
                       (name, user, code, grade, start, end))
        data = cursor.fetchall()
        con.commit()
        con.close()
