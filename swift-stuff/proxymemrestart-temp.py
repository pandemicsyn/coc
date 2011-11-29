from resource import getpagesize
from subprocess import call
import datetime
import time
import os
from sys import exit

# warn at 5GB of use , reload at 6GB
memlimit_warn = 5120 #in MB
memlimit_max = 6144 #in MB

def get_socket_memuse():
    try:
        with open('/proc/net/sockstat') as proc_sockstat:
            for entry in proc_sockstat:
                if entry.startswith("TCP: inuse"):
                    return int(entry.split()[10]) * getpagesize() / 1024 / 1024
    except IOError as e:
        if e.errno != errno.ENOENT:
                raise

def proxy_reload():
    print "--> Attempting proxy reload"
    command = '/etc/init.d/swift-proxy'
    sudo = False
    args = "reload"
    if sudo:
        retcode = call(['sudo', command, args])
    else:
        retcode = call([command, args])
    if retcode is 0:
        return True
    else:
        return False

def main():
    inuse = get_socket_memuse()
    if inuse >= memlimit_warn:
        now = datetime.datetime.now()
        print "sockstat mem usage at %dMB - %s" % (inuse, str(now)) 
        if inuse >= memlimit_max:
            if proxy_reload():
                print "--> Reloaded proxy"
            else:
                print "--> Reload failed"
        exit(1)
        time.sleep(120)
            print "usage after 120s sleep: %dMB" % get_socket_memuse()

if __name__ == '__main__':
    try:
        os.mkdir("/var/lock/proxymemusecheck")
    except OSError as e:
        print str(e)
        exit(1)
    main()
    try:
        os.rmdir("/var/lock/proxymemusecheck")
    except Exception as e:
    print "error removing lock"
        print str(e)
