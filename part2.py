import socket
import sys 

class DNS_proxy:
	
	port = 53
	host = ""
	CHUNK_SIZE = 4096
	DNS_IP = 8.8.8.8 #Google IP
	
	def __init__(self):
		try: 
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.bind(self.host, self.port)
			while True: 
				data, addr = self.sock.recvfrom(self.CHUNK_SIZE)
				if data: 
					sent = self.sock.sendto(data,addr)
		except exception, e: 
			sys.stderr.write(e)
			self.sock.shutdown()
			return 0 

if __name__ == "__main__": 
    main()
