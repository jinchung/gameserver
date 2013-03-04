Server (socket) logic is under serverhandler.py

This is separate from the controller that manages game sessions and users (gameinterface.py)

To start:

python serverhandler.py

On a separate client, connect to port 8888
Messages are in json format: 
For socket s: 
s.send("{'type': 'new', 'gameId': None, 'gameType': 'tictactoe', 'move': None}")
s.send("{'type': 'move', 'gameId': 1, 'gameType': 'tictactoe', 'move': '1 1'}")

type: new, move
gameId: sent back from server once game is created
move: x and y coordinates sent as 'x y' 
gameType: tictactoe
