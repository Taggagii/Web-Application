import sqlite3 as sql


class Chat:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.create_table()
        self.clear_table()
        self.add_user_one("testing")

    def get_table_values(self):
        self.connect()
        self.cursor.execute("SELECT * FROM chat")
        values = self.cursor.fetchall()
        self.disconnect()
        return values

    def add_user_one(self, name):
        self.connect()
        self.cursor.execute("INSERT INTO chat (userone) VALUES (?)", (name,))
        self.disconnect()

    def clear_table(self):
        self.connect()
        self.cursor.execute("DROP TABLE IF EXISTS chat")
        self.create_table()


    def connect(self):
        '''
        opens the connection between the class and the database
        '''
        self.connection = sql.connect(self.db_name)  # creates new connection to the databse name passed in during initalization
        self.cursor = self.connection.cursor()

    def disconnect(self):
        '''
        closes the connection between the class and the database
        '''
        self.connection.commit()
        self.connection.close()


    def create_table(self):
        self.connect()
        self.cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS chat (
                    id integer primary key autoincrement,
                    userone text, 
                    usetwo text
                    )
        ''')
        self.disconnect()

