import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port))

response = c.transmit(gas)

cs,length,id,flags,data = c.unpack_dccnet_frame(response)
print(flags)