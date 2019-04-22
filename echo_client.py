# -*- coding: utf-8 -*-
from asyncore.tcp_client import TcpClient
from asyncore.poller import Select
from rpc.echo_service import TestEchoClientService
from rpc.rpc_channel import EchoRpcChannel

class EchoClient(object):
	def __init__(self):
		super(EchoClient, self).__init__()
		self.poller = Select()
		self.client = TcpClient(self.poller, '127.0.0.1', 8888)
		self.client.set_message_callback(self.on_message)
		self.client.set_connection_callback(self.on_connected)

		self.rpc_service = TestEchoClientService()

	def on_message(self, conn, msg):
		self.rpc_channel.input_data(msg)

	def on_connected(self, conn):
		if conn.is_connected():
			print 'connect to server'
			self.rpc_channel = EchoRpcChannel(self.rpc_service, conn)
			self.rpc_service.attach_rpc_channel(self.rpc_channel)
			self.rpc_service.call_server('world')
		else:
			print 'disconnect to server'

	def connect(self):
		self.client.connect()

	def poll(self):
		self.poller.poll()

if __name__ == '__main__':
	echo_client = EchoClient()
	echo_client.connect()
	while True:
		echo_client.poll()
