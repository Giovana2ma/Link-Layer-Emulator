
SYNC = 0xDCC023C2


ID_POSITION     = 14
FLAG_POSITION   = 15
HEADER_SIZE     = 15
HEADER_FORMAT   = '!I I H H H B'

ACK = 0x80
END = 0x40
RST = 0x20 

RST_ID          = 0xFFFF


def checksum(data):
        """
        Calculate the Internet checksum of the given data.
        """
        cs = 0
        # Handle complete 16-bit blocks
        for i in range(0, len(data) - len(data) % 2, 2):
            word = (data[i] << 8) + data[i + 1]
            cs += word
            cs = (cs & 0xffff) + (cs >> 16)
        # Handle remaining byte, if any
        if len(data) % 2:
            cs += data[-1] << 8
            cs = (cs & 0xffff) + (cs >> 16)
        # One's complement
        cs = ~cs & 0xffff
        return cs