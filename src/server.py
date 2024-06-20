import struct
from socket_t import *
from utils import *

SYNC = 0xDCC023C2

class Server:

    def __init__(self,host,port):
        self.host = str(host).strip()
        self.port = int(port)  
        self.id = 0
        self.socket_ = Socket(host,port)
        

    def check_internet_checksum(data):
        checksum = checksum(data)
        return checksum

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
        length = len(data)
        
        # Create header without checksum
        header = struct.pack('!2IHHBB', SYNC, SYNC, 0, length, self.id, flags)
        
        # Calculate checksum with checksum field set to 0
        checksum = self.internet_checksum(header + data)
        
        # Create the full frame with the correct checksum
        header = struct.pack('!2IHHBB', SYNC, SYNC, checksum, length, self.id, flags)
        frame = header + data
        
        return frame

# Example usage
# data = b'\x01\x02\x03\x04'
# frame_id = 0
# frame = create_dccnet_frame(data, frame_id)
# print(frame)

