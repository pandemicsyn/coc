#!/usr/bin/python
import os
def get_quarantine_count():
    """get obj/container/account quarantine counts"""
    qcounts = {"objects": 0, "containers": 0, "accounts": 0}
    qdir = "quarantined"
    for device in os.listdir("/srv/node"):
        for qtype in qcounts:
            qtgt = os.path.join("/srv/node", device, qdir, qtype)
            if os.path.exists(qtgt):
                linkcount = os.lstat(qtgt).st_nlink
                if linkcount > 2:
                    qcounts[qtype] += linkcount - 2
        if sum(qcounts.values()) is not 0:
            print "%s: %s" % (device, qcounts)
            qcounts = {"objects": 0, "containers": 0, "accounts": 0}
    #return qcounts
    
get_quarantine_count()
