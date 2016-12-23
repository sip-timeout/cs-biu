import socket

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

    def is_packet_available(self):
        self.sock

    def get_packet(self):
        header_bytes = self.__get_bytes__(Consts.HEADER_SIZE)
        packet = Packet.from_bytes(header_bytes,False)
        if packet and packet.data_length > 0:
            payload_bytes = self.__get_bytes__(packet.data_length)
            packet = Packet.from_bytes(header_bytes+payload_bytes)
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