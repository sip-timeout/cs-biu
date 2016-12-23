from packet import Packet
from socket_manager import SocketManager

import time

pack = Packet(23)
pack.set_payload('dog')

mgr = SocketManager()
mgr.connect('localhost')

mgr.send_packet(pack)
work = True
while work:
    if mgr.is_packet_available():
        ack = mgr.get_packet()
        if ack:
            if ack.is_valid:
                work = False
            else:
                print 'bad packet, resend'
                mgr.send_packet(pack)
    else:
        print 'No answer from client, keep waiting'

print 'finished sending!'
mgr.disconnect()


print 'Finished!'
