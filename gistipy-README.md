## Quick and dirty script to post gist to github. Target can either be an existing file or we'll launch vim. If you're on OSX the gist url will be copyied automatically to your clipboard.

If you don't want to be prompted for your username make sure you either set the environmental variable:

    export GITHUB_USER=bob

Or add it to your git config:

    [github]
        user = bob

Althought not recommended you can also set your password in a similar fashion to skip password prompts.

Usage:

    fhines@argos:~$ python gisti.py -h
    ===============================================================================
    Usage: 
        usage: gisti.py [-v] [-p|--private] [-l|--list] gist.file
        

    Options:
      -h, --help       show this help message and exit
      -v, --verbose    Print verbose info
      -p, --private    post private gist
      -a, --anonymous  post an anonymous git
      -l, --list       list gists, use with -a to list only your public gists

Post the file test.py as a private gist:

    fhines@argos:~$ python gisti.py -p test.py 
    ===============================================================================
    Enter password for pandemicsyn@github.com: 
    Posting gist as pandemicsyn
    Posted to https://gist.github.com/62775765217def1facdd
    Git pull: git://gist.github.com/62775765217def1facdd.git
    Git push: git@gist.github.com:62775765217def1facdd.git

Create and then post a file called test.txt:

    fhines@argos:~$ python gisti.py test.py 
    ===============================================================================
    Enter password for pandemicsyn@github.com: 
    Launching vim...
    Are you sure you wish to post test.py? (y/n)[y]: y
    Posting gist as pandemicsyn
    Posted to https://gist.github.com/62775765217def1facdd
    Git pull: git://gist.github.com/62775765217def1facdd.git
    Git push: git@gist.github.com:62775765217def1facdd.git

Post an anonymous gist:

    fhines@argos:~$ python gisti.py -a test.py 
    ===============================================================================
    Posting anonymous gist
    Posted to https://gist.github.com/62775765217def1facdd
    Git pull: git://gist.github.com/62775765217def1facdd.git
    Git push: git@gist.github.com:62775765217def1facdd.git

List your gists:

    fhines@argos:~$ python gisti.py -l
    ===============================================================================
    Enter password for pandemicsyn@github.com: 
    https://gist.github.com/e64a7d5a8562cc92aa14 - [u'graphiteinstall.txt'] 'install graphite'
    https://gist.github.com/1396977 - [u'proxymemuse.py'] 'proxy mem use monitor'
    https://gist.github.com/1174389 - [u'rfind.py'] 'redbo's rfind'
    https://gist.github.com/933647 - [u'gistfile1.txt'] 'Openstack Swift /healthcheck'
    https://gist.github.com/871bd9909ef10561f2c7 - [u'pyiops'] 'script to interact with blkio goodness'
    https://gist.github.com/491763 - [u'zenoss-growlalert.py'] 'None'
    https://gist.github.com/477433 - [u'posterous-media-post.py'] 'posting media to posterous using python and pycurl'
    https://gist.github.com/477426 - [u'check-memcache.py'] 'None'

List your gists without authenticating (i.e. only your public gists):

    fhines@argos:~$ python gisti.py -l -a
    ===============================================================================
    https://gist.github.com/1396977 - [u'proxymemuse.py'] 'proxy mem use monitor'
    https://gist.github.com/1174389 - [u'rfind.py'] 'redbo's rfind'
    https://gist.github.com/933647 - [u'gistfile1.txt'] 'Openstack Swift /healthcheck'
    https://gist.github.com/491763 - [u'zenoss-growlalert.py'] 'None'
    https://gist.github.com/477433 - [u'posterous-media-post.py'] 'posting media to posterous using python and pycurl'
    https://gist.github.com/477426 - [u'check-memcache.py'] 'None'
