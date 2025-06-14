from chess_game import ChessGame

class ChessBot():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    def __init__(self, chess_engine : ChessGame):
        self.chess_engine = chess_engine
        self.params = {}

    def __rule_pawnspace(self, bitboards, occupancy):
        print("Rule space")
        return 0
    def __rule_bishoppair(self, bitboards, occupancy):
        print("Rule bishop")
        return 0

    def evaluate(self, bitboards, occupancy):
        ret = 0
        for name in dir(self):
            if name.startswith("_ChessBot__rule_"):
                func = getattr(self, name)
                if callable(func):
                    ret += func(bitboards, occupancy)
        return ret

    def make_decision(self, bitboards):
        occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
        self.chess_engine.update_occupancy(bitboards, occupancy)
        moves = self.chess_engine.get_moves(bitboards, occupancy)
        print(moves)
    