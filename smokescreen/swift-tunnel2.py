#!/usr/bin/env python

'''
swift_tunnel2.py

 # A quick & *very* dirty script that acts a HTTP proxy to openstack #
 # Requires eventlet, greenlet, python-memcache,                     #
 # Works against a stock openstack swift SAIO install out of the box #
 # Its dirty, im a relative python n00b, and its only purpose was to #
 # let me tinker with eventlet.  Use at your own peril ;)            #
 # Constructive feed back is always welcome.                         #
 # Author: Florian Hines <florian.hines<AT>gmail.com                 #

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA.

Authors:
    Florian Hines <florian.hines<AT>gmail.com>
'''
import eventlet
from eventlet import wsgi
from eventlet.green import socket
from eventlet.green import httplib
memcache = eventlet.import_patched('memcache')
from eventlet import greenio, GreenPool, sleep, listen
from configobj import ConfigObj
from urlparse import urlparse
from os import path
import optparse
import hashlib
import cPickle
import signal
import errno
import time
import sys
import re
import os

listen_port = 8090 #port to listen on
auth_server = '127.0.0.1'
auth_https = False
auth_port = '11000'
auth_acct = 'test'
auth_user = 'tester'
auth_pass = 'testpass'
storage_url_port = 8080 #TODO: needs to be checked on the fly
storage_https = False #TODO: needs to be checked on the fly
use_cache = False #perform ghetto caching using memcache
memcache_host = []
cache_ttl = 900
workers = 1

auth = ''
storage_token = ''
storage_url = ''
fake_cache = {}
mc = None


def setup_mc():
    global mc
    memcache_host = ["127.0.0.1:11211"]
    mc = memcache.Client(memcache_host, debug=0)


def setconfig(config):
    try:
        options = config['swift-tunnel']
        coptions = config['ghetto-cache']
        global listen_port
        listen_port = options.as_int('listen_port')
        global workers
        workers = options.as_int('workers')
        global auth_server
        auth_server = options['auth_server']
        global auth_https
        auth_https = options.as_bool('auth_https')
        global auth_port
        auth_port = options.as_int('auth_port')
        global auth_acct
        auth_acct = options['auth_acct']
        global auth_user
        auth_user = options['auth_user']
        global auth_pass
        auth_pass = options['auth_pass']
        global storage_url_port
        storage_url_port = options.as_int('storage_url_port')
        global storage_https
        storage_https = options.as_bool('storage_https')
        global use_cache
        use_cache = coptions.as_bool('use_cache')
        global memcache_host
        memcache_host.append(coptions['memcache_host'])
        global cache_ttl
        cache_ttl = coptions.as_int('cache_ttl')
    except KeyError as (e):
        print "Error: your missing the config var %s " % e
        print "I'm too lazy to default, so im just bailing."
        sys.exit(2)


def perform_auth(url, port, acct, user, password):
    if auth_https is True:
        authconn = httplib.HTTPSConnection(url, port)
    else:
        authconn = httplib.HTTPConnection(url, port)
    authconn.request("GET", "/v1/%s/auth" % acct, "",
        {"X-Storage-User": user, "X-Storage-Pass": password})
    response = authconn.getresponse()

    if response.status != 204:
        print "Bad Monkey - No TACO!"
        raise ResponseError(response.status, response.reason)

    auth = storage_token = storage_url = None
    for header in response.getheaders():
        if header[0].lower() == "x-auth-token":
            auth = header[1]
        if header[0].lower() == "x-storage-token":
            storage_token = header[1]
        if header[0].lower() == "x-storage-url":
            storage_url = header[1]

    authconn.close()
    return (auth, storage_token, storage_url)


def perform_reauth():
    global auth
    global storage_token
    global storage_url
    auth, storage_token, storage_url = perform_auth(auth_server,
        auth_port, auth_acct, auth_user, auth_pass)


def head_Object(url, port, storage_token, acct, container, objname):
    conn = getConnection(url, port)
    conn.request("HEAD", "/%s/%s/%s" % (acct, container, objname), "",
        {"X-Auth-Token": storage_token})
    response = conn.getresponse()
    head = response.getheaders()
    status = response.status
    data = response.read()
    conn.close()
    if status == 401:
        perform_reauth()
        conn = getConnection(url, port)
        # Head an Object
        conn.request("HEAD", "/%s/%s/%s" % (acct, container, objname), "",
            {"X-Auth-Token": storage_token})
        response = conn.getresponse()
        head = response.getheaders()
        status = response.status
        data = response.read()
        conn.close()

    return status, head, data


