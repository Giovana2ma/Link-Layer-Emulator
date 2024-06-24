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
    
    def transmit(self,data,flags=0):
        frame   = self.create_dccnet_frame(data,flags)

        recv,n    = None,16
        while(n and not self.is_acceptable(recv)):
            recv = self.socket.send(frame)
            n -= 1
        
        self.last_received_frame = recv
        return recv
    
    def must_send_ack(self,response):
        #Upon accepting a data frame (cases 2 and), the receiver must respond with an acknowledgement frame.
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        # (3) a retransmission of the last received frame;

        _,_,id,flag,_ = self.unpack_dccnet_frame(response)
        if(not self.is_acceptable(response)): return False
        if(flag == ACK): return False
        if(flag == RST): return False
        return True
    
    def send_ack(self,response):
        if(not self.must_send_ack(response)): return None
        return self.transmit("",flags=ACK)


    def is_acceptable(self,frame):
        # A frame can only be accepted if (Checksum IS VALID)
        if(frame == None): return False
        if(not self.is_checksum_valid(frame)): return False

        cs,length,id,flag,data = self.unpack_dccnet_frame(frame)

        # (1) it is an acknowledgement frame for the last transmitted frame;
        if((flag == ACK) and (id == self.id)):  return True
        # (4) or a reset frame.
        if((flag == RST) and (id == RST_ID)):   return True
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        if((flag != ACK) and (id != self.id)):  return True
        # (3) a retransmission of the last received frame;
        if(self.last_received_frame == frame):  return True

        return False
    
    @staticmethod
    def unpack_dccnet_frame(response):
        header  = response[:HEADER_SIZE]
        data    = response[HEADER_SIZE:]

        _,_,cs,length,id,flag = struct.unpack(HEADER_FORMAT,header)

        return cs,length,id,flag,data

    @staticmethod
    def is_checksum_valid(frame):
        cs,length,id,flags,data = NetworkInterface.unpack_dccnet_frame(frame)
        
        format_string = f"{HEADER_FORMAT} {str(length) + 's'}"
        frame = struct.pack(format_string, SYNC, SYNC, 0, length, id, flags,data)

        return cs == checksum(frame)