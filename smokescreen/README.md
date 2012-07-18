### OLD and CRUSTY - you should probably not use me.

    ===================

    Usage: swift-tunnel2.py [-C /path/to.conf]

    Options:
      -h, --help            show this help message and exit
      -C CONFIG, --config=CONFIG
                            path to config file. (Default: ./swift-tunnel.conf)
      --cache               enable cache, overrides config

    ===================

    Sample config:

    [swift-tunnel]

#port we should listen on
    listen_port = 8090

#how many threads/workers should we use
#should not exceed # of proc/cores on system
    workers = 4

#The host and port performing auth
    auth_server = '127.0.0.1'
    auth_port = '11000'
    auth_https = False
#Auth credentials
    auth_acct = 'test'
    auth_user = 'tester'
    auth_pass = 'testpass'

#Port the storage service is using
#its not determined automatically right now
    storage_url_port = 8080
#is the storage service using HTTPS ?
    storage_https = False 

    [ghetto-cache]
#its ghetto, and there is no error handling. Would be better to use nginx proxy cache
    use_cache = False
    memcache_host = 127.0.0.1:11211
#memcache_host = 127.0.0.1:11211, 127.0.0.2:11211, 127.0.0.3:112111
    cache_ttl = 900

