# -*- coding: utf-8 -*-

from asyncore.tcp_server import TcpServer
from asyncore.poller import Select
from rpc.echo_service import TestEchoServerService
from rpc.rpc_channel import EchoRpcChannel

class EchoServer(object):
	def __init__(self):
		super(EchoServer, self).__init__()
		self.poller = Select()
		self.server = TcpServer(self.poller, 8888)
		self.server.set_message_callback(self.on_message)
		self.server.set_connection_callback(self.on_connected)

		self.clients = {}
		self.rpc_channels = {}
		self.rpc_services = {}

	def on_message(self, conn, msg):
		fd = conn.get_fd()
		rpc_channle = self.rpc_channels.get(fd)
		if rpc_channle is not None:
			rpc_channle.input_data(msg)

	def on_connected(self, conn):
		sock = conn.sock
		if conn.is_connected():
			client_info = sock.getpeername()
			self.clients[sock.fileno()] = client_info
			print 'client %s connected'%(client_info, )
			rpc_service = TestEchoServerService()
			rpc_channel = EchoRpcChannel(rpc_service, conn)
			rpc_service.attach_rpc_channel(rpc_channel)
			fd = conn.get_fd()
			self.rpc_services[fd] = rpc_service
			self.rpc_channels[fd] = rpc_channel
		else:
			client_info = self.clients.pop(sock.fileno(), None)
			print 'client %s disconnected' %(client_info, )

	def start(self):
		self.server.start()

	def poll(self):
		self.poller.poll()

if __name__ == '__main__':
	echo_server = EchoServer()
	echo_server.start()
	while True:
		echo_server.poll()