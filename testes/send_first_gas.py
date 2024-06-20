import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port),gas=gas)
frame = c.create_dccnet_frame(gas)
c.socket_.connect()
c.socket_.send(frame)
msg = c.socket_.receive()
header = msg[:HEADER_SIZE]
_,_,cs,length,id,flags = struct.unpack(HEADER_FORMAT,header)
print(msg[HEADER_SIZE:])
print(msg)
print(len(msg[HEADER_SIZE:]),header)
print()