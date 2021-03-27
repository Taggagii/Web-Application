import sqlite3 as sql
import requests
from passlib.hash import pbkdf2_sha256

# See the weather package for SQL basics. Format is mostly the same
class Login:
    def connect(self):
        self.connection = sql.connect(self.db)
        self.cursor = self.connection.cursor()

    def __init__(self, db):
        self.db = db
        self.connection = None
        self.cursor = None
        self.initialize_login_table()

    def initialize_login_table(self):
        self.connect()
        with open('login.sql', 'r') as schema:
            script = schema.read()
            self.cursor.executescript(script)
        self.connection.commit()
        self.connection.close()

    # Searches for an existing account under the submitted username. If an account is found, the password is matched
    # against the stored hash, and if successful the user is logged in.
    def log_in(self, username, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        user_req = self.cursor.fetchall()
        self.connection.close()

        if user_req:
            return pbkdf2_sha256.verify(password, user_req[0][2])
        return False

    # Checks if a username has been taken, and if not, adds the username and password (hash) to the database
    def sign_up(self, username, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        user_req = self.cursor.fetchall()

        if user_req:
            self.connection.close()
            return False
        else:
            '''Storing passwords as plain text in a database is not secure. Anyone with access (authorized or otherwise)
            would be able to see your password. A cryptographic hashing algorithm transforms its input into a seemingly 
            random, fixed-length string. What's powerful about this is that it's computationally infeasible to reverse 
            the hash
            back into the original input, but the same input will produce the same (at least, the computer can tell it's 
            the same) hash. This can be used to verify that the password a user logs in with is the correct one, without
            ever saving the password itself.'''
            pass_hash = pbkdf2_sha256.hash(password)
            self.cursor.execute(f"INSERT INTO users (username, pass_hash) VALUES ('{username}', '{pass_hash}')")
            self.connection.commit()
            self.connection.close()
            return True

    # Updates a user in the datatbase with a new password (hash)
    def change_password(self, username, new_password):
        self.connect()
        new_pass_hash = pbkdf2_sha256.hash(new_password)
        self.cursor.execute(f"UPDATE users SET pass_hash='{new_pass_hash}' WHERE username='{username}'")
        self.connection.commit()
        self.connection.close()
        return True

    def get_usernames(self):
        self.connect()
        self.cursor.execute("SELECT id, username FROM users")
        values = self.cursor.fetchall()
        self.connection.commit()
        self.connection.close()
        return values





