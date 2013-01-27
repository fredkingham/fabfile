from threading import Thread
import time

def print_hello():
    print "hello"
    time.sleep(10)
    print "hello"

def print_goodbye():
    print "goodbye"
    time.sleep(10)
    print "goodbye"

h = Thread(target = print_hello)
g = Thread(target = print_goodbye)
h.daemon = True
g.daemon = True
h.start()
time.sleep(3)
g.start()



