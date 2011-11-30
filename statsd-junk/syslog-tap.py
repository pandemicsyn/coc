import eventlet
from eventlet.green import socket
from eventlet.queue import Queue
import re

counter = 0
hits = 0

sp = re.compile('.*SIGTERM received.*')
sp2 = re.compile('.*"DELETE.*')

q = Queue()

def stats_print():
    global counter
    while True:
        eventlet.sleep(5)
        print "%d hits, %d misses" % (hits, counter)

def worker():
    global hits
    while True:
        msg = q.get()
        if sp.match(msg) or sp2.match(msg):
            hits += 1
            #print "HIT: %s" % msg
        else:
            pass

def producer():
    global counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 8126)
    sock.bind(addr)
    buf = 512
    print "Listening on %s:%d" % addr
    while 1:
        data, addr = sock.recvfrom(buf)
        if not data:
            break
        else:
            q.put(data)
            #print "recv: %s" % data
            counter += 1


def main():
    eventlet.spawn(worker)
    eventlet.spawn(stats_print)
    global counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 8126)
    sock.bind(addr)
    buf = 512
    print "Listening on %s:%d" % addr
    while 1:
        data, addr = sock.recvfrom(buf)
        if not data:
            break
        else:
    #        print "recv: %s" % data
            q.put(data)
            counter += 1
    #

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\nReceived %d events" % counter
        print '\n'
