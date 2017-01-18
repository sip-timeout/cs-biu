# Oded Golreich 301840476

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


mgr = SocketManager()
mgr.connect(sys.argv[1])
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
