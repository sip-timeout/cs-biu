import socket
import select

from consts import Consts
from packet import Packet


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
        packet = Packet.from_bytes(header_bytes,False)
        if not packet:
            if expect_payload:
                # clean payload bytes in case of bad header
                self.__get_bytes__(Consts.PAYLOAD_SIZE)
        elif packet.data_length>0:
            payload_bytes = self.__get_bytes__(packet.data_length)
            packet_with_data = Packet.from_bytes(header_bytes+payload_bytes)
            if packet_with_data:
                packet = packet_with_data
            else:
                packet.is_valid = False
        return packet

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