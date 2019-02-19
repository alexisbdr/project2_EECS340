import select, signal, socket, sys, thread
from struct import *

def signal_handler(signal, frame):
	sys.stderr.write("Keyboard Interrupt, exiting")
	sys.exit(0)

class DNS_proxy:

	port = 53
	host = ""
	CHUNK_SIZE = 4096
	DNS_IP = '8.8.8.8' #Google IP

	def __init__(self):
		try:
			self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.udp_sock.bind((self.host, self.port))
			self.udp_sock.setblocking(0)

			self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_sock.bind((self.host, self.port))
			self.tcp_sock.listen(1)

			self.tcp_sock.setblocking(0)

			self.sockets = [self.tcp_sock, self.udp_sock]

		except (Exception) as e:
			self.shutdown_with_error(str(e))

		self.listen_for_dns_queries()

	def listen_for_dns_queries(self):
		try:
			while True:
				ready_read, ready_write, exceptional = select.select(self.sockets, [], [], None)
				for sock in ready_read:
					if int(sock.type) == 1:
						self.handle_tcp(sock)
					if int(sock.type) == 2:
						self.handle_udp(sock)

		except (KeyboardInterrupt, SystemExit) as e:
			self.shutdown_with_error(str(e))

	def handle_udp(self, sock):
		data, addr = sock.recvfrom(self.CHUNK_SIZE)
		dns_data = self.send_upstream(data, 1)
		print(dns_data)
		sock.sendto(dns_data, addr)

	def handle_tcp(self, sock):
		print("TCP")
		conn, addr = sock.accept()
		message = conn.recv(2)
		message_size = unpack("!H", message)[0]
		while message_size:
			data = conn.recv(1024)
			message += data
			message_size -= len(data)
		print(message)
		dns_data = self.send_upstream(message, 0)
		print(dns_data)
		conn.sendto(dns_data, addr)

	#threadless and loopless for now - could be interesting to run this in the background
	def send_upstream(self, data, flag):
		if flag:
			up_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		else:
			up_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		up_sock.connect((self.DNS_IP,self.port))
		up_sock.send(data)
		rec_data = up_sock.recv(self.CHUNK_SIZE)

		return rec_data

	def shutdown_with_error(self, error):
		sys.stderr.write(error)
		self.tcp_sock.shutdown(socket.SHUT_RDWR)
		self.udp_sock.shutdown(socket.SHUT_RDWR)
		sys.exit(1)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	DNS_proxy()
