# -*- coding: utf-8 -*-
import select

class Select(object):
	def __init__(self):
		super(Select, self).__init__()
		self.activeChannels = {}

	def update(self, channel):
		fd = channel.get_fd()
		if fd not in self.activeChannels:
			self.activeChannels[fd] = channel
		elif not channel.is_active():
			self.activeChannels.pop(fd)

	def poll(self):
		rlist, wlist, elist = [], [], []
		for channel in self.activeChannels.itervalues():
			sock = channel.sock
			if channel.is_reading():
				rlist.append(sock)
				elist.append(sock)
			if channel.is_writing():
				wlist.append(sock)
				elist.append(sock)

		rlist, wlist, elist = select.select(rlist, wlist, elist, 0)

		for sock in rlist:
			channel = self.activeChannels.get(sock.fileno())
			if channel is not None:
				channel.handle_read()

		for sock in wlist:
			channel = self.activeChannels.get(sock.fileno())
			if channel is not None:
				channel.handle_write()

		for sock in elist:
			channel = self.activeChannels.get(sock.fileno())
			if channel is not None:
				channel.handle_exception()
