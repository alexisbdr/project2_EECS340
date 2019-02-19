import signal, socket, sys, thread

def signal_handler(signal, frame):
    sys.stderr.write("Keyboard Interrupt, exiting")
    sys.exit(0)

class DNS_proxy:
	
	port = 53
	host = socket.gethostbyname(socket.gethostname())
	CHUNK_SIZE = 4096
	DNS_IP = '8.8.8.8' #Google IP
	
	def __init__(self):
		try: 
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.bind((self.host, self.port))
		except (Exception) as e: 
			self.shutdown_with_error(str(e))

		self.listen_for_dns_queries()

	def listen_for_dns_queries(self):
		try: 
			while True: 
				data,addr = self.sock.recvfrom(self.CHUNK_SIZE)
				if data: 
					print(data)
					dns_data = self.send_upstream(data)
					print(dns_data)
					self.sock.sendto(dns_data, addr)
		except (KeyboardInterrupt, SystemExit) as e: 
			self.shutdown_with_error(str(e))

	
	#threadless and loopless for now - could be interesting to run this in the background
	def send_upstream(self, data):
		up_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		up_sock.connect((self.DNS_IP,self.port))
		up_sock.send(data)
		rec_data = up_sock.recv(self.CHUNK_SIZE)
		
		return rec_data

	def shutdown_with_error(self, error):
		sys.stderr.write(error)
		self.sock.shutdown(socket.SHUT_RDWR)
		sys.exit(1)

if __name__ == "__main__": 
	signal.signal(signal.SIGINT, signal_handler)
	DNS_proxy()