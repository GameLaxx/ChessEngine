from chess_game import ChessGame

class ChessBot():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    def __init__(self, chess_engine : ChessGame):
        self.chess_engine = chess_engine

    def evaluate(self, bitboards, occupancy):
        pass

    def make_decision(self, bitboards):
        occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
        self.chess_engine.update_occupancy(bitboards, occupancy)
        moves = self.chess_engine.get_moves(bitboards, occupancy)
        print(moves)
    