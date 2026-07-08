import sqlite3

sql_file = "database.sql"
db_file = "database.db"

conn = sqlite3.connect(db_file)

with open(sql_file, "r", encoding="utf-8") as file:
    sql_script = file.read()

conn.executescript(sql_script)

conn.commit()
conn.close()

print("Database created successfully!")