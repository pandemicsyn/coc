import eventlet
from eventlet.green import socket
from eventlet.queue import Queue
import re

class SyslogTap(object):

    def __init__(self, statsd_host='172.24.24.14', statsd_port=8125, buff=8192, 
                listen_addr='127.0.0.1', listen_port=8126, patterns=None, 
                debug=False):
        self.counter = 0
        self.hits = 0
        self.q = Queue()
        # key: regex
        self.patterns = {'notice.restart': '.*SIGTERM received.*',
                        'error.auth.stagingus':  '.*ERROR with auth for reseller StagingUS.*',
                        'error.proxy.locktimeout.put': '.*error with PUT.*LockTimeout.*',
                        'error.proxy.timeout.object': '.*ERROR with Object server.*ConnectionTimeout.*',
			'error.proxy.timeout.memcache': '.*Timeout talking to memcached.*',
			'error.proxy.connect.memcache': '.*Error connecting to memcached.*',
                        'error.object.timeout.containerupdate': 'object-server ERROR container update failed with',
			'error.proxy.code.400': '.*code 400.*'}
        self.debug = debug
        self.statsd_addr = (statsd_host, statsd_port)
        self.statsd_sample_rate = 1.0
        self.comp_patterns = {} 
        for item in self.patterns:
            self.comp_patterns[item] = re.compile(self.patterns[item])

    def recompile_regex(self, patterns):
        for item in patterns:
            search_patterns[item] = re.compile(patterns[item])
        return search_patterns

    def check_line(self, line):
        for entry in self.comp_patterns:
            if self.comp_patterns[entry].match(line):
                return entry
        return None

    def stats_print(self):
        lastcount = 0
        lasthit = 0
        while True:
            eventlet.sleep(20)
            lps = (self.counter - lastcount) / 10
            hps = (self.hits - lasthit) / 10
            lastcount = self.counter
            lasthit = self.hits
	    print "--> per second: %d lines  -  hits %d" % (lps, hps)
            print "--> totals: %d hits  -  %d lines" % (self.hits, self.counter) 
            print " "
        
    def send_event(self, payload):
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.sendto(payload, self.statsd_addr)
        except Exception:
            #udp sendto failed (socket already in use?), but thats ok
            print "error: attempting to send statsd event."
            #self.logger.exception(_("Error trying to send statsd event"))

    def statsd_counter_increment(self, stats, delta=1):
        """
        Increment multiple statsd stats counters
        """
        if self.statsd_sample_rate < 1:
            if random() <= self.statsd_sample_rate:
                for item in stats:
                    payload = "%s:%s|c|@%s" % (item, delta,
                        self.statsd_sample_rate)
                    self.send_event(payload)
        else:
            for item in stats:
                payload = "%s:%s|c" % (item, delta)
                self.send_event(payload)

    def worker(self):
        while True:
            msg = self.q.get()
            matched = self.check_line(msg)
            if matched:
                self.statsd_counter_increment([matched])
                self.hits +=1
            else:
                pass

    def start(self, listen_addr='127.0.0.1', listen_port=8126, buff=8192):
        eventlet.spawn_n(self.worker)
        if self.debug:
            eventlet.spawn_n(self.stats_print)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bind_addr = (listen_addr, listen_port)
        sock.bind(bind_addr)
        print "Listening on %s:%d" % bind_addr
        while 1:
            data, addr = sock.recvfrom(buff)
            if not data:
                break
            else:
                self.q.put(data)
                self.counter += 1


if __name__ == '__main__':
    try:
        tap = SyslogTap(debug=True)
        tap.start()
    except KeyboardInterrupt:
        print "\nReceived %d events\n" % counter
