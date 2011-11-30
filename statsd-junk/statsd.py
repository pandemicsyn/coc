import eventlet
from eventlet.green import socket
from eventlet.queue import Queue
import time
import re

counters = {}
counter = 0
hits = 0

sp = re.compile('.*SIGTERM received.*')
sp2 = re.compile('.*"DELETE.*')

q = Queue()

def report_stats(payload):
    try:
        with eventlet.Timeout(5, True) as timeout:
            graphite = socket.socket()
            graphite.connect(("127.0.0.1", 5555))
            graphite.sendall(payload)
            graphite.close()
            print "sent payload to graphite"
    except Exception as e:
        print e


def stats_print():
    tstamp = int(time.time())
    flush_interval = 10 #seconds not milli
    global counters
    payload = None
    while True:
        eventlet.sleep(flush_interval)
        print "current counters: %s" % counters
        print "flushing to graphite"
        for item in counters:
            stats = 'stats.%s %s %s\n' % (item, counters[item] / flush_interval, tstamp)
            stats_counts = 'stats_counts.%s %s %s\n' % (item, counters[item], tstamp) 
            payload = "".join([stats, stats_counts])
            counters[item] = 0 
        report_stats(payload)

def worker():
    global hits
    while True:
        msg = q.get()
        #print msg.split(':')


def main():
    global counters
    keycheck = re.compile(r'\s+|/|[^a-zA-Z_\-0-9\.]')
    ratecheck = re.compile('^@([\d\.]+)')
    eventlet.spawn(worker)
    eventlet.spawn(stats_print)
    global counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 8125)
    sock.bind(addr)
    buf = 8192
    print "Listening on %s:%d" % addr
    while 1:
        data, addr = sock.recvfrom(buf)
        if not data:
            break
        else:
            bits = data.split(':')
            if len(bits) == 2:
                key = keycheck.sub('_', bits[0])
                print "got key: %s" % key
                fields = bits[1].split("|")
                if fields[1]:
                    if fields[1] is "ms":
                        print "error: no timer support yet"
                    else:
                        sample_rate = 1
                        try:
                            sample_rate = ratecheck.match(fields[2]).groups()[0]
                        except AttributeError:
                            #y u pass @ symbol ?
                            pass
                        if key not in counters:
                            counters[key] = 0
                        try:
                            counters[key] = float(fields[0] or 1) * (1 / float(sample_rate))
                        except ValueError:
                            print "error: bad counter data"
                        except ZeroDivisionError:
                            print "error: bad sample rate"
                else:
                    print "error: invalid"
            else:
                print "error: invalid"
            counter += 1 

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\nReceived %d events" % counter
        print '\n'
