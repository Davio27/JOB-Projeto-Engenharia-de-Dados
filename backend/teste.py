import sqlite3

conn = sqlite3.connect("backend\historico.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM quotes;")
print(cur.fetchone()[0])

conn.close()
