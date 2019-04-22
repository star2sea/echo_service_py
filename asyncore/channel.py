# -*- coding: utf-8 -*-
IO_EVT_NONE = 0x00
IO_EVT_R = 0x01
IO_EVT_W = 0x02
IO_EVT_R_W = IO_EVT_R | IO_EVT_W
class Channel(object):
	def __init__(self, poller, sock):
		super(Channel, self).__init__()

		self.poller = poller
		self.sock = sock

		self.fd = sock.fileno()

		self.events = IO_EVT_NONE

		self.readable_callback = None
		self.writeable_callback = None
		self.exception_callback = None

	def get_fd(self):
		return self.fd

	def is_active(self):
		return self.events != IO_EVT_NONE

	def is_writing(self):
		return self.events & IO_EVT_W

	def is_reading(self):
		return self.events & IO_EVT_R

	def enable_reading(self):
		self.events |= IO_EVT_R
		self.update()

	def disable_reading(self):
		self.events &= (~IO_EVT_R)
		self.update()

	def enable_writing(self):
		self.events |= IO_EVT_W
		self.update()

	def disable_writing(self):
		self.events &= (~IO_EVT_W)
		self.update()

	def enable_all(self):
		self.events = IO_EVT_R_W
		self.update()

	def disabll_all(self):
		self.events = IO_EVT_NONE
		self.update()

	def update(self):
		self.poller.update(self)

	def handle_read(self):
		self.readable_callback and self.readable_callback()

	def handle_write(self):
		self.writeable_callback and self.writeable_callback()

	def handle_exception(self):
		self.exception_callback and self.exception_callback()

	def set_readable_callback(self, cb):
		self.readable_callback = cb

	def set_writeable_callback(self, cb):
		self.writeable_callback = cb

	def set_exception_callback(self, cb):
		self.exception_callback = cb