from packet import Packet
from socket_manager import SocketManager
from consts import Consts

import  time

mgr = SocketManager()
mgr.connect('localhost')
print 'Connection Established'

file_packets = {}
work = True
while work:
    pack = mgr.get_packet()
    time.sleep(5)
    if pack:
        response = Packet(pack.seq_num,True,pack.is_valid)
        mgr.send_packet(response)
        if pack.is_valid:
            file_packets[pack.seq_num] = pack.data_length
            if pack.data_length < Consts.PAYLOAD_SIZE:
                work = False

mgr.disconnect()
print 'Finished!'
