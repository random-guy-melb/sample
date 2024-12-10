
from configs import config
import sqlite3


class UserData():

    def __init__(self):
        self.conn = sqlite3.connect(config.feedback_db)
        self.cursor = self.conn.cursor()


    def create_logintable(self):
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS UserLogin(username text, password nvarchar(255), email text, empcode text, manager text, birthyear text, vertical text, created text, changed text)')


    def create_feedbacktable(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS UserFeedback(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username text, 
            email text, 
            vertical text, 
            query text, 
            response text, 
            feedback text, 
            comment text, 
            ts datetime)""")


    def _update(self, username, email, vertical, query, response, feedback, comment, ts):
        self.cursor.execute("update UserFeedback set username=?, email=?, vertical=?, query=?, response=?, feedback=?, comment=?, ts=?",
                            (username, email, vertical, query, response, feedback, comment, ts))
        self.conn.commit()
        self.conn.close()


    def save_feedback(self, username, email, vertical, query, response, feedback, comment, ts):
        self._update(username, email, vertical, query, response, feedback, comment, ts)

