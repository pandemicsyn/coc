from eventlet.green import socket
from eventlet import sleep
from datetime import datetime

def send_event(payload):
    addr = ('127.0.0.1', 8125)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(payload, addr)

transform_test = 'te$t_key !fix{\)\/?@#%th\'is^&*be"ok'
good_events = ['testitem:1|c', 'testitem:1|c|@0.5']
crap_events = ['.', ' ', ':', ' : |c', 'baditem:1|k', 'baditem:1|c|@',
    'baditem:1|c|@wtf', 'baditem:1|c|@05f.6']

print "--> %s" % datetime.now()
for event in good_events:
    print "Sending [%s]" % event
    send_event(event)
    sleep(.5)
for event in crap_events:
    print "Sending crap [%s]" % event
    send_event(event)
    sleep(.5)
print "Sending transform [%s]" % transform_test
send_event(transform_test)
