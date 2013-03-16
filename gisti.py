#!/usr/bin/env python
import subprocess
import platform
import optparse
import urllib2
import getpass
import sys
import os
try:
    import simplejson as json
except ImportError:
    import json


def getcontent(fname):
    """ read content from file
    :returns: file contents"""
    with open(fname) as f:
        return f.read()


def bauth(user, password):
    """perform basic auth
    :param user: the username
    :param password: the password 
    :returns: string in the format: "Basic THEHASH"
    """
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()


def parse_list(response):
    """Parse a github gist listing .
    :param response: the returned body."""
    try:
        gists = json.loads(response.replace('\n', '\\n'))
        if type(gists) is list:
            for entry in gists:
                print "%s - %s '%s'" % (entry['html_url'],
                    entry['files'].keys(), entry['description'])
        else:
            print "%s - %s '%s'" % (gists['html_url'],
                    gists['files'].keys(), gists['description'])
    except Exception as err:
        print "Error parsing json: %s" % err
        print "=" * 79
        print repr(response)
        print "=" * 79
    return None


def parse_post(response):
    """Parse a github gist posting.
    :param response: the returned body."""
    try:
        gist = json.loads(response.replace('\n', '\\n'))
        print "Posted to %s" % gist['html_url']
        if platform.system() == 'Darwin':
            os.system('echo "%s" | pbcopy' % gist['html_url'])
        print "Git pull: %s" % gist['git_pull_url']
        print "Git push: %s" % gist['git_push_url']
    except Exception as err:
        print "Error parsing json: %s" % err
        print "=" * 79
        print repr(response)
        print "=" * 79


def gist_list(user, password=None, gid=None):
    """Peform a gist listing
    :param user: github user name for auth.
    :param password: github user password.
    :param gid: gist id to retrieve or None for all"""
    if gid is None:
        if user is not None:
            url = "https://api.github.com/users/%s/gists" % user
        else:
            print "Couldn't find your github username."
            sys.exit(1)
    else:
        url = "https://api.github.com/gists/%s" % gid

    if user is not None and password is not None:
        req = urllib2.Request(url, headers = {
            'Authorization': bauth(user, password),
            'Accept': '*/*',
            'User-Agent': 'gistipy/1'})
    else:
        req = urllib2.Request(url, headers = {
            'Accept': '*/*',
            'User-Agent': 'gistipy/1'})
    try:
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        parse_list(response)
    except Exception as err:
        print "Error getting gist(s): %s" % err


def gist_post(fname, public=True, user=None, password=None):
    """
    Post a anonymous, public or private gist to github. 
    {
      "description": "the description for this gist",
      "public": true,
      "files": {
        "file1.txt": {
          "content": "String file contents"
        }
      }
    }
    :param fname: The gist filename.
    :param public: Whether this gist is public (True) or private (False)
    :param user: github user
    :param password: github password
    """
    if fname is sys.stdin:
        content = fname.read()
        fname = 'stdin'
    else:
        content = getcontent(fname)
    url = "https://api.github.com/gists"
    gist = {}
    gist['description'] = fname
    gist['public'] = public
    gist['files'] = {fname: {'content': content}}
    data = json.dumps(gist)
    if user is not None and password is not None:
        req = urllib2.Request(url, data=data, headers = {
            'Authorization': bauth(user, password),
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'gistipy/1'})
        print "Posting gist as %s" % user
    else:
        req = urllib2.Request(url, data=data, headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'gistipy/1'})
        print "Posting anonymous gist..."
    try:
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        parse_post(response)
    except Exception as err:
        print "Error posting gist: %s" % err


def get_gh_user():
    cmd = ['git', 'config', '--get', 'github.user']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    user = run.stdout.readline().strip()
    if user:
        return user
    else:
        try:
            return os.environ['GITHUB_USER']
        except KeyError:
            return None


def get_gh_pass():
    cmd = ['git', 'config', '--get', 'github.password']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    password = run.stdout.readline().strip()
    if password:
        return password
    else:
        try:
            return os.environ['GITHUB_PASSWORD']
        except KeyError:
            return None


def main():
    print "=" * 79
    usage = '''
    usage: %prog [-v] [-p|--private] [-l|--list] [gist.file]
    '''
    args = optparse.OptionParser(usage)
    args.add_option('--verbose', '-v', action="store_true",
        help="Print verbose info")
    args.add_option('--private', '-p', action="store_true",
        help="post private gist")
    args.add_option('--anonymous', '-a', action="store_true",
        help="post an anonymous git")
    args.add_option('--list', '-l', action="store_true",
        help="list gists, use with -a to list only your public gists")
    options, arguments = args.parse_args()

    if options.private:
        public = False
    else:
        public = True

    if not options.anonymous:
        ghuser = get_gh_user()
        ghpass = get_gh_pass()
        if not ghuser:
            ghuser = raw_input("Enter your github username: ")
            if len(ghuser) is 0:
                print "Aborting..."
                sys.exit(1)
        if not ghpass:
            ghpass = getpass.getpass("Enter password for %s@github.com: " % \
                ghuser)
    else:
        ghuser = None
        ghpass = None

    if options.list:
        ghuser = get_gh_user()
        gist_list(user=ghuser, password=ghpass)
        sys.exit(0)

    if not arguments:
        gist_post(sys.stdin, public=public, user=ghuser, password=ghpass)
    else:
        for fname in arguments:
            if os.path.isfile(fname):
                gist_post(fname, public=public, user=ghuser, password=ghpass)
            else:
                cmd = '%s ./%s' % (os.environ.get('EDITOR', 'vim'), fname)
                os.system(cmd)
                if os.path.isfile(fname):
                    sendit = raw_input("Post %s as gist? (y/n)[y]: " % fname)
                    if sendit == "y" or sendit == "yes" or len(sendit) is 0:
                        gist_post(fname, public=public,
                                user=ghuser, password=ghpass)
                else:
                    print "Did not post %s as gist." % fname


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\n'
