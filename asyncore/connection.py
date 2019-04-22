# -*- coding: utf-8 -*-
import errno
from channel import Channel
import socket
CONNECTED = 1
DISCONNECTED = 2
class TcpConnection(object):
	def __init__(self, poller, sock):
		super(TcpConnection, self).__init__()
		self.poller = poller
		self.sock = sock

		self.channel = Channel(poller, sock)
		self.channel.set_writeable_callback(self.handle_writeable)
		self.channel.set_readable_callback(self.handle_readable)
		self.channel.set_exception_callback(self.handle_exception)
		self.channel.enable_reading()

		self.send_buf = ''
		self.recv_buf = ''

		self.state = CONNECTED

		self.message_callback = None
		self.connection_callback = None
		self.close_callback = None

	def is_connected(self):
		return self.state == CONNECTED

	def get_fd(self):
		return self.sock.fileno()

	def set_message_callback(self, cb):
		self.message_callback = cb

	def set_connection_callback(self, cb):
		self.connection_callback = cb

	def set_close_callback(self, cb):
		self.close_callback = cb

	def handle_readable(self):
		read_closed = False
		while True:
			try:
				data = self.sock.recv(1024)
				if not data:
					read_closed = True
					break
				self.recv_buf += data
			except socket.error, err:
				if err.args[0] not in (errno.EAGAIN, ):
					print 'socket read error, err = [%s]'%err
					self.handle_close()
				break

		self.message_callback and self.message_callback(self, self.recv_buf)
		self.recv_buf = ''

		if read_closed:
			self.handle_close()

	def handle_writeable(self):
		if self.send_buf:
			n = self.sock.send(self.send_buf)
			if n <= 0:
				print 'connection broken'
				self.handle_close()
				return
			self.send_buf = self.send_buf[n:]

		if not self.send_buf:
			self.channel.disable_writing()

	def handle_exception(self):
		err = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
		if err != 0:
			print 'connection error, err = [%s]'%err

	def handle_close(self):
		self.state = DISCONNECTED
		self.connection_callback and self.connection_callback(self)
		self.close_callback and self.close_callback(self)
		self.stop()

	def stop(self):
		try:
			if self.sock:
				self.sock.close()
		except socket.error, err:
			print 'socket close error, err = [%s]'%err

		self.state = DISCONNECTED
		self.channel.disabll_all()
		self.poller = None
		self.sock = None
		self.channel = None
		self.message_callback = None
		self.connection_callback = None
		self.close_callback = None

	def send(self, msg):
		if not self.is_connected():
			print 'connection disconnected, send error!!!'
			return

		if self.send_buf:
			self.send_buf += msg
			if not self.channel.is_writing():
				self.channel.enable_writing()
			return

		try:
			n = self.sock.send(msg)

			if n <= 0:
				print 'connection broken'
				self.handle_close()
				return

			self.send_buf += msg[n:]

			if self.send_buf:
				self.channel.enable_writing()

		except socket.error, err:
			if err.args[0] not in (errno.EAGAIN, ):
				print 'socket send error, err = [%s]'%err
				self.handle_close()

