import struct
import threading
import hashlib
import time

from socket_t   import *
from utils      import *
from DCCNET_frame import *


class NetworkInterface:
    def __init__(self,host,port):
        self.socket = Socket(host,port)

        self.process = lambda x: Frame.unpack_dccnet_frame(x)[4]
        self.last_received_frame = None
        self.id   = 0

        self.condition = threading.Condition()
        self.queue = []
        self.running = True
    
    def transmit(self):
        while self.running:
            with self.condition:
                while (not self.queue) and (self.running):
                    self.condition.wait()
                if(not self.running): break

                frame   = self.queue[0]
                print("Enviado: ", Frame.unpack_dccnet_frame(frame))
                self.socket.send(frame)

            time.sleep(2)
        return frame
    
    def receive(self):
        while self.running:
            time.sleep(1)
            with self.condition:
                header  = self.socket.receive(HEADER_SIZE)
                cs,length,id,flag,_ = Frame.unpack_dccnet_frame(header)
                data    = self.socket.receive(length)

                format_string = create_format_string(length)
                response = struct.pack(format_string, SYNC, SYNC, cs, length, id, flag, data)
                self.treat_response(response)
            time.sleep(1)
        return response
            # return self.treat_response(response)

    def treat_response(self,response):
        print()
        print("Recebido: ", Frame.unpack_dccnet_frame(response))

        if(not self.is_acceptable(response)): 
            return response
        
        if(self.must_send_ack(response)):
            self.send_ack(response)
            return self.enqueue(self.process(response))

        if(Frame.get_flag(response) == ACK):
            self.id = int(not self.id)
            return self.dequeue(response)

        if(Frame.get_flag(response) == RST):
            return self.terminate()

    
    def must_send_ack(self,response):
        #Upon accepting a data frame (cases 2 and), the receiver must respond with an acknowledgement frame.
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        # (3) a retransmission of the last received frame;

        if(not self.is_acceptable(response)): 
            return False
        if(Frame.get_flag(response) == ACK): 
            return False
        if(Frame.get_flag(response) == RST): 
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

        # (1) it is an acknowledgement frame for the last transmitted frame;
        if((flag == ACK) and (id == self.id)):  
            return True
        # (4) or a reset frame.
        if((flag == RST) and (id == RST_ID)):   
            return True
        # (2) a data frame with an identifier (ID) different from that of the last received frame;
        if((flag != ACK) and (id != self.id)):  
            return True
        # (3) a retransmission of the last received frame;
        if(self.last_received_frame == frame):  
            return True
        return False
    

    def enqueue(self,data,flag = 0):
        frame   = Frame.create_dccnet_frame(data + "\n",id=self.id,flag=flag)
        with self.condition:
            self.queue.append(frame)
            self.condition.notify()
        return frame
    
    def dequeue(self,response):
        id = Frame.get_id(response)
        if(self.queue):
            if Frame.get_id(self.queue[0]) == id:
                return self.queue.pop()   
        return None
        
    def terminate(self):
        with self.condition:
            self.queue = []
            self.running = False
            self.condition.notify_all()

    def run(self):
        transmit_thread = threading.Thread(target=self.transmit)
        receive_thread  = threading.Thread(target=self.receive)

        transmit_thread.start()
        receive_thread.start()

        transmit_thread.join()
        receive_thread.join()