#!/usr/bin/env

import os

def proccount():
    if hasattr(os, 'sysconf'):
        if 'SC_NPROCESSORS_ONLN' in os.sysconf_names.keys():
            return os.sysconf("SC_NPROCESSORS_ONLN")
        else:
            return None

print "Found %s active procs/cores" % proccount()
