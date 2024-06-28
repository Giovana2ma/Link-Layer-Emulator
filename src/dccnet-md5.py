import sys
import hashlib
from NetworkInterface import *

args = sys.argv
host_port, gas = args[1], args[2]
host, port = host_port.split(':')

c = NetworkInterface(host, int(port))

def md5(line):
    return hashlib.md5(line.encode('ascii')).hexdigest() + '\n'

c.process_line = md5
response = c.enqueue(gas + '\n')
c.run()