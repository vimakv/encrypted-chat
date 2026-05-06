import sqlite3
import bcrypt

DB_NAME = "chat.db"


# =========================
# CREATE USERS TABLE
# =========================

def create_users_table():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB
        )
        '''
    )

    conn.commit()

    conn.close()


# =========================
# SIGNUP
# =========================

def signup(username, password):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute(
            '''
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
            ''',
            (
                username,
                hashed
            )
        )

        conn.commit()

        return True

    except Exception as e:

        print("SIGNUP ERROR:", e)

        return False

    finally:

        conn.close()


# =========================
# LOGIN
# =========================

def login(username, password):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT password
        FROM users
        WHERE username=?
        ''',
        (username,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:

        return False

    stored_password = row[0]

    # SQLITE MAY RETURN memoryview
    if isinstance(
        stored_password,
        memoryview
    ):

        stored_password = stored_password.tobytes()

    return bcrypt.checkpw(
        password.encode(),
        stored_password
    )