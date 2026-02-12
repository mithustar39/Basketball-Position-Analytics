import sqlite3

conn  = sqlite3.connect('basketball.db')

cursor = conn.cursor()

cursor.execute("SELECT * FROM players WHERE position =?", (position,))
rows = cursor.fetchall()


for row in rows:
    print(row)

conn.close()