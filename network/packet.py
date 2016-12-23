import struct
from crc import compute
from crc import check
from consts import Consts


class Packet:
    def __init__(self, seq_num,is_ack = False,is_valid = True):
        self.seq_num = seq_num
        self.is_ack = is_ack
        self.is_valid = is_valid
        self.data_length = 0

    @classmethod
    def from_bytes(cls, pack_bytes,include_payload= True):
        crc_header = bin(ord(list(pack_bytes)[0])).zfill(10).replace('0b', '')
        crc_header_input_string = cls.__get_crc_input_string__(pack_bytes[2:Consts.HEADER_SIZE])

        if not check(crc_header_input_string,crc_header):
            return None

        seq_num, is_ack, is_valid, data_length = struct.unpack('=i??i', pack_bytes[2:Consts.HEADER_SIZE])
        packet = cls(seq_num, is_ack, is_valid)
        packet.data_length = data_length

        if data_length and include_payload:
            data = pack_bytes[Consts.HEADER_SIZE:]
            crc_payload = bin(ord(list(pack_bytes)[1])).zfill(10).replace('0b', '')
            crc_payload_input_string = cls.__get_crc_input_string__(data)

            if not check(crc_payload_input_string,crc_payload):
                return None

            packet.payload = data

        return packet


    def set_payload(self,data):
        self.payload = data
        self.data_length = len(data)



    def to_bytes(self):
        crc_payload_byte = struct.pack('B', 0)

        raw_bytes = struct.pack('=i??i',self.seq_num,self.is_ack,self.is_valid,self.data_length)
        crc_header_input_string = self.__get_crc_input_string__(raw_bytes)
        crc_header_code = compute(crc_header_input_string)
        crc_header_byte = struct.pack('B', int(crc_header_code, 2))

        if self.data_length:
            payload_bytes = struct.pack(str(self.data_length) + 's',self.payload)
            crc_payload_input_string = self.__get_crc_input_string__(payload_bytes)
            crc_payload_code = compute(crc_payload_input_string)
            crc_payload_byte = struct.pack('B', int(crc_payload_code, 2))
            raw_bytes += payload_bytes + (Consts.PAYLOAD_SIZE - len(payload_bytes)) * '0'

        return crc_header_byte + crc_payload_byte + raw_bytes

    @classmethod
    def __get_crc_input_string__(self, raw_bytes):
        crc_input_string = ''.join(map(lambda byte: bin(ord(byte)).zfill(10).replace('0b', ''), list(raw_bytes)))
        return crc_input_string










