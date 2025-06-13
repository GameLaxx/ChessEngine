from chess_game import ChessGame
from chess_render import ChessRender

board = ChessGame()
print(board)
print(board.get_moves())
render = ChessRender(board)

render.update()
