import select, signal, socket, sys, thread, binascii
from struct import *

def signal_handler(signal, frame):
	sys.stderr.write("Keyboard Interrupt, exiting")
	sys.exit(0)

class DNS_proxy:

	port = 53
	host = socket.gethostbyname(socket.gethostname())
	CHUNK_SIZE = 4096
	DNS_QUERY_MESSAGE_HEADER = Struct("!3H")
	DNS_IP = '8.8.8.8' #Google IP

	def __init__(self):
		self.host = str(sys.argv[1])
		try:

			self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.udp_sock.bind((self.host, self.port))
			self.udp_sock.setblocking(0)

			self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_sock.bind((self.host, self.port))
			self.tcp_sock.listen(1)
			self.tcp_sock.setblocking(0)

			self.sockets = [self.tcp_sock, self.udp_sock]

			print(self.host)

		except (Exception) as e:
			self.shutdown_with_error(str(e))

		self.listen_for_dns_queries()

	def listen_for_dns_queries(self):
		try:
			while True:
				ready_read, ready_write, exceptional = select.select(self.sockets, [], [], None)
				for sock in ready_read:
					if sock is self.tcp_sock:
						self.handle_tcp(sock)
					elif sock is self.udp_sock:
						self.handle_udp(sock)

		except (KeyboardInterrupt, SystemExit) as e:
			self.shutdown_with_error(str(e))


	def no_such_name(self, message, rcode_index):
		response = self.DNS_QUERY_MESSAGE_HEADER.unpack_from(message)
		rcode_digit = response[rcode_index]
		rcode_digit_hex = hex(rcode_digit)[-1]

		response2 = None
		counter = 4
		fmt = "!4H"
		while True:
			try:
				response2 = unpack_from(fmt, message)
				counter += 1
				fmt = "!" + str(counter) + "H"
			except:
				break

		print(response2)
		host_split = str(self.host).split('.')
		host_hexSplit = []
		host_hex_string = ""
		for numberIndex in range(len(host_split)):
			number = host_split[numberIndex]
			ans = hex(int(number))
			host_hexSplit.append(ans)
			if len(ans) == 3:
				host_hex_string += "0" + ans[2] # add spaces between entries
				# something
			elif len(ans) == 4:
				host_hex_string += ans[2:]
			if numberIndex < len(host_split) - 1:
				host_hex_string += " "

		if rcode_digit_hex == "0":
			return message
		elif rcode_digit_hex == "3":
			print("enter 3 digits hex")
			response2_lst = list(response2)
			response2_lst[rcode_index] = 33152
			if len(host_hexSplit) == 4:
				first = int(str(host_hexSplit[0][2:] + host_hexSplit[1][2:]), 16)
				second = int(str(host_hexSplit[2][2:] + host_hexSplit[3][2:]), 16)
				response2_lst[-2] = first
				response2_lst[-1] = second

			response2 = tuple(response2_lst)
			new_ans = ""
			for val in response2:
				new_ans += pack("!H", val)

			print(response2)
			return new_ans

	def handle_udp(self, sock):
		print("UDP")
		data, addr = sock.recvfrom(self.CHUNK_SIZE)
		dns_data = self.send_upstream(data, 1)
		dns_data = self.no_such_name(dns_data, 1)
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
		dns_data = self.send_upstream(message, 0)
		dns_data = self.no_such_name(dns_data, 2)
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
