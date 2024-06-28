import socket

class Socket:
    """ Class that implements the socket communication with builtin stop and wait."""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = self.create_socket()
        self.connect()

    def determine_ip_type(self,hostname):
        ip_address = socket.getaddrinfo(hostname, None)[0][4][0]
        try:
            socket.inet_pton(socket.AF_INET, ip_address)
            return socket.AF_INET

        except socket.error:
            pass

        try:
            socket.inet_pton(socket.AF_INET6, ip_address)
            return socket.AF_INET6
        except socket.error:
            pass

        # If neither conversion succeeds, the resolved IP address is not a valid IPv4 or IPv6 address
        return None

    def create_socket(self):
        # Create a TCP socket
        self.socket = socket.socket(self.determine_ip_type(self.host), socket.SOCK_STREAM)
        self.socket.settimeout(1)
        return self.socket
    
    def connect(self):
        self.socket.connect((self.host, self.port))
    
    def send(self,packet):
        try:
            self.socket.sendto(packet, (self.host, self.port))

        except socket.error as e: 
            print ("Socket error: %s" %str(e)) 
        except Exception as e: 
            print ("Other exception: %s" %str(e))
        

    def receive(self,n_bytes = 4096):
        try:
            response = self.socket.recv(n_bytes)
            return response
        except socket.error as e: 
            # print ("Socket error: %s" %str(e)) 
            raise e
        except Exception as e: 
            print ("Other exception: %s" %str(e)) 

    def close(self):
        if self.socket:
            self.socket.close()

    def __del__(self):
        return self.close()


