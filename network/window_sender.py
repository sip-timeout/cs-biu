from consts import Consts
import time


class WindowSender:
    def __init__(self, window_size, packets, socket_mgr):
        self.pending_packets = packets
        self.window = dict()
        self.cur_pack = 0
        self.socket_mgr = socket_mgr
        self.last_packet_time = time.time()
        self.max_packet_timeout = Consts.MAX_PACKET_TIMEOUT
        self.finalize_protocol = False
        self.global_timeout = 600

        for i in range(0, window_size):
            packet_val = self.get_next_packet()
            self.window[packet_val['packet'].seq_num] = packet_val

    def get_next_packet(self):
        if self.cur_pack < len(self.pending_packets):
            packet_val = dict()
            packet_val['packet'] = self.pending_packets[self.cur_pack]
            packet_val['send_time'] = 0
            packet_val['timeout'] = Consts.INIT_PACKET_TIMEOUT
            self.cur_pack += 1
            return packet_val
        else:
            return None

    def send_packets(self):
        start_time = time.time()
        try:
            while len(self.window) > 0:
                if time.time() - self.last_packet_time > self.global_timeout:
                    print 'Global timeout reached, this means last ack was probably lost and client already exited..'
                    break
                for seq in self.window:
                    pack = self.window[seq]
                    if time.time() - pack['send_time'] > max(pack['timeout'],self.max_packet_timeout):
                        pack['timeout'] += Consts.TIMEOUT_STEP
                        print 'Setting pack ' + str(pack['packet'].seq_num) + ' timeout to ' + str(pack['timeout'])
                        self.socket_mgr.send_packet(pack['packet'])
                        time.sleep(Consts.TIMEOUT_RESEND_GAP)
                        print 'Timeout expired, sending packet '+ str(pack['packet'].seq_num)
                        pack['send_time'] = time.time()
                while self.socket_mgr.is_packet_available():
                    self.last_packet_time = time.time()
                    ack = None
                    try:
                        ack, seq_num = self.socket_mgr.get_packet(False)
                    except RuntimeError:
                        print 'Connection closed on socket end, finishing in '+ str(time.time() - start_time)
                        return

                    if seq_num == Consts.END_SEQ_NUM:
                        print 'Finished sending packets in ' + str(time.time() - start_time) + ' seconds.'
                        return

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
                                    if not self.finalize_protocol:
                                        print 'Last packet sent, set max timeout to initial'
                                        # for key in self.window:
                                        #     self.window[key]['timeout'] = Consts.INIT_PACKET_TIMEOUT
                                        self.max_packet_timeout = Consts.FINALIZE_TIMEOUT
                                        self.finalize_protocol = True
                                        self.global_timeout = Consts.GLOBAL_TIMEOUT
                                    continue
                        else:
                            print 'ack for invalid packet ' + str(ack.seq_num) + ', resend'
                            packet_to_send= self.window[ack.seq_num]

                        if packet_to_send:
                            packet_to_send['send_time'] = time.time()
                            self.socket_mgr.send_packet(packet_to_send['packet'])
                    else:
                        print 'invalid ack received - sending pack ' + str(seq_num) + ' again'
                        if seq_num in self.window:
                            pack = self.window[seq_num]
                            pack['send_time'] = time.time()
                            self.socket_mgr.send_packet(pack['packet'])
        except Exception:
            print 'Transmittion ended by relay'

        print 'Finished sending packets in ' + str(time.time() - start_time) + ' seconds.'
