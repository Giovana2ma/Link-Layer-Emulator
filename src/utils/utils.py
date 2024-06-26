import struct

SYNC = 0xDCC023C2
SYNCRONIZED = struct.pack("!I I",SYNC,SYNC)


FLAG_POSITION   = 14
HEADER_SIZE     = 15
SYNC_SIZE       = 8
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

create_format_string = lambda length: f"{HEADER_FORMAT} {str(length) + 's'}"