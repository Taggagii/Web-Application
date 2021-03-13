import sqlite3 as sql
import requests
from passlib.hash import pbkdf2_sha256


class Login:
    def connect(self):
        self.connection = sql.connect(self.db)
        self.cursor = self.connection.cursor()

    def __init__(self, db):
        self.db = db
        self.connection = None
        self.cursor = None
        #self.initialize_login_table()

        password = "pass"
        h = pbkdf2_sha256.hash(password)

    def initialize_login_table(self):
        self.connect()
        with open('login.sql', 'r') as schema:
            script = schema.read()
            self.cursor.executescript(script)
        self.connection.commit()
        self.connection.close()

    def log_in(self, username, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        user_req = self.cursor.fetchall()
        self.connection.close()

        if user_req:
            return pbkdf2_sha256.verify(password, user_req[0][2])
        return False

    def sign_up(self, username, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        user_req = self.cursor.fetchall()

        if user_req:
            self.connection.close
            return False
        else:
            pass_hash = pbkdf2_sha256.hash(password)
            self.cursor.execute(f"INSERT INTO users (username, pass_hash) VALUES ('{username}', '{pass_hash}')")
            self.connection.commit()
            self.connection.close
            return True





