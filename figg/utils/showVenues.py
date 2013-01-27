import sqlite3

db = '../twigg.db'
conn = sqlite3.connect('../twigg.db')
c = conn.cursor()
c.execute('select * from mainPage_event')

for row in c:
 print "%s, %s" % (row.id, row.venue_id)

c.close()

