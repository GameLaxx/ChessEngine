from chess_game import ChessGame

class ChessBot():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    def __init__(self, chess_engine : ChessGame):
        self.chess_engine = chess_engine
        self.params = {
            "pawn_value" : 1,
            "bishop_value" : 3,
            "knight_value" : 3,
            "rook_value" : 5,
            "queen_value" : 10,
            "bishop_pair" : 1,
            "pawn_space" : 0.1,
            "pawn_center" : 0.1
        }
        self.values = ["pawn_value", "knight_value", "bishop_value", "rook_value", "queen_value"]
        self.center_squares = 1 << 27 | 1 << 28 | 1 << 35 | 1 << 36

    def __rule_material(self, bitboards, occupancy):
        ret = 0
        for piece in range(5):
            piece_white = self.chess_engine.count_piece_wholeboard(self.WHITE, piece, bitboards)
            piece_black = self.chess_engine.count_piece_wholeboard(self.BLACK, piece, bitboards)
            ret += self.params[self.values[piece]] * (piece_white - piece_black)
        return ret
    
    def __rule_pawnspace(self, bitboards, occupancy):
        white_pawn_squares = self.chess_engine.bitboard_to_squares(bitboards[self.WHITE][0])
        black_pawn_squares = self.chess_engine.bitboard_to_squares(bitboards[self.BLACK][0])
        white_space = 0
        black_space = 0
        for row, _ in white_pawn_squares:
            white_space += 7 - row
        for row, _ in black_pawn_squares:
            black_space += row
        return self.params["pawn_space"] * (white_space - black_space)
    
    def __rule_pawncenter(self, bitboards, occupancy):
        center_white_bb = bitboards[self.WHITE][0] & self.center_squares
        center_black_bb = bitboards[self.BLACK][0] & self.center_squares
        nb_center_pawns_white = self.chess_engine.count_piece_bitboard(center_white_bb)
        nb_center_pawns_black = self.chess_engine.count_piece_bitboard(center_black_bb)
        return self.params["pawn_center"] * (nb_center_pawns_white - nb_center_pawns_black)
    
    def __rule_bishoppair(self, bitboards, occupancy):
        bishop_white = self.chess_engine.count_piece_wholeboard(self.WHITE, self.chess_engine.BISHOP, bitboards)
        bishop_black = self.chess_engine.count_piece_wholeboard(self.BLACK, self.chess_engine.BISHOP, bitboards)
        if bishop_black == bishop_white:
            return 0
        if bishop_white == 2:
            return self.params["bishop_pair"]
        if bishop_black == 2:
            return -self.params["bishop_pair"]
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
        max_score = None
        to_play = None
        for move in moves:
            sim_bitboards = [row[:] for row in self.chess_engine.bitboards]
            sim_occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
            self.chess_engine.update_occupancy(sim_bitboards, sim_occupancy)
            self.chess_engine.move(move, sim_bitboards, sim_occupancy)
            score = self.evaluate(sim_bitboards, sim_occupancy)
            print(move, score)
            if max_score == None:
                max_score = score
                to_play = move
                continue
            if self.chess_engine.player_turn == self.BLACK:
                if max_score > score:
                    max_score = score
                    to_play = move
                continue
            if max_score < score:
                max_score = score
                to_play = move
            continue
        return to_play

