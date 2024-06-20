from NetworkInterface import *

class Server:
    def __init__(self,host,port):
        super().__init__(host,port)

    def check_internet_checksum(packet):
        _,length,id,flags,data = self.unpack_dccnet_frame(packet)
        
        format_string = f"{HEADER_FORMAT} {str(length) + 's'}"
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flags,data)

        return checksum(packet) == checksum(frame)