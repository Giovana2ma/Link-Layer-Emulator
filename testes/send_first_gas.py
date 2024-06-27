import sys
sys.path.insert(1, 'src/')
from client import * 

args = sys.argv
host,port,gas = args[1:]
c = Client(host,int(port))




# c.process = Client.md5()
response = c.enqueue(gas)
c.run()
a = 10