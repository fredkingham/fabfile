import sqlite3

db = '../twigg.db'
conn = sqlite3.connect('../twigg.db')
cursor = conn.cursor()

info = [('TheSunInn', 'SW13'), ('TheNewRose', 'N1'), ('TheSouthamptonArms', 'NW7')]

for rows in info:
 cursor.execute("insert into mainPage_venue(NAME, POSTCODE) VALUES (?, ?)", rows)

conn.commit()

cursor.close() 
