from consts import Consts
import time


class WindowSender:
    def __init__(self, window_size, packets, socket_mgr):
        self.pending_packets = packets
        self.window = dict()
        self.cur_pack = 0
        self.socket_mgr = socket_mgr

        for i in range(0, window_size):
            packet_val = self.get_next_packet()
            self.window[packet_val['packet'].seq_num] = packet_val

    def get_next_packet(self):
        if self.cur_pack < len(self.pending_packets):
            packet_val = dict()
            packet_val['packet'] = self.pending_packets[self.cur_pack]
            packet_val['send_time'] = 0
            self.cur_pack += 1
            return packet_val
        else:
            return None

    def send_packets(self):
        while len(self.window) > 0:
            for seq in self.window:
                pack = self.window[seq]
                if time.time() - pack['send_time'] > Consts.PACKET_TIMEOUT:
                    self.socket_mgr.send_packet(pack['packet'])
                    print 'Timeout expired, sending packet '+ str(pack['packet'].seq_num)
                    pack['send_time'] = time.time()
            while self.socket_mgr.is_packet_available():
                ack = self.socket_mgr.get_packet(False)
                if ack:
                    packet_to_send = None
                    if ack.is_valid:
                        if ack.seq_num in self.window:
                            self.window.pop(ack.seq_num)
                            next_pack = self.get_next_packet()
                            if next_pack:
                                self.window[next_pack['packet'].seq_num] = next_pack
                                print 'Good ack for ' + str(ack.seq_num) + ' received, sending next packet '+ str(next_pack['packet'].seq_num)
                                packet_to_send = next_pack
                            else:
                                continue
                    else:
                        print 'ack for invalid packet ' + str(ack.seq_num) + ', resend'
                        packet_to_send= self.window[ack.seq_num]

                    packet_to_send['send_time'] = time.time()
                    self.socket_mgr.send_packet(packet_to_send['packet'])
                else:
                    print 'invalid ack received - throwing'

        print 'Finished sending packets'