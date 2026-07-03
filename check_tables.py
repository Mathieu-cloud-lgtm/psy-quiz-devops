import sqlite3

DB_FILE = "psyquiz.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables dans la base :", tables)
conn.close()