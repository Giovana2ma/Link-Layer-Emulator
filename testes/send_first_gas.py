import sys
sys.path.insert(1, 'src/')
from NetworkInterface import * 

args = sys.argv
host,port,gas = args[1:]
c = NetworkInterface(host,int(port))

def md5(line):
    return hashlib.md5(line.encode('ascii')).hexdigest() + "\n"

c.process_line = md5
response = c.enqueue(gas + "\n")
c.run()