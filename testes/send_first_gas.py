import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port))

def md5(line):
    return hashlib.md5(line.encode('ascii')).hexdigest()

c.process_line = md5
response = c.enqueue(gas)
c.run()
a = 10