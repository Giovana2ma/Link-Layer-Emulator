import struct
from utils      import *


class Frame:
    def __init__(self, binary = None):
        if(binary != None):
            cs,length,id,flag,data = self.unpack_dccnet_frame(binary)
    
    @staticmethod
    def create_dccnet_frame(data,id=0,flag=0):
        """
        Create a DCCNET frame with the given data, frame ID, and flag.
        
        Args:
        data (bytes): The data to be included in the frame.
        frame_id (int): The frame identifier (0 or 1).
        flag (int): Control flag (default is 0).
        
        Returns:
        bytes: The constructed DCCNET frame.
        """
        
        # Firstly, encode the data as bytes 
        data_encoded = bytes(data, encoding="ascii")
        length = len(data_encoded)

        # The packet format depends on data
        format_string = create_format_string(length)

        # Create header without checksum
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flag,data_encoded)
        
        # Calculate checksum with checksum field set to 0
        cs = checksum(frame)
        
        # Create the full frame with the correct checksum
        frame = struct.pack(format_string, SYNC, SYNC, cs, length, id, flag, data_encoded)
        
        return frame
    
    @staticmethod
    def unpack_dccnet_frame(response):
        header  = response[:HEADER_SIZE]
        data    = response[HEADER_SIZE:].decode("ascii")

        _,_,cs,length,id,flag = struct.unpack(HEADER_FORMAT,header)

        return cs,length,id,flag,data
    
    @staticmethod
    def is_checksum_valid(frame):
        cs,length,id,flag,data = Frame.unpack_dccnet_frame(frame)
        
        format_string = create_format_string(length)
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flag,bytes(data + "\n", encoding="ascii"))

        return cs == checksum(frame)
    
    @staticmethod
    def get_id(frame):
        cs,length,id,flag,data = Frame.unpack_dccnet_frame(frame)
        return id
    
    @staticmethod
    def get_flag(frame):
        cs,length,id,flag,data = Frame.unpack_dccnet_frame(frame)
        return flag