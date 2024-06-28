import struct
import threading
import hashlib
import time

from utils.socket_t     import *
from utils.utils        import *
from utils.DCCNET_frame import *


class NetworkInterface:
    """
    This class is responsible for the concrete implementation of the DCCNET link layer protocol.
    This emulator handle framing, sequencing, error detection and data retransmission.

    In order to used it, the user most provide the (host,port) pair of the desired server
    In addition to change the function self.process, in order to process the lines in a desired way 

    The main function of this class is run(), that sends packets to the server until a RST, a END or a Error occurs
    """
    def __init__(self,host,port,socket_type="client"):
        self.socket = Socket(host,port,socket_type)

        self.process_line = lambda x: Frame.unpack_dccnet_frame(x)[4]
        self.last_received_frame = None
        self.id   = 0       #last received ack id
        self.send_id = 0    #last sended id                                           
        self.last_id = 1    #last receveid data id

        self.curr = ''

        self.queue = []
        self.running = True
    
    def transmit(self):
        """
        In order to send frames to the server, the frames must first be enqueued. The queue is like a buffer that contains all
        frames that haven´t been acknowledged by it's pairs. The first frame is always enqueue before run() is called
        """
        if(not self.running): return
        if(not self.queue): return

        frame   = self.queue[0]
        self.socket.send(frame)

        print("Enviado: ", Frame.unpack_dccnet_frame(frame))
        return frame
    
    def receive(self):
        """
        The receiver is reponsible for both listening and processing the lines received by the server.
        The receiver only process frames that are acceptable. 
        """
        if(not self.running): return

        try:
            response = self.detect_frame()

            # Some times, the corrupted frames can´t be processed, being discarded
            if(not response): return
            self.treat_response(response)

        except socket.error as e: 
            # This error only triggers if the servers times out and don´t respond the last sended message
            self.send_ack(self.last_received_frame)
            return

        return response

    def treat_response(self,response):
        """
        Once the response is listened by the receiver, it takes different paths depending on what type of frame the response is
        All treated responses are valid responses
        """

        print("Recebido ", Frame.unpack_dccnet_frame(response))

        if(not self.is_acceptable(response)):  return response

        # Valid ACK frames change the current id
        if(Frame.get_flag(response) == ACK):
            self.id ^= 1
            return self.dequeue(response)
        
        # Data frames must the acknowledged and processed
        if(self.is_data_frame(response)):
            self.send_ack(response)
            # Control variables for retransmition and error detection
            self.last_received_frame = response
            self.last_id = Frame.get_id(response)
            # Since frames do not necessarily have a single line, 
            # we have to handle boundary cases
            # self.process_line() generate the expected output for every inpuy
            for m in self.break_in_lines(response):
                self.enqueue(self.process_line(m))
            return self.queue


        # RST and END frames are processed to stop the execution
        if(Frame.get_flag(response) in [RST,END]):
            self.send_ack(response)
            return self.terminate()
        
    def detect_frame(self):
        """
        A DCCNET packet always starts with 
        0   32  64
        -------------------------
        SYNC SYNC CS L ID F DATA
        -------------------------

        So, to synchonize the received frame, we must search for the double SYNC occurence
        """
        try:
            sync = 0x0
            while (sync != SYNCRONIZED):
                sync  = self.socket.receive(SYNC_SIZE)

            header  = self.socket.receive(HEADER_SIZE-SYNC_SIZE)
            cs,length,id,flag = struct.unpack('!H H H B',header)

            data    = self.socket.receive(length)

            format_string = create_format_string(length)

            response = struct.pack(format_string, SYNC, SYNC, cs, length, id, flag, data)
            return response

        except socket.error as e:
            # self.send_ack(self.last_received_frame)
            return

    def is_data_frame(self,response):
        # Upon accepting a data frame (cases 2 and), the receiver must respond with an acknowledgement frame.
        # (2) a data frame with an identifier (ID) different from that of the last received frame;

        if(not self.is_acceptable(response)): 
            return False
        if(Frame.get_flag(response) == ACK): 
            return False
        if(Frame.get_flag(response) == RST): 
            return False
        if(Frame.get_flag(response) == END): 
            return False
        return True
    
    def send_ack(self,response):
        id = Frame.get_id(response)
        frame = Frame.create_dccnet_frame("",id,ACK)
        print("ACK E: ", Frame.unpack_dccnet_frame(frame))
        self.socket.send(frame)


    def is_acceptable(self,frame):
        # A frame can only be accepted if (Checksum IS VALID)
        if(frame == None): 
            return False
        if(not Frame.is_checksum_valid(frame)): 
            return False

        cs,length,id,flag,data = Frame.unpack_dccnet_frame(frame)

        # (5) Termination frame;
        if((flag == END)):
            return True
        # (1) it is an acknowledgement frame for the last transmitted frame;
        if((flag == ACK) and (id == self.id)):  
            return True
        # (4) or a reset frame.
        if((flag == RST) and (id == RST_ID)):   
            return True
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        if((flag != ACK) and (id != self.last_id)):  
            return True
        # (3) a retransmission of the last received frame;
        if(self.last_received_frame == frame):  
            return True
        return False
    

    def enqueue(self,data,flag = 0):
        """
        All sended packets must pass by this function
        The queue is maintened to transmit the packets in the right order
        There is no limit on how many packets the queue can handle
        """
        if(data == None): return None
        frame   = Frame.create_dccnet_frame(data,id=self.send_id,flag=flag)
        if frame not in self.queue:
            self.queue.append(frame)
            self.send_id ^= 1
        return frame
    
    def dequeue(self,response):
        """
        Once a valid ACK is received, 
        the corresponding frame must get out of the queue
        
        The valid ACK only applies to the top of the queue
        """
        if(not self.queue): return None
        if Frame.get_id(self.queue[0]) == Frame.get_id(response):
            return self.queue.pop(0)   
        return None
    
    def break_in_lines(self,response):
        messages = []
        _,_,_,flg,data = Frame.unpack_dccnet_frame(response)

        self.curr += data
        lines = self.curr.split('\n')

        for m in lines[:-1]:
            messages.append(m)
        
        self.curr = lines[-1]
        return messages

    def terminate(self):
        self.queue = []
        self.running = False

    def run(self):
        while(self.running):
            self.transmit()
            self.receive()

        self.running = True
        self.queue = []
    
    def listen(self):
        while self.running:
            try:
                # --- accept client ---
                # print('[DEBUG] accept ... waiting')
                conn, addr = self.socket.socket.accept() # socket, address
                print('[DEBUG] connected!',addr)
                self.socket.socket = conn
                self.run()
            except socket.error as e: 
                continue