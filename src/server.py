from NetworkInterface import *

class Server:
    def __init__(self,host,port):
        super().__init__(host,port)

    def check_internet_checksum(frame):
        cs,length,id,flags,data = self.unpack_dccnet_frame(frame)
        
        format_string = f"{HEADER_FORMAT} {str(length) + 's'}"
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flags,data)

        return cs == checksum(frame)