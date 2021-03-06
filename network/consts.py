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
    GLOBAL_TIMEOUT = 10
    FINALIZE_TIMEOUT = 5
    END_SEQ_NUM = 300
    FINALIZE_PCTG = 0.7
