import select, signal, socket, sys, thread, binascii
from struct import *

def signal_handler(signal, frame):
	sys.stderr.write("Keyboard Interrupt, exiting")
	sys.exit(0)

class DNS_proxy:

	port = 53
	host = socket.gethostbyname(socket.gethostname())
	CHUNK_SIZE = 4096
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
		success_lst = [11008, 33152, 1, 1, 0, 0, 887, 30583, 1639, 28527, 26476, 25859, 25455, 27904, 1, 1, 49164, 1, 1, 0, 299, 4, 44249, 1092]
		response = None
		counter = 3
		fmt = "!3H"
		while True:
			try:
				response = unpack_from(fmt, message)
				counter += 1
				fmt = "!" + str(counter) + "H"
			except:
				break

		rcode_digit = response[rcode_index]
		rcode_digit_hex = hex(rcode_digit)[-1]

		host_split = str(self.host).split('.')
		host_hexSplit = []
		for numberIndex in range(len(host_split)):
			number = host_split[numberIndex]
			ans = hex(int(number))
			host_hexSplit.append(ans)

		if rcode_digit_hex == "0":
			return message
		elif rcode_digit_hex == "3":
			response_lst = list(response)
			if rcode_index == 2:
				response_lst = response_lst[1:]
			if len(host_hexSplit) == 4:
				first = int(str(host_hexSplit[0][2:] + host_hexSplit[1][2:]), 16)
				second = int(str(host_hexSplit[2][2:] + host_hexSplit[3][2:]), 16)
				response_lst[-2] = first
				response_lst[-1] = second

			prevEntry = response_lst[6]
			query_lst = [prevEntry]
			for entry in response_lst[7:]:
				if entry == 0:
					query_lst.append(1)
					query_lst.append(1)
					break
				elif entry == 1 and prevEntry == 1:
					query_lst.append(1)
					break
				query_lst.append(entry)
				prevEntry = entry

			final_response_lst = response_lst[0:1] + success_lst[1:6] + query_lst + success_lst[16:]
			final_response_lst[-2] = response_lst[-2]
			final_response_lst[-1] = response_lst[-1]
			final_rsps_len = len(final_response_lst) * 2
			final_response_lst = [final_rsps_len] + final_response_lst
			final_response = tuple(final_response_lst)
			new_ans = ""
			for val in final_response:
				new_ans += pack("!H", val)
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
