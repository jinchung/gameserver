""" Game Server """

import socket
import game
import random
import messageparser as mp

class GameInterface(object):
	
	def __init__(self, server):
		self.games_in_play = {}
		self.games_pending = {}
		self.server = server
		
		self.games_pending["tictactoe"] = []
		self.games_pending["connect4"] = []
		self.games_pending["chess"] = []
		self.games_pending["checkers"] = []
		self.games_pending["go"] = []

	def handleIncomingMsg(self, data, r):
		try:
			inputMsg = mp.parse(data)
			type = inputMsg.type
		except :
			type = 'error'
		if type == "new":
			print 'Game request: NEW'
			self.handleJoinGame(inputMsg, r)	
		elif type == "move":
			self.handleMove(inputMsg, r)
		elif type == "exit":
			pass
		elif type == "reqgameplay":
			pass
		else:
			print 'Error reading game request.'
			self.sendMessage(r, 'Error reading game request. Please make sure message type is either [new move exit reqgameply]')
		
	def movePendingToPlay(self, g, r):
		self.games_in_play[g.id] = g
		g.players.append(r)
		announce =  mp.ResponseMessage("announce", g.id, None, "Game is now live", None)
		self.sendMessage(r, announce)
		self.sendMessage(g.players[0], announce)
		self.randomlyChooseFirstPlayerAndStartGame(g)

	def sendMessage(self, s, msg):
		self.server.sendMessage(s, str(msg.__dict__))

	def randomlyChooseFirstPlayerAndStartGame(self, g):
		g.currPlayerIndex = random.randint(0,1)
		print 'curr player index is: %s' % (g.currPlayerIndex)
		self.constructGamePlayMsg(g)
	
	def constructGamePlayMsg(self, g):
		play = mp.ResponseMessage("play", g.id, g.gamestate, "Play", g.getCurrPlayer())
		self.sendMessage(g.getCurrPlayer(), play)

	def createNewGame(self, inputMsg, r):
		g = game.buildNewGame(inputMsg.gameType, r)
		self.games_pending[g.type].append(g)
		announce = mp.ResponseMessage("announce", g.id, None, "Created a new game. Please wait for another player to connect.", None)
		self.sendMessage(r, announce)

	def handleJoinGame(self, inputMsg, r):
		if inputMsg.gameId:
			print 'User has requested specific game with ID: %s' % (inputMsg.gameId)
			self.handleRequestToJoinSpecificGame(inputMsg, r)
		else:
			print 'User has requested to join any game of type: %s' % (inputMsg.gameType)
			possGames = self.games_pending[inputMsg.gameType]
			if possGames:
				print 'Game of type %s exists. Joining game now.' % (inputMsg.gameType)
				self.movePendingToPlay(possGames.pop(0), r)
			else:
				print 'Game of type %s does not exist yet. Creating a new game.' % (inputMsg.gameType)
				self.createNewGame(inputMsg, r)
	
	def handleRequestToJoinSpecificGame(self, inputMsg, r):
		game = None
		if inputMsg.gameType in self.games_pending:
			for x in self.games_pending[inputMsg.gameType]:
				if x.type == inputMsg.gameType:
					game = x
			if game:
				print 'Requested game available to join.'
				self.movePendingToPlay(game, r)
			else:
				error = mp.ResponseMessage("error", None, None, "Game with that ID does not exist.", None)
				self.sendMessage(r, error)
		else:
			error = mp.ResponseMessage("error", None, None, "Requested game type not supported.", None)
			self.sendMessage(r, error)

	def handleMove(self, inputMsg, r):
		if inputMsg.gameId in self.games_in_play:
			g = self.games_in_play[inputMsg.gameId]
			success, msg, hasWinner, isTied = g.move(inputMsg.move, r)
			if success:
				if hasWinner:
					winMsg = mp.ResponseMessage('gameover', g.id, g.gamestate, 'You have won.', None)
					loseMsg = mp.ResponseMessage('gameover', g.id, g.gamestate, 'You have lost.', None)
					self.sendMessage(g.getCurrPlayer(), loseMsg)
					self.sendMessage(g.getOtherPlayer(), winMsg)
					self.gameCleanup(g)
				else:
					if isTied:
						tiedMsg = mp.ResponseMessage('gameover', g.id, g.gamestate, 'Game is tied.', None)
						self.sendMessage(g.getCurrPlayer(), tiedMsg)
						self.sendMessage(g.getOtherPlayer(), tiedMsg)
						self.gameCleanup(g)
					else:
						announce = mp.ResponseMessage('announce', g.id, g.gamestate, 'Success.', g.getCurrPlayer())
						play = mp.ResponseMessage('play', g.id, g.gamestate, 'Play', g.getCurrPlayer())
						self.sendMessage(g.getCurrPlayer(), play)
						self.sendMessage(g.getOtherPlayer(), announce)
			else:
				error = mp.ResponseMessage('error', g.id, g.gamestate, msg, g.getOtherPlayer())
				self.sendMessage(r, error)
		else:
			error = mp.ResponseMessage('error', None, None, 'Cannot find game with that ID', None)
			self.sendMessage(r,error)

	def gameCleanup(self, g):
		del self.games_in_play[g.id]
