import struct
from socket_t import *
from utils import *


class Client:
    def __init__(self,host,port,gas):
        self.host = host
        self.port = port
        self.gas = gas
        self.id = 0
        self.socket_ = Socket(host,port)
        
    def create_dccnet_frame(self,data, flags=0):
        """
        Create a DCCNET frame with the given data, frame ID, and flags.
        
        Args:
        data (bytes): The data to be included in the frame.
        frame_id (int): The frame identifier (0 or 1).
        flags (int): Control flags (default is 0).
        
        Returns:
        bytes: The constructed DCCNET frame.
        """
        
        # Frame length does not include header bytes
        data_encoded = bytes(data + "\n", encoding="ascii")
        length = len(data_encoded)
        format_string = f"{HEADER_FORMAT} {str(length) + 's'}"

        # Create header without checksum
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, self.id, flags,data_encoded)
        
        # Calculate checksum with checksum field set to 0
        cs = checksum(frame)
        
        # Create the full frame with the correct checksum
        frame = struct.pack(format_string, SYNC, SYNC, cs, length, self.id, flags, data_encoded)
        
        return frame