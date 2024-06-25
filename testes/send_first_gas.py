import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port))


def md5(frame):
    line = Frame.unpack_dccnet_frame(frame)[4]
    b = line[:-1]
    return hashlib.md5(line[:-1].encode('ascii')).hexdigest()

c.process = md5
response = c.enqueue(gas)
c.run()
a = 10