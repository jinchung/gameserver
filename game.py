""" 
Game Interface
"""

ID_GENERATOR = 0

class Game(object):

	def __init__(self, type, player):
		self.type = type
		self.id = generateNewId()
		self.players = []
		self.players.append(player)
		self.gamestate = ""
		self.currPlayerIndex = -1

	def getCurrPlayer(self):
		return self.players[self.currPlayerIndex]

	def getOtherPlayer(self):
		otherIndex = (self.currPlayerIndex + 1) % 2
		return self.players[otherIndex]

class TicTacToe(Game):
	
	def __init__(self, type, player):
		super(TicTacToe, self).__init__(type, player)
		self.playerMarkers = ['X', 'O']
		self.board = createBoard(3)
		self.updateGamestate()		
		self.totalMoves = 9

	def printBoard(self):
		for row in self.board:
			for val in row:
				print val
	
	def move(self, move, s):
		m = move.split()
		row = int(m[0])
		col = int(m[1])
		print self.getCurrPlayer()
		print s

		if self.getCurrPlayer() == s:
			if self.board[row][col] == '_':
				self.board[row][col] = self.getCurrPlayerMarker()
				self.totalMoves -= 1
				isWinner, isTied = self.checkForWinner(row, col)
				self.switchPlayer()
				self.updateGamestate()
				return (True, 'Success', isWinner, isTied)
			else: 
				return (False, 'Invalid move', False, False)
		else:
			return (False, 'User is not current player', False, False)

	def updateGamestate(self):
		state = ''
		for row in self.board:
			for val in row:
				state+=val
			state+=':'
		self.gamestate = state
		print 'game state is: ' + state

	def switchPlayer(self):
		self.currPlayerIndex = (self.currPlayerIndex + 1) % 2
	
	def checkForWinner(self, row, col):
		winner = True
		
		for c in range(0, 3):
			if self.board[row][c] != self.getCurrPlayerMarker():
				winner = False
				break

		if not winner:
			for r in range(0, 3):
				if self.board[r][col] != self.getCurrPlayerMarker():
					winner = False
					break

		if not winner:
			for i in range(0, 3):
				if self.board[i][i] != self.getCurrPlayerMarker():
					winner = False
					break

		if not winner:
			for j in range(0, 3):
				if self.board[j][2 - j] != self.getCurrPlayerMarker():
					winner = False
					break
		if not winner and self.totalMoves == 0:
			return winner, True 
		
		return winner, False			

	def getCurrPlayerMarker(self):
		return self.playerMarkers[self.currPlayerIndex]

class Go(Game):

	def __init__(self, type, player):
		super(self).__init__(type, player)
		self.board = createBoard(3)

def createBoard(size):
    board = []
    for i in range(0, size):
		board.append([])
		for j in range(0, size):
			board[i].append('_')
    return board

def buildNewGame(type, s):
	if type == 'tictactoe':
		return TicTacToe(type, s)
	else: return Go(type, s)

def generateNewId():
	global ID_GENERATOR
	ID_GENERATOR += 1
	return ID_GENERATOR		
