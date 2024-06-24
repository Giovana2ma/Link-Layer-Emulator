import struct
from socket_t   import *
from utils      import *

class NetworkInterface:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.id = 0
        self.socket = Socket(host,port)

        self.last_received_frame = None
    
    def create_dccnet_frame(self,data,flags=0):
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


        # Create header without checksum
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, self.id, flags,data_encoded)
        
        # Calculate checksum with checksum field set to 0
        cs = checksum(frame)
        
        # Create the full frame with the correct checksum
        frame = struct.pack(format_string, SYNC, SYNC, cs, length, self.id, flags, data_encoded)
        
        return frame
    
    def unpack_dccnet_frame(self,response):
        header  = response[:HEADER_SIZE]
        data    = response[HEADER_SIZE:]

        _,_,cs,length,id,flags = struct.unpack(HEADER_FORMAT,header)

        return cs,length,id,flags,data

    
    def is_acceptable(self,frame):
        # A frame can only be accepted if 
        # (1) it is an acknowledgement frame for the last transmitted frame;
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        # (3) a retransmission of the last received frame;
        # (4) or a reset frame.
        _,_,id,flag,_ = self.unpack_dccnet_frame(frame)

        if((flag == ACK) and (id == self.id)):
            return True
        
        if((flag == RST) and id == RST_ID):
            return True
        
        if((flag != ACK) and id != self.id):
            return True
        
        if(self.last_received_frame == frame):
            return True

        return False
    
    def transmit(self,data,flags=0):
        frame = self.create_dccnet_frame(data,flags)
        n=16

        while(n>0):
            recv = self.socket.send(frame)

            if(self.is_acceptable(recv)): break
            n -= 1
        return recv



