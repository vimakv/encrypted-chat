# =========================
# database.py
# =========================

import sqlite3

DB_NAME = "chat.db"


def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # USERS
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB
        )
        '''
    )

    # MESSAGES
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp TEXT
        )
        '''
    )

    conn.commit()

    conn.close()


def save_message(sender, receiver, message, timestamp):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO messages
        (sender, receiver, message, timestamp)
        VALUES (?, ?, ?, ?)
        ''',
        (
            sender,
            receiver,
            message,
            timestamp
        )
    )

    conn.commit()

    conn.close()