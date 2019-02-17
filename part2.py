import ssignal, socket, sys, thread

def signal_handler(signal, frame):
    sys.stderr.write("Keyboard Interrupt, exiting")
    sys.exit(0)

class DNS_proxy:
	
	port = 53
	host =""
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
		while True: 
			data,addr = self.sock.recvfrom(self.CHUNK_SIZE)
			if data: 
				sys.stdout.write(data)
				self.send_upstream(data)
	
	def send_upstream(self, data):
		self

	def shutdown_with_error(self, error):
		sys.stderr.write(error)
		self.sock.shutdown(socket.SHUT_RDWR)
		sys.exit(1)

if __name__ == "__main__": 
	signal.signal(signal.SIGINT, signal_handler)
    DNS_proxy()
