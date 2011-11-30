import eventlet
from eventlet.green import socket
from eventlet.queue import Queue
import time
import re


counters = {}
stats_seen = 0
debug = False

def report_stats(payload):
    if debug:
        print "reporting stats"
    try:
        with eventlet.Timeout(5, True) as timeout:
            graphite = socket.socket()
            graphite.connect(("127.0.0.1", 5555))
            stime = time.time()
            graphite.sendall(payload)
            graphite.close()
    except Exception as e:
        print "error connecting to graphite: %s" % e


def stats_flush():
    tstamp = int(time.time())
    flush_interval = 10 #seconds not milli
    global counters
    payload = None
    while True:
        eventlet.sleep(flush_interval)
        if debug:
            print "current counters: %s" % counters
            print "flushing to graphite"
        for item in counters:
            stats = 'stats.%s %s %s\n' % (item, counters[item] / flush_interval, tstamp)
            stats_counts = 'stats_counts.%s %s %s\n' % (item, counters[item], tstamp) 
            payload = "".join([stats, stats_counts])
            counters[item] = 0 
        report_stats(payload)


def main():
    global counters
    global stats_seen
    keycheck = re.compile(r'\s+|/|[^a-zA-Z_\-0-9\.]')
    ratecheck = re.compile('^@([\d\.]+)')
    eventlet.spawn_n(stats_flush)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 8125)
    sock.bind(addr)
    buf = 8192
    print "Listening on %s:%d" % addr
    while 1:
        sample_rate = 1
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
                        #checking if theres a sample rate
                        if len(fields) is 3:
                            try:
                                sample_rate = ratecheck.match(fields[2]).groups()[0]
                            except (IndexError, AttributeError):
                                #y u no pass @ symbol ?
                                print "error: bad sample rate field"
                                break

                        if key not in counters:
                            counters[key] = 0
                        try:
                            counters[key] += float(fields[0] or 1) * (1 / float(sample_rate))
                        except (ValueError, ZeroDivisionError) as e:
                            print e
                else:
                    print "error: invalid"
            else:
                print "error: invalid"
            stats_seen += 1 

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\nReceived %d events" % stats_seen
        print '\n'
