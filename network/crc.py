from consts import Consts


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