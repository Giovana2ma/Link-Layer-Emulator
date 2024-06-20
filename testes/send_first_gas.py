import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port))
frame = c.create_dccnet_frame(gas)
c.socket_.connect()
c.socket_.send(frame)
header = c.socket_.receive(HEADER_SIZE)
length = struct.unpack(HEADER_FORMAT,header)[3]
print(c.unpack_dccnet_frame(header))

# _,_,cs,length,id,flags = struct.unpack(HEADER_FORMAT,header)
# msg = c.socket_.receive(length)
# print(header)
# print(length)
# print(msg)