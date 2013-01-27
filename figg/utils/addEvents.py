import sqlite3

db='../twigg.db'
conn=sqlite3.connect('../twigg.db')
cursor=conn.cursor()

data = [
('2011-9-18', '8:45', 1, "Stand Up Comedy by David Mitchell, because he's a funny man and that is funny and stuff and stuff", 'fredKingham'),
('2011-9-19', '8:45', 1, "A little play about life the world and everything in it", 'fredKingham'),
]

for row in data:
 cursor.execute("insert into mainPage_event(date, time, venue_id, description, creator) VALUES( ?, ?, ?, ?,?)", row)

conn.commit()

cursor.close()
