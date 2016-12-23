from packet import Packet
from socket_manager import SocketManager

import time

pack = Packet(23)
pack.set_payload('dog')

mgr = SocketManager()
mgr.connect('localhost')

mgr.send_packet(pack)

print 'finished sending!'
time.sleep(120)
mgr.disconnect()


print 'Finished!'
