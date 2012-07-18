#!/usr/bin/env python

'''
check_memcache.py

 # A quick and *very* dirty script to health check memcache    #
 # server(s) and dump their stats. Requires python-memcache.   #

Authors:
    Florian Hines <florian.hines<AT>gmail.com>
'''

import memcache
import optparse


def main():
    usage = '''usage: %prog [-h host] [-p port] [-s|-d]
       %prog [-m host1:port,host2:port,...] [-d]'''
    p = optparse.OptionParser(usage)
    p.add_option('--host', '-H', default="127.0.0.1",
        help="Default = 127.0.0.1")
    p.add_option('--port', '-p', default="11211", help="Default = 11211")
    p.add_option('--stats', '-s', action="store_true",
        help="dump output of stats command")
    p.add_option('--debug', '-d', action="store_true",
        help="debug/verbose")
    p.add_option('--multihost', '-m', default=False,
        help="(host:port,host:port,...)")
    options, arguments = p.parse_args()
    if options.multihost is not False:
        servers = options.multihost.split(",")
        result = mconnect(servers, options.stats, options.debug)
    else:
        result = single_connect(options.host, options.port,
            options.stats, options.debug)

    if result is True:
        print "check:ok"
        exit(0)
    else:
        print "check:failed"
        exit(1)


def mconnect(servers, collectstats, debug):
    if debug:
        print "-> Checking %s servers" % len(servers)
    mc = memcache.Client(servers, debug)
    stats = mc.get_stats()
    if collectstats:
        print stats
    if debug:
        print "-> Successfully queried %s of %s servers" % (len(stats),
            len(servers))
    if len(servers) is not len(stats):
        return False
    else:
        return True


def single_connect(host, port, collectstats, debug):
    server = host + ":" + port
    if debug:
        print "-> %s" % server

    sc = memcache.Client([server], debug)
    stats = sc.get_stats()

    if not stats:
        return False

    if not stats[0][1]['uptime']:
        return False

    if collectstats:
        for item in stats[0][1]:
            print item + ":" + stats[0][1][item]

    return True

if __name__ == '__main__':
    main()
