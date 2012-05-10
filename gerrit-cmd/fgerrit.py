#!/usr/bin/env python

#http://gerrit-documentation.googlecode.com/svn/Documentation/2.2.2/cmd-query.html

import envoy
import simplejson as json

class FGerrit(object):

    def __init__(self, ssh_port=29418, host="review.openstack.org",
                 status="open", project="openstack/swift"):
        self.ssh_port = ssh_port
        self.host = host
        self.status = status
        self.project = project

    def list_reviews(self):
        sshcmd = "ssh -p %d %s gerrit query --format=JSON status:%s project:%s" % \
                (self.ssh_port, self.host, self.status, self.project)
        r = envoy.run(sshcmd)
        if r.status_code == 0:
            cleaned = r.std_out.strip().split('\n')
            reviews = []
            for line in cleaned:
                reviews.append(json.loads(line))
            return [x for x in reviews if 'status' in x]
        else:
            raise Exception('Error obtaining reviews from Gerrit')

    def get_review(self, review_id, comment=False):
        """Either a short id (5264) or long hash"""
        if comments:
            sshcmd = "ssh -p %d %s gerrit query --format=JSON %s --comments" % \
                        (self.ssh_port, self.host, review_id)
        else:
            sshcmd = "ssh -p %d %s gerrit query --format=JSON %s" % \
                        (self.ssh_port, self.host, review_id)
        r = envoy.run(sshcmd)
        if r.status_code == 0:
            cleaned = r.std_out.strip().split('\n')
            reviews = []
            for line in cleaned:
                reviews.append(json.loads(line))
            return [x for x in reviews if 'status' in x]
        else:
            raise Exception('Error obtaining reviews from Gerrit')

    def print_reviews(reviews):
        for r in reviews:
            print "%s - %s (%s) - %s - %s" % (r['subject'], r['owner']['name'],
                                              r['owner']['username'], r['url'],
                                              r['lastUpdated'])

    
