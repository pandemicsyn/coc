from eventlet.green import socket

def send_event(payload):
    addr = ('127.0.0.1', 8125)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(payload, addr)

send_event("randomtest")
