import sqlite3

DATABASE = "splitmate.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    with open("schema.sql", "r") as file:
        conn.executescript(file.read())

    conn.commit()
    conn.close()