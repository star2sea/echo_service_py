# -*- coding: utf-8 -*-
from proto.echo_pb2 import EchoServerService, EchoClientService
from proto.echo_pb2 import EchoClientService_Stub, EchoServerService_Stub
from proto.echo_pb2 import EchoResponse
class TestEchoServerService(EchoServerService):
	def __init__(self):
		super(TestEchoServerService, self).__init__()

	def attach_rpc_channel(self, rpc_channel):
		self.rpc_channel = rpc_channel
		self.client_stub = EchoClientService_Stub(rpc_channel)

	def echo_server(self, rpc_controller, request, done):
		print 'server received msg', request.message
		self.call_client('hello')

	def call_client(self, msg):
		response = EchoResponse()
		response.message = msg
		self.client_stub.echo_client(None, response, None)

class TestEchoClientService(EchoClientService):
	def __init__(self):
		super(TestEchoClientService, self).__init__()

	def attach_rpc_channel(self, rpc_channel):
		self.rpc_channel = rpc_channel
		self.server_stub = EchoServerService_Stub(rpc_channel)

	def echo_client(self, rpc_controller, request, done):
		print 'client received msg', request.message

	def call_server(self, msg):
		response = EchoResponse()
		response.message = msg
		self.server_stub.echo_server(None, response, None)