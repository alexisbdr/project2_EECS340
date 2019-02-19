import socket
import sys
from urlparse import urlparse
import os
import time
import signal

CRLF = '\r\n\r\n'

def signal_handler(sig, frame):

	sock.shutdown()


def generate_http_header(code, host):

	http_header = 'HTTP/1.1 200 OK \n'

	current_date = 'Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()) + ' GMT\n'
	http_header += current_date

	server_name = 'Server: http_server1 (Simple)\n'
	http_header += server_name

	if code == 200:
		http_header += 'Content-Type: text/html; charset=UTF-8\n'

	CLRF = '\r\n\r\n'
	connection_close = 'Connection: Close' + CLRF
	http_header+=connection_close

	return http_header


def generate_http_response(code, host_name):

	response_header = generate_http_header(code, host_name)

	response_body = "<html><body><p>You will never find"
	response_body += str(host_name)
	response_body += "come have fun at https://theuselessweb.com/ </p>"

	response = response_header + response_body

	print(response)

	return response


def get_host(data):
	
	http_header = data.split(CRLF,1)[0].split('\n')
	print(http_header)
	for line in http_header:
		if line[0:3] == 'Host':
			break
	host = line.split()[1]
	print(host)

	return host

def get_request_method(data):

	http_header = data.split('\n')[0].split()
	print(http_header)
	if len(http_header) == 0:
		return None

	return str(http_header[0])


def get_file_name(data):

	http_header = data.split('\n')[0].split()

	file_name = http_header[1]

	if file_name == '/':
		return 'index.html'

	return file_name.strip('/')


def ends_with_(name):

	if name[-4:] == ".htm" or name[-4:] == "html":
		return False


class Socket:

	CHUNK = 1024

	def __init__(self):

		self.host = ""
		self.port = 80

		self.create_socket()


	def shutdown(self):

		self.sock.shutdown(socket.SHUT_RDWR)

		sys.exit(1)


	def create_socket(self):

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.sock.bind((self.host, self.port))

		self.run_forever()


	def run_forever(self):

		while True:

			try:

				self.sock.listen(1) #1 means accept single connection

				client_socket, client_address = self.sock.accept()

				data = client_socket.recv(self.CHUNK)

				if data and get_request_method(data) == "GET":

					http_host = get_host(data)
					
					http_response = generate_http_response(200, http_host)

					client_socket.send(http_response)

					client_socket.close()

			except (KeyboardInterrupt, SystemExit):

				self.sock.shutdown(socket.SHUT_RDWR)

				sys.exit(1)



if __name__ == "__main__":
	Socket()