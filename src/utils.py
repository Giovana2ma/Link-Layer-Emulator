SYNC = 0xDCC023C2
HEADER_SIZE = 15

HEADER_FORMAT = '!I I H H H B'


def checksum(data):
        """
        Calculate the Internet checksum of the given data.
        """
        checksum = 0
        # Handle complete 16-bit blocks
        for i in range(0, len(data) - len(data) % 2, 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
            checksum = (checksum & 0xffff) + (checksum >> 16)
        # Handle remaining byte, if any
        if len(data) % 2:
            checksum += data[-1] << 8
            checksum = (checksum & 0xffff) + (checksum >> 16)
        # One's complement
        checksum = ~checksum & 0xffff
        return checksum