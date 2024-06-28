import sys
from NetworkInterface import *


def read_file_in_chunks(input_file, chunk_size=4096):
    with open(input_file, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


def server_mode(port, input_file, output_file):
    host = "127.0.0.1"
    c = NetworkInterface(host,port,socket_type="server")
    c.process_line = lambda x: None
    
    for m in read_file_in_chunks(input_file):
        c.enqueue(str(m))
    c.listen()


def client_mode(host, port, input_file, output_file):
    c = NetworkInterface(host,port,socket_type="client")
    c.process_line = lambda x: None

    for m in read_file_in_chunks(input_file):
        c.enqueue(str(m))
    c.enqueue("",flag=END)
    c.run()


def main():
    args = sys.argv
    if args[1] == '-s' and len(args) == 5:
        server_mode(int(args[2]), args[3], args[4])

    elif args[1] == '-c' and len(args) == 5:
        ip, port = args[2].split(':')
        client_mode(ip, int(port), args[3], args[4])
    else:
        print("Usage:")
        print("  Server mode: ./dccnet-xfer -s <PORT> <INPUT> <OUTPUT>")
        print("  Client mode: ./dccnet-xfer -c <IP>:<PORT> <INPUT> <OUTPUT>")

if __name__ == "__main__":
    main()