def get_Object(url, port, storage_token, acct, container, objname):
    conn = getConnection(url, port)
    # Get an Object
    conn.request("GET", "/%s/%s/%s" % (acct, container, objname), "",
        {"X-Auth-Token": storage_token})
    response = conn.getresponse()
    header = response.getheaders()
    status = response.status
    data = response.read()
    conn.close()
    if status == 401:
        perform_reauth()
        conn = getConnection(url, port)
        # Get an Object
        conn.request("GET", "/%s/%s/%s" % (acct, container, objname), "",
            {"X-Auth-Token": storage_token})
        response = conn.getresponse()
        header = response.getheaders()
        status = response.status
        data = response.read()
        conn.close()
    return status, header, data


def display(duration, rcode, headers, body):
    print "Time: %s" % duration
    print "Response Code: %s" % rcode
    print "Headers: "
    print " "
    print headers
    print " "
    for header in headers:
        print "%s : %s" % (header[0], header[1])
    print "Body:\n%s " % body


def getConnection(url, port):
    if storage_https is True:
        return httplib.HTTPSConnection(url, port)
    else:
        return httplib.HTTPConnection(url, port)


def isValidObject(target):
    (scheme, netloc, path, params, query, frag) = urlparse(storage_url)
    match = re.match('([a-zA-Z0-9\-\.]+):?([0-9]{2,5})?', netloc)
    if match:
        (host, port) = match.groups()
    else:
        raise InvalidUrl('Invalid host and/or port: %s' % netloc)

    spath = path.strip('/')
    account = spath.split('/')[1]
    status, head, data = head_Object(host, storage_url_port,
        storage_token, spath, target['CONTAINER'], target['OBJECT'])
    if status != 200:
        return False
    else:
        return True


def get_swift_object_headers(target):
    (scheme, netloc, path, params, query, frag) = urlparse(storage_url)
    print netloc
    match = re.match('([a-zA-Z0-9\-\.]+):?([0-9]{2,5})?', netloc)
    if match:
        (host, port) = match.groups()
    else:
        raise InvalidUrl('Invalid host and/or port: %s' % netloc)
    spath = path.strip('/')
    account = spath.split('/')[1]
    tduration, status, headers, data = head_Object(host, storage_url_port,
        storage_token, spath, target['CONTAINER'], target['OBJECT'])
    return status, headers, data


def get_swift_object(target):
    (scheme, netloc, path, params, query, frag) = urlparse(storage_url)
    match = re.match('([a-zA-Z0-9\-\.]+):?([0-9]{2,5})?', netloc)
    if match:
        (host, port) = match.groups()
    else:
        raise InvalidUrl('Invalid host and/or port: %s' % netloc)
    spath = path.strip('/')
    account = spath.split('/')[1]
    status, header, data = get_Object(host, storage_url_port,
        storage_token, spath, target['CONTAINER'], target['OBJECT'])
    return status, header, data


def cache_set(target, headers, data, timeout):
    #TODO time based on last modified
    key = "%s/%s" % (target['CONTAINER'], target['OBJECT'])
    payload = [headers, data]
    mc.set(str(hashlib.sha1(key).hexdigest()),
            cPickle.dumps(payload, 2), time=timeout)


def cache_check(target):
    key = "%s/%s" % (target['CONTAINER'], target['OBJECT'])
    if mc.get(str(hashlib.sha1(key).hexdigest())) is not None:
        return True
    else:
        return False


def cache_get(target):
    key = "%s/%s" % (target['CONTAINER'], target['OBJECT'])
    return mc.get(str(hashlib.sha1(key).hexdigest()))


