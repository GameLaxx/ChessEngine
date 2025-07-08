from chess_game import ChessGame

class ChessBot():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    def __init__(self, chess_engine : ChessGame, debug = False):
        self.chess_engine = chess_engine
        self.params = {
            "pawn_value" : 1,
            "bishop_value" : 3,
            "knight_value" : 3,
            "rook_value" : 5,
            "queen_value" : 10,
            "bishop_pair" : 1,
            "pawn_space" : 0.1,
            "pawn_center" : 0.1,
            "square_attacked" : 0.1,
            "king_safety" : 0.01,
            "check_mate" : 100
        }
        self.values = ["pawn_value", "knight_value", "bishop_value", "rook_value", "queen_value"]
        self.center_squares = 1 << 27 | 1 << 28 | 1 << 35 | 1 << 36
        self.debug = debug

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
    
    def __rule_squareattacked(self, bitboards, occupancy):
        white_attacks = self.chess_engine.board_attacked(bitboards, occupancy, self.BLACK)
        black_attacks = self.chess_engine.board_attacked(bitboards, occupancy, self.WHITE)
        nb_attacks_white = self.chess_engine.count_piece_bitboard(white_attacks)
        nb_attacks_black = self.chess_engine.count_piece_bitboard(black_attacks)
        return self.params["square_attacked"] * (nb_attacks_white - nb_attacks_black)
    
    def __rule_kingsafety(self, bitboards, occupancy):
        white_attacks = self.chess_engine.board_attacked(bitboards, occupancy, self.BLACK)
        black_attacks = self.chess_engine.board_attacked(bitboards, occupancy, self.WHITE)
        count = 0
        for color in [self.WHITE,self.BLACK]:
            king_index = bitboards[color][self.chess_engine.KING].bit_length() - 1
            king_rank, king_file = divmod(king_index, 8)
            deltas = self.chess_engine.KING_DELTAS
            for delta in deltas:
                neighbor_index = king_index + delta
                if not (0 <= neighbor_index < 64):
                    continue
                neighbor_rank, neighbor_file = divmod(neighbor_index, 8)
                if abs(king_rank - neighbor_rank) > 1 or abs(king_file - neighbor_file) > 1:
                    continue 
                if color == self.WHITE:
                    count += -1 if black_attacks & 1 << neighbor_index else 0
                else : 
                    count += 1 if white_attacks & 1 << neighbor_index else 0
        return self.params["king_safety"] * count
    
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
    
    def assign_score(self, bitboards, occupancy):
        ret = 0
        for name in dir(self):
            if name.startswith("_ChessBot__rule_"):
                func = getattr(self, name)
                if callable(func):
                    ret += func(bitboards, occupancy)
        return ret
    
    def evaluate(self, player_turn, bitboards, occupancy):
        ret = None
        for move in self.chess_engine.get_moves(bitboards, occupancy, (player_turn + 1) % 2):
            sim_bitboards = [row[:] for row in bitboards]
            sim_occupancy = {self.WHITE : 0, self.BLACK : 0, self.BOTH : 0}
            self.chess_engine.update_occupancy(sim_bitboards, sim_occupancy)
            self.chess_engine.move(move, sim_bitboards, sim_occupancy, sim_color=(player_turn + 1) % 2)
            score = self.assign_score(sim_bitboards, sim_occupancy)
            if ret == None:
                ret = score
                continue
            if player_turn == self.BLACK:
                if ret < score:
                    ret = score
                continue
            if ret > score:
                ret = score
            continue
        return ret

    def make_decision(self, board : ChessGame):
        moves = board.get_moves()
        max_score = None
        to_play = None
        for move in moves:
            sim_bitboards = [row[:] for row in board.bitboards]
            sim_occupancy = board.occupancy.copy()
            self.chess_engine.move(move, sim_bitboards, sim_occupancy)
            score = self.evaluate(board.player_turn, sim_bitboards, sim_occupancy)
            if score == None: # no response found ie check mate or pat
                winning = board.is_king_checked(sim_bitboards, sim_occupancy)
                if winning:
                    score = self.params["check_mate"] * (1 - board.player_turn * 2)
                else:
                    score = 0
            if max_score == None:
                max_score = score
                to_play = move
                continue
            if board.player_turn == self.BLACK:
                if max_score > score:
                    max_score = score
                    to_play = move
                continue
            if max_score < score:
                max_score = score
                to_play = move
            continue
        return to_play

