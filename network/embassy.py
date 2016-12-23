from packet import Packet
from socket_manager import SocketManager

import time

mgr = SocketManager()
mgr.connect('localhost')

pack = mgr.get_packet()

if pack == None:
    print 'Packet Fucked'

mgr.disconnect()


print 'Finished!'
