# -*- coding: utf-8 -*-
import socket
import errno
from channel import Channel
from connection import TcpConnection

class TcpServer(object):
	def __init__(self, poller, port, ip = None):
		self.poller = poller
		self.port = port
		self.ip = ip if ip is not None else '127.0.0.1'

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(False)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.channel = Channel(self.poller, self.sock)
		self.channel.set_readable_callback(self.handle_accept)

		self.connection_callback = None
		self.message_callback = None

		self.connections = {}

	def set_connection_callback(self, cb):
		self.connection_callback = cb

	def set_message_callback(self, cb):
		self.message_callback = cb

	def start(self):
		self.sock.bind((self.ip, self.port))
		self.sock.listen(10)
		self.channel.enable_reading()

	def on_connection_close(self, conn):
		fd = conn.get_fd()
		self.connections.pop(fd, None)

	def handle_accept(self):
		try:
			sock, addr = self.sock.accept()
			if sock:
				tcp_connection = TcpConnection(self.poller, sock)
				tcp_connection.set_message_callback(self.message_callback)
				tcp_connection.set_connection_callback(self.connection_callback)
				tcp_connection.set_close_callback(self.on_connection_close)
				self.connections[sock.fileno()] = tcp_connection
				self.connection_callback and self.connection_callback(tcp_connection)
		except socket.error, err:
			if err.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN, errno.ECONNABORTED):
				print 'accept error, err = [%s]'%err
				return
