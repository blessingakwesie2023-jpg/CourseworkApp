import sqlite3

DB_NAME = "database.db"


def connect():
    return sqlite3.connect(DB_NAME)


def execute(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


def fetch(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)

    rows = cur.fetchall()

    # safely extract column names
    cols = [description[0] for description in cur.description] if cur.description else []

    conn.close()

    # ALWAYS return exactly 2 values
    return cols, rows