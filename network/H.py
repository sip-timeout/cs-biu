# Oded Golreich 301840476

import time
import sys
import socket
import select
import struct


def compute(binary_str):

    binary_str += '0'*len(Consts.CRC_DIVISOR)
    binary_str = list(binary_str)

    # use divisor from wiki for 8 bit crc
    div = list(Consts.CRC_DIVISOR)

    # implement strictly as seen in wiki
    for i in range(len(binary_str)-len(Consts.CRC_DIVISOR)):
        if binary_str[i] == '1':
            for j in range(len(div)):
                binary_str[i+j] = str((int(binary_str[i+j])+int(div[j]))%2)

    return ''.join(binary_str[-len(Consts.CRC_DIVISOR):])


def check(binary_str,code):
    return compute(binary_str) == code


class Consts:
    HEADER_SIZE = 9
    CRC_DIVISOR = '11010101'
    TCP_HEADER_SIZE = 20
    MTU = 500
    DEAFULT_PORT = 11000
    DEFAILT_RECV_TIMEOUT = 0.07
    MAX_CHUNK_SIZE = 2048
    PAYLOAD_SIZE = MTU - TCP_HEADER_SIZE - HEADER_SIZE
    WINDOW_SIZE = 70
    MAX_PACKET_TIMEOUT = 20
    INIT_PACKET_TIMEOUT = 10
    TIMEOUT_STEP = 2
    GLOBAL_TIMEOUT = 16
    FINALIZE_TIMEOUT = 10
    END_SEQ_NUM = 300
    FINALIZE_PCTG = 0.7


class SocketManager:

    def __init__(self):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port=Consts.DEAFULT_PORT):
        self.sock.connect((host, port))
        self.__get_bytes__(5)

    def disconnect(self):
        self.sock.close()

    def send_packet(self, packet):
        total_sent = 0
        packet_bytes = packet.to_bytes()
        packet_size = len(packet_bytes)
        while total_sent < packet_size:
            sent = self.sock.send(packet_bytes[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def is_packet_available(self,timeout=Consts.DEFAILT_RECV_TIMEOUT):
        ready = select.select([self.sock], [], [], timeout)
        return ready[0]

    def get_packet(self,expect_payload=True):
        header_bytes = self.__get_bytes__(Consts.HEADER_SIZE)
        packet, seq_num = Packet.from_bytes(header_bytes,False)
        if not packet:
            if expect_payload:
                # clean payload bytes in case of bad header
                self.__get_bytes__(Consts.PAYLOAD_SIZE)
        elif packet.data_length>0:
            payload_bytes = self.__get_bytes__(Consts.PAYLOAD_SIZE)
            packet_with_data , seq_num = Packet.from_bytes(header_bytes+payload_bytes[0:packet.data_length])
            if packet_with_data:
                packet = packet_with_data
            else:
                packet.is_valid = False
        return packet, seq_num

    def __get_bytes__(self,bytes_to_get):
        chunks = []
        bytes_recd = 0
        while bytes_recd < bytes_to_get:
            chunk = self.sock.recv(min(bytes_to_get - bytes_recd, Consts.MAX_CHUNK_SIZE))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)


class Packet:
    def __init__(self, seq_num,is_ack = False,is_valid = True):
        self.seq_num = seq_num
        self.is_ack = is_ack
        self.is_valid = is_valid
        self.data_length = 0
        self.is_final = False

    @classmethod
    def from_bytes(cls, pack_bytes,include_payload= True):
        seq_num = struct.unpack('h',pack_bytes[0:2])[0]
        crc_header = bin(ord(list(pack_bytes)[2])).zfill(10).replace('0b', '')
        crc_header_input_string = cls.__get_crc_input_string__(pack_bytes[4:Consts.HEADER_SIZE])

        if not check(crc_header_input_string,crc_header):
            return None, seq_num

        is_ack, is_valid, is_final, data_length = struct.unpack('=???h', pack_bytes[4:Consts.HEADER_SIZE])
        packet = cls(seq_num, is_ack, is_valid)
        packet.set_final(is_final)
        packet.data_length = data_length

        if data_length and include_payload:
            data = pack_bytes[Consts.HEADER_SIZE:]
            crc_payload = bin(ord(list(pack_bytes)[3])).zfill(10).replace('0b', '')
            crc_payload_input_string = cls.__get_crc_input_string__(data)

            if not check(crc_payload_input_string,crc_payload):
                return None, seq_num

            packet.payload = data

        return packet, seq_num


    def set_payload(self, data):
        self.payload = data
        self.data_length = len(data)

    def set_final(self,is_final=True):
        self.is_final = is_final



    def to_bytes(self):

        seq_num_bytes = struct.pack('h', self.seq_num)
        crc_payload_byte = struct.pack('B', 0)

        raw_bytes = struct.pack('=???h',self.is_ack,self.is_valid,self.is_final, self.data_length)
        crc_header_input_string = self.__get_crc_input_string__(raw_bytes)
        crc_header_code = compute(crc_header_input_string)
        crc_header_byte = struct.pack('B', int(crc_header_code, 2))

        if self.data_length:
            payload_bytes = struct.pack(str(self.data_length) + 's',self.payload)
            crc_payload_input_string = self.__get_crc_input_string__(payload_bytes)
            crc_payload_code = compute(crc_payload_input_string)
            crc_payload_byte = struct.pack('B', int(crc_payload_code, 2))
            raw_bytes += payload_bytes + (Consts.PAYLOAD_SIZE - len(payload_bytes)) * '0'

        return seq_num_bytes + crc_header_byte + crc_payload_byte + raw_bytes

    @classmethod
    def __get_crc_input_string__(self, raw_bytes):
        crc_input_string = ''.join(map(lambda byte: bin(ord(byte)).zfill(10).replace('0b', ''), list(raw_bytes)))
        return crc_input_string


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
            if packet_val:
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
                    if time.time() - pack['send_time'] > min(pack['timeout'],self.max_packet_timeout):
                        pack['timeout'] += Consts.TIMEOUT_STEP
                        print 'Timeout expire, setting pack ' + str(pack['packet'].seq_num) + ' timeout to ' + \
                              str(min(pack['timeout'], self.max_packet_timeout)) + ' and sending'
                        self.socket_mgr.send_packet(pack['packet'])
                        pack['send_time'] = time.time()
                        break
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
                                    if not self.finalize_protocol and len(self.window) <= Consts.FINALIZE_PCTG * Consts.WINDOW_SIZE:
                                        print 'Last packet sent, set max timeout to initial'
                                        # for key in self.window:
                                        #     self.window[key]['timeout'] = Consts.FINALIZE_TIMEOUT
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
