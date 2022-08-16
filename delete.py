import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Delete table contents
conn.execute('''DELETE FROM users WHERE userId = 2''')

conn.close()