def swift_get_mc(env, start_response):
    uri = env['PATH_INFO'].strip('/').split('/', 1)
    try:
        target = {'CONTAINER': uri[0], 'OBJECT': uri[1]}
    except IndexError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    cached = cache_get(target)
    if cached is not None:
        payload = cPickle.loads(cached)
        status = 200
        if status is 200:
            start_response('200 OK', payload[0])
            return [payload[1]]
        else:
            start_response('500 Internal Error',
                [('Content-Type', 'text/plain')])
            return ['Got %s status during cache headers GET' % status]
    else:
        if isValidObject(target):
            status, headers, data = get_swift_object(target)
            if status is 200:
                start_response('200 OK', headers)
                print "Valid Object Requested. Entering into cache."
                #TODO: set cache timeout properly
                if not cache_check(target):
                    cache_set(target, headers, data, cache_ttl)
                else:
                    print "cache set stampede, hot file"
                return [data]
            else:
                start_response('500 Internal Error',
                    [('Content-Type', 'text/plain')])
                return ['Got %s status during GET' % status]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['Not Found\r\n']


def swift_get(env, start_response):
    uri = env['PATH_INFO'].strip('/').split('/', 1)
    try:
        target = {'CONTAINER': uri[0], 'OBJECT': uri[1]}
    except IndexError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    if isValidObject(target):
        status, headers, data = get_swift_object(target)
        if status is 200:
            start_response('200 OK', headers)
            return [data]
        else:
            start_response('500 Internal Error',
                [('Content-Type', 'text/plain')])
            return ['Got %s status during GET' % status]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']


def main():
    usage = "usage: %prog [-C /path/to.conf]"
    p = optparse.OptionParser(usage)
    p.add_option('--config', '-C', default="swift-tunnel.conf",
        help="path to config file. (Default: ./swift-tunnel.conf)")
    p.add_option('--cache', action="store_true",
        help="enable cache, overrides config")
    options, arguments = p.parse_args()

    if path.exists(options.config) is True:
        config = ConfigObj(options.config)
        setconfig(config)
    else:
        print "Config file not found: %s" % options.config
        sys.exit(2)

    global auth
    global storage_token
    global storage_url
    bind_addr = ('0.0.0.0', listen_port)
    setup_mc()
    auth, storage_token, storage_url = perform_auth(auth_server, auth_port,
        auth_acct, auth_user, auth_pass)

    #threading courtesy of openstack swift via
    #swift/trunk/swift/common/wsgi.py
    try:
        os.setsid()
    except OSError:
        no_cover = True     # pass
    sock = None
    retry_until = time.time() + 30
    while not sock and time.time() < retry_until:
        try:
            sock = listen(bind_addr)
        except socket.error, err:
            if err.args[0] != errno.EADDRINUSE:
                raise
            sleep(0.1)
    if not sock:
        raise Exception('Could not bind to %s:%s after trying for 30 seconds' %
                        bind_addr)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # in my experience, sockets can hang around forever without keepalive
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 600)
    worker_count = workers

    def run_server():
        wsgi.HttpProtocol.default_request_version = "HTTP/1.0"
        eventlet.hubs.use_hub('poll')
        pool = GreenPool(size=1024)
        try:
            if use_cache is True or options.cache is True:
                print "Cache enabled, memcache better buckle up."
                wsgi.server(sock, swift_get_mc, custom_pool=pool)
            else:
                wsgi.server(sock, swift_get, custom_pool=pool)

        except socket.error, err:
            if err[0] != errno.EINVAL:
                raise
        pool.waitall()

    def kill_children(*args):
        """Kills the entire process group."""
        print('SIGTERM received')
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        running[0] = False
        os.killpg(0, signal.SIGTERM)

    def hup(*args):
        """Shuts down the server, but allows running requests to complete"""
        print('SIGHUP received')
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        running[0] = False

    running = [True]
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGHUP, hup)
    children = []
    while running[0]:
        while len(children) < worker_count:
            pid = os.fork()
            if pid == 0:
                signal.signal(signal.SIGHUP, signal.SIG_DFL)
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
                run_server()
                print('Child %d exiting normally' % os.getpid())
                return
            else:
                print('Started child %s' % pid)
                children.append(pid)
        try:
            pid, status = os.wait()
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                print('Removing dead child %s' % pid)
                children.remove(pid)
        except OSError, err:
            if err.errno not in (errno.EINTR, errno.ECHILD):
                raise
    greenio.shutdown_safe(sock)
    sock.close()
    print('Exited')


if __name__ == '__main__':
    main()


# vim:set ai ts=4 sw=4 tw=0 expandtab:
