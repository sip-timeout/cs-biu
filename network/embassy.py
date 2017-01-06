from packet import Packet
from socket_manager import SocketManager
from consts import Consts

mgr = SocketManager()
mgr.connect('localhost')
print 'Connection Established'

file_packets = {}


def got_all_packets():
    if final_seq > 0:
        for i in range(1, final_seq+1):
            if i not in file_packets:
                return False
        return True
    else:
        return False


work = True
final_seq = -1
while work:
    pack , seq_num = mgr.get_packet()
    if pack:
        if pack.seq_num not in file_packets:
            response = Packet(pack.seq_num, True, pack.is_valid)
            mgr.send_packet(response)
            if pack.is_valid:
                print 'Received valid pack ' + str(pack.seq_num)
                file_packets[pack.seq_num] = pack.payload
                if pack.is_final:
                    final_seq = pack.seq_num
                if got_all_packets():
                    for i in range(0,3):
                        mgr.send_packet(Packet(Consts.END_SEQ_NUM,True,True))
                    work = False
            else:
                print 'Received invalid pack with bad data ' + str(pack.seq_num) + ', sent bad ack'
        else:
            mgr.send_packet(Packet(pack.seq_num,True,True))
    else:
        print 'Received pack with bad header ' + str(seq_num) + ', asking again'
        mgr.send_packet(Packet(seq_num,True,False))

mgr.disconnect()

file_bytes = []
sorted_keys = file_packets.keys()
sorted_keys.sort()
for key in sorted_keys:
    file_bytes+= file_packets[key]

with open('output.txt', 'wb') as out_file:
    out_file.write(''.join(file_bytes))

print 'Finished!'
