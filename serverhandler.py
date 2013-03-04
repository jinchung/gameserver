""" Game Server """

import socket
import select
import gameinterface

class GameServer(object):
	
	def __init__(self, HOST, PORT):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.setblocking(0)
		self.messages = {}	
		self.gint = gameinterface.GameInterface(self)
		print 'Game Server socket created'

		try:
			self.s.bind((HOST, PORT))
			print 'Game Server bind complete on HOST: ' + HOST + ' on PORT: ' + str(PORT)
		except socket.error, msg:
			print 'Bind failed. Error code: ' + str(msg[0]) + ' Message ' + msg[1]
			self.s.close()

		self.s.listen(10)
		print 'Game Server is now listening'
		

	def fileno(self):
		return self.s.fileno()

	def sendMessage(self, s, msg):
		if s not in self.outputs:
			self.outputs.append(s)
		self.messages[s].append(msg)

	def cleanup(self, s1, s2):
		if s1 in self.messages:
			del self.messages[s1]
		if s2 in self.messages:
			del self.messages[s2]
		if s1 in self.inputs:
			self.inputs.remove(s1)
		if s2 in self.outputs:
			self.inputs.remove(s2)
		if s1 in self.inputs:
			self.outputs.remove(s1)
		if s2 in self.outputs:
			self.outputs.remove(s2)

	def serve_forever(self):
		self.inputs = [self.s]
		self.outputs = []
		while True:
			print 'Game Server Re-selecting'
			readReady, writeReady, errorReady = select.select(self.inputs, self.outputs, [])
			print 'Game Server has Selected...now going through each socket'
			for r in readReady:
				print 'GS Read loop'
				if r is self.s:
					print 'GS Current socket IS the Game Server socket'
					conn, addr = r.accept()
					print 'Game Server accepted connection %d from %s' % (conn.fileno(), addr)
					self.inputs.append(conn)
				else:
					print 'GS Current socket is NOT the Game Server socket'
					data = r.recv(1024)
					if data:
						print 'GS Received...%s' % (data)	
						if r not in self.outputs:
							self.outputs.append(r)
							if r not in self.messages:
								self.messages[r] = []
						self.gint.handleIncomingMsg(data, r)
					else: # client has actually closed itself
						print 'GS Closing a socket upon reading no data.'			
						if r in self.outputs:
							self.outputs.remove(r)
							del self.messages[r]
						self.inputs.remove(r)
						r.close()

			for w in writeReady:
				print 'GS write loop'
				if w in self.outputs: #is there a more elegant way to do this?
					if self.messages[w] == []:
						self.outputs.remove(w)
						#del self.messages[w]
					else:
						n = w.send(self.messages[w][0])
						if n == len(self.messages[w][0]):
							print "GS Sent {0} to {1}".format(self.messages[w][0], w.getpeername())
							self.messages[w] = self.messages[w][1:]
						else:
							print "GS Sent {0} to {1}".format(self.messages[w][0], w.getpeername())
							self.messages[w][0] = self.messages[w][0][n:]

			for e in errorReady:
				print "GS Closing {0} upon exceptional condition".format(e.getpeername())
				self.inputs.remove(e)
				if e in self.outputs:
					self.outputs.remove(e)
					del self.messages[e]
				e.close()

server = GameServer('localhost', 8888) 
server.serve_forever()
