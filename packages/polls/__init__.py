#we are using sqlite3 for out sql database needs as it allows one to host the database locally
import sqlite3 as sql
from ast import literal_eval

#classes used to keep app.py clean
class Polls:
    def __init__(self, db_name):
        '''
        sets internal variables and pulls the table we will be working with
        (during testing has the ability is used to clear the contents of the
         table in the database)
                        |   TABLE FORM   |
        -----------------------------------------------------------------
                id        INTEGER PRIMARY KEY AUTOINCREMENT
                question  TEXT
                votes     TEXT
        '''
        self.database_name = db_name
        self.make_table()
        self.polls = {}
        self.download_table()
        #self.clear_table() # was used during development
        self.connection = None
        self.cursor = None
        self.length = len(self.polls)
        self.id = self.length

    def get_poll(self, id):
        '''
        connects to the database, pulls the data for a specified id and returns a dict in form:
            {"ID": id string, "Question": question string, "Votes": {choice string: vote_count int} dict}}
        '''
        self.connect()
        self.cursor.execute("SELECT * FROM polls WHERE id = ?", (id,)) #SQL command to request a row in polls where the id is as specified
        value = self.cursor.fetchone() #fetches the request
        poll = {"ID": value[0],
                "Question": value[1],
                "Votes": literal_eval(value[2])}
        self.disconnect()
        return poll

    def download_table(self, clear_current = False):
        '''
        pulls the polls table into local memory
        (used in __init__ to bring the local table up to date)
        '''
        if clear_current:
            self.polls = {}
        self.connect()
        self.cursor.execute('SELECT * FROM polls') #requests all rows in polls
        values = self.cursor.fetchall()
        for value in values:
            #updates each key in polls with the local table
            self.polls[value[0]] = {"Question": value[1],
                                    "Votes": literal_eval(value[2])}
        self.length = len(self.polls)
        self.disconnect()

    def connect(self):
        '''
        opens the connection between the class and the database
        '''
        self.connection = sql.connect(self.database_name) #creates new connection to the databse name passed in during initalization
        self.cursor = self.connection.cursor()

    def disconnect(self):
        '''
        closes the connection between the class and the database
        '''
        self.connection.commit()
        self.connection.close()

    def make_table(self):
        '''
        checks if the polls table exists and creates it if it does not
        '''
        self.connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS polls (
                            id integer primary key autoincrement,
                            question text,
                            votes text)''')
        self.disconnect()

    def clear_table(self, merge = True):
        '''
        FOR USE WHEN TESTING:
            clears / drops the polls table
        '''
        self.connect()
        self.cursor.execute('DROP TABLE IF EXISTS polls')
        self.make_table()
        #self.disconnect() is not needed as self.make_table() calls to disconnect
        self.length = len(self.polls)
        if merge:
            self.download_table(clear_current = True)

    def add_poll(self, question, choices, push = True):
        '''
        takes in a question and list of choices and adds them to the local table as well
            as the database so long as push is left as True
        '''
        self.polls[self.id] = {"Question": question, "Votes": {i: 0 for i in choices}}
        if push:
            self.push_to_table(self.id)
        self.id += 1
        self.length += 1


    def push_to_table(self, id):
        '''
        takes the id of a row in the local table and pushes it to the database
        '''
        self.connect()
        self.cursor.execute("INSERT INTO polls (id, question, votes) VALUES (?, ?, ?)", (id, str(self.polls[id]["Question"]), str(self.polls[id]["Votes"])))
        self.disconnect()


    def vote(self, id, choice, merge = True):
        '''
        takes in a row id and choice and attempts to increment the choice's vote count by one
        '''
        self.download_table() #updates local
        if id in self.polls: #makes sure the id exists
            if choice in self.polls[id]["Votes"]: #makes sure the choice exists in the id
                self.polls[id]["Votes"][choice] += 1 #increments the local choice's votes
                self.connect()
                self.cursor.execute("UPDATE polls SET Votes = ? WHERE id = ?", (str(self.polls[id]["Votes"]), id)) #pushes the updated poll to replace the database's copy
                self.disconnect()
            else:
                return "Choice does not exist in ID"
        else:
            return "ID does not exist"

