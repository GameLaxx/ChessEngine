from chess_game import ChessGame
from chess_render import ChessRender

board = ChessGame()
board.pop_piece(0, 5, board.square_to_index("e1"))
print(board)
# render = ChessRender(board)

# render.update()
