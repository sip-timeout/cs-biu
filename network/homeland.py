from consts import Consts
from packet import Packet
from socket_manager import SocketManager
from window_sender import WindowSender
import sys

seq_num = 1
packets = []
with open('input.txt','rb') as sent_file:
    while True:
        pack_bytes = sent_file.read(Consts.PAYLOAD_SIZE)
        if pack_bytes != '':
            packet = Packet(seq_num)
            packet.set_payload(pack_bytes)
            packets.append(packet)
            seq_num += 1
        else:
            break

packets[-1].set_final()

mgr = SocketManager()
mgr.connect(sys.argv[1])

sender = WindowSender(Consts.WINDOW_SIZE, packets, mgr)
sender.send_packets()

mgr.disconnect()


print 'Finished!'
