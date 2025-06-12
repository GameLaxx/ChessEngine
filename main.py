from chess_game import ChessGame
from chess_render import ChessRender

board = ChessGame()
render = ChessRender(board)

render.update()
