import sqlite3 as sql
from ast import literal_eval

class Polls:
    def __init__(self, db_name):
        self.table_name = db_name
        self.make_table()
        self.polls = {}
        self.download_table()
        self.clear_table()
        self.connection = None
        self.cursor = None
        self.length = len(self.polls)
        self.id = self.length

    def get_poll(self, id):
        self.connect()
        self.cursor.execute("SELECT * FROM polls WHERE id = ?", (id,))
        value = self.cursor.fetchone()
        poll = {"ID": value[0],
                "Question": value[1],
                "Votes": literal_eval(value[2])}
        self.disconnect()
        return poll

    def download_table(self, clear_current = False):
        if clear_current:
            self.polls = {}
        self.connect()
        self.cursor.execute('SELECT * FROM polls')
        values = self.cursor.fetchall()
        for value in values:
            self.polls[value[0]] = {"Question": value[1],
                                    "Votes": literal_eval(value[2])}
        self.length = len(self.polls)
        self.disconnect()

    def connect(self):
        self.connection = sql.connect(self.table_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.commit()
        self.connection.close()

    def make_table(self):
        self.connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS polls (
                            id integer primary key autoincrement,
                            question text,
                            votes text)''')
        self.disconnect()

    def clear_table(self, merge = True):
        self.connect()
        self.cursor.execute('DROP TABLE IF EXISTS polls')
        self.make_table()
        self.length = len(self.polls)
        if merge:
            self.download_table(clear_current = True)

    def add_poll(self, question, choices, push = True):
        self.polls[self.id] = {"Question": question, "Votes": {i: 0 for i in choices}}
        if push:
            self.push_to_table(self.id)
        self.id += 1
        self.length += 1


    def push_to_table(self, id):
        self.connect()
        self.cursor.execute("INSERT INTO polls (id, question, votes) VALUES (?, ?, ?)", (id, str(self.polls[id]["Question"]), str(self.polls[id]["Votes"])))
        self.disconnect()

    def sync_to_table(self):
        for poll in self.polls:
            self.push_to_table(poll)

    def vote(self, id, choice, merge = True):
        self.download_table()
        if id in self.polls:
            if choice in self.polls[id]["Votes"]:
                self.polls[id]["Votes"][choice] += 1
                self.connect()
                self.cursor.execute("UPDATE polls SET Votes = ? WHERE id = ?", (str(self.polls[id]["Votes"]), id))
                self.disconnect()
            else:
                print("Choice does not exist in ID")
                return 0
        else:
            print("ID does not exist")
            return 0

