# -*- coding: utf-8 -*-

import socket
import errno
from channel import Channel
from connection import TcpConnection

class TcpClient(object):
	def __init__(self, poller, ip, port):
		super(TcpClient, self).__init__()

		self.poller = poller
		self.ip = ip
		self.port = port

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(False)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.connecting = False
		self.connected = False

		self.channel = Channel(self.poller, self.sock)
		self.channel.set_writeable_callback(self.on_connect)

		self.tcp_connection = None

		self.message_callback = None
		self.connection_callback = None

	def set_message_callback(self, cb):
		self.message_callback = cb

	def set_connection_callback(self, cb):
		self.connection_callback = cb

	def on_connect(self):
		err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
		if err != 0:
			self.stop()
		else:
			self.channel.disabll_all()

			self.tcp_connection = TcpConnection(self.poller, self.sock)
			self.tcp_connection.set_message_callback(self.message_callback)
			self.tcp_connection.set_connection_callback(self.connection_callback)
			self.tcp_connection.set_close_callback(self.on_close)
			self.connecting = False
			self.connected = True

			self.connection_callback and self.connection_callback(self.tcp_connection)

	def on_close(self, conn):
		self.stop()

	def connect(self):
		if self.connecting:
			return

		if self.connected:
			self.stop()

		self.connecting = True
		try:
			self.sock.connect((self.ip, self.port))
		except socket.error, err:
			if err.args[0] not in (errno.EINPROGRESS, ):
				self.stop()
			else:
				self.channel.enable_writing()

	def stop(self):
		self.connected = False
		self.connecting = False

		if self.tcp_connection and self.tcp_connection.is_connected():
			self.tcp_connection.stop()
			self.tcp_connection = None
		self.channel.disabll_all()