import eventlet
from eventlet.green import socket
import time
import re

counters = {}
stats_seen = 0
debug = True


def report_stats(payload):
    if debug:
        print "reporting stats"
    try:
        with eventlet.Timeout(5, True) as timeout:
            graphite = socket.socket()
            graphite.connect(("127.0.0.1", 5555))
            graphite.sendall(payload)
            graphite.close()
    except Exception as err:
        print "error connecting to graphite: %s" % err


def stats_flush():
    tstamp = int(time.time())
    flush_interval = 10 #seconds not milli
    global counters
    payload = []
    while True:
        eventlet.sleep(flush_interval)
        if debug:
            print "seen %d stats so far." % stats_seen
            print "current counters: %s" % counters
            print "flushing to graphite"
        for item in counters:
            stats = 'stats.%s %s %s\n' % (item,
                        counters[item] / flush_interval, tstamp)
            stats_counts = 'stats_counts.%s %s %s\n' % (item,
                                counters[item], tstamp)
            payload.append(stats)
            payload.append(stats_counts)
            counters[item] = 0
        if payload:
            report_stats("".join(payload))


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
        sample_rate = 1.0
        data, addr = sock.recvfrom(buf)
        if not data:
            break
        else:
            bits = data.split(':')
            if len(bits) == 2:
                key = keycheck.sub('_', bits[0])
                print "got key: %s" % key
                fields = bits[1].split("|")
                field_count = len(fields)
                if field_count >= 2:
                    if fields[1] is "ms":
                        print "error: no timer support yet."
                    elif fields[1] is "c":
                        try:
                            if key not in counters:
                                counters[key] = 0
                            if field_count is 3:
                                if ratecheck.match(fields[2]):
                                    sample_rate = float(fields[2].lstrip("@"))
                                else:
                                    raise Exception("bad sample rate.")
                            counters[key] += float(fields[0] or 1) * \
                                (1 / float(sample_rate))
                        except Exception as err:
                            print "error decoding packet: %s" % err
                        stats_seen += 1
                    else:
                        print "error: unsupported stats type"
                else:
                    print "error: not enough fields received"
            else:
                print "error: invalid request"


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\nReceived %d events\n" % stats_seen
