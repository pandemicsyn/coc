# Quick and *very* dirty script to health check memcache server(s) and dump their stats. Requires python-memcache

# Usage

    syn@masada:~$ python bin/check-memcache.py -h
    Usage: check-memcache.py [-h host] [-p port] [-s|-d] OR check-memcache.py [-m host1:port,host2:port,...] [-d]

    Options:
      -h, --help            show this help message and exit
      -H HOST, --host=HOST  Default = 127.0.0.1
      -p PORT, --port=PORT  Default = 11211
      -s, --stats           dump output of stats command
      -d, --debug           debug/verbose
      -m MULTIHOST, --multihost=MULTIHOST
                            (host:port,host:port,...)

# Basic Zenoss friendly check
    fhines@masada:~$ python bin/check-memcache.py -H 127.0.0.1 
    check:failed
    fhines@masada:~$ echo $?
    1

# Check multiple servers (enable debug)
    syn@masada:~$ python bin/check-memcache.py -m 192.168.1.107:11211,127.0.0.1:11211 -d
    -> Checking 2 servers
    MemCached: MemCache: inet:127.0.0.1:11211: connect: Connection refused.  Marking dead.
    -> Successfully queried 1 of 2 servers
    check:failed

# Grab some stats.
    syn@masada:~$ python bin/check-memcache.py -H 192.168.1.107 -s | tail
    evictions:0
    bytes:155174618
    connection_structures:744
    rusage_user:35976.700000
    time:1304659236
    delete_hits:426825
    pointer_size:64
    decr_misses:0
    get_hits:1783172303
    check:ok
