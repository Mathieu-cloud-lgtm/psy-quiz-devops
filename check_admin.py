import sqlite3

DB_FILE = "psyquiz.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("SELECT id, username, is_psychologist FROM users")
rows = c.fetchall()
for row in rows:
    print(f"ID: {row[0]}, Username: {row[1]}, is_psychologist: {row[2]}")
conn.close()