import sqlite3

conn = sqlite3.connect("historico.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM quotes;")
print(cur.fetchone()[0], "linhas")

conn.close()

conn = sqlite3.connect('historico.db')
cur = conn.cursor()
cur.execute("SELECT MAX(create_date) FROM quotes;")
print(cur.fetchone())
conn.close()
