""" 
Functions and classes for message parsing 
"""
import ast

class RequestMessage(object):
	def __init__(self, type, gameId, gameType, move):
		self.type = type
		self.gameId = gameId
		self.gameType = gameType
		self.move = move
		
class ResponseMessage(object):
	def __init__(self, type, gameId, gamestate, msg, currPlayer):
		self.type = type
		self.gameId = gameId
		self.gamestate = gamestate
		self.msg = msg
		self.currPlayer = currPlayer

def parse(data):
	dataDict = ast.literal_eval(data)
	return RequestMessage(dataDict["type"], dataDict["gameId"], dataDict["gameType"], dataDict["move"])
