import struct
from socket_t   import *
from utils      import *

class NetworkInterface:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.id = 0
        self.socket_ = Socket(host,port)
    
    def create_dccnet_frame(self,data,id=None,flags=0):
        """
        Create a DCCNET frame with the given data, frame ID, and flags.
        
        Args:
        data (bytes): The data to be included in the frame.
        frame_id (int): The frame identifier (0 or 1).
        flags (int): Control flags (default is 0).
        
        Returns:
        bytes: The constructed DCCNET frame.
        """
        
        # Firstly, encode the data as bytes 
        data_encoded = bytes(data + "\n", encoding="ascii")
        length = len(data_encoded)

        # The packet format depends on data
        format_string = f"{HEADER_FORMAT} {str(length) + 's'}"

        if(id == None):
            id = self.id

        # Create header without checksum
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flags,data_encoded)
        
        # Calculate checksum with checksum field set to 0
        cs = checksum(frame)
        
        # Create the full frame with the correct checksum
        frame = struct.pack(format_string, SYNC, SYNC, cs, length, id, flags, data_encoded)
        
        return frame
    
    def unpack_dccnet_frame(self,response):
        header  = response[:HEADER_SIZE]
        data    = response[HEADER_SIZE:]

        _,_,cs,length,id,flags = struct.unpack(HEADER_FORMAT,header)

        return cs,length,id,flags,data
