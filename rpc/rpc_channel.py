# -*- coding: utf-8 -*-
from google.protobuf import service
import struct

class EchoRpcChannel(service.RpcChannel):
	def __init__(self, rpc_service, conn):
		super(EchoRpcChannel, self).__init__()
		self.rpc_service = rpc_service
		self.tcp_connetion = conn
		self.recv_buf = ''
		self.msg_len = -1
		self.rpc_index = -1

	def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
		index = method_descriptor.index

		data = request.SerializeToString()

		pack_msg = ''.join([struct.pack('!ih', len(data), index), data])

		self.tcp_connetion.send(pack_msg)

	def input_data(self, data):
		self.recv_buf += data
		while True:
			if self.msg_len != -1 and self.rpc_index != -1:
				if len(self.recv_buf) >= self.msg_len:
					serialized_msg = self.recv_buf[:self.msg_len]
					self.call_rpc(serialized_msg, self.rpc_index)
					self.recv_buf = self.recv_buf[self.msg_len:]
					self.msg_len, self.rpc_index = -1, -1
				else:
					break
			else:
				if len(self.recv_buf) >= 6:
					self.msg_len, self.rpc_index = struct.unpack('!ih', self.recv_buf[:6])
					self.recv_buf = self.recv_buf[6:]
				else:
					break

	def call_rpc(self, serialized_msg, rpc_index):
		s_descriptor = self.rpc_service.GetDescriptor()
		m_descriptor = s_descriptor.methods[rpc_index]
		request = self.rpc_service.GetRequestClass(m_descriptor)()
		request.ParseFromString(serialized_msg)
		self.rpc_service.CallMethod(m_descriptor, None, request, None)