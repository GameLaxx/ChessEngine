from chess_game import ChessGame
import random

class ChessParams():
    def __init__(self,
        pawn_value = 1,
        bishop_value = 3,
        knight_value = 3,
        rook_value = 5,
        queen_value = 10,
        bishop_pair = 1,
        pawn_space = 0.1,
        pawn_center = 0.1,
        square_attacked = 0.1,
        king_safety = 0.01,
        check_mate = 100
        ):
        self.dict = {
            "pawn_value" : pawn_value,
            "bishop_value" : bishop_value,
            "knight_value" : knight_value,
            "rook_value" : rook_value,
            "queen_value" : queen_value,
            "bishop_pair" : bishop_pair,
            "pawn_space" : pawn_space,
            "pawn_center" : pawn_center,
            "square_attacked" : square_attacked,
            "king_safety" : king_safety,
            "check_mate" : check_mate
        }

class ChessBot():
    WHITE = 0
    BLACK = 1
    BOTH = 2
    def __init__(self, params = ChessParams(), debug = False):
        self.params = params.dict
        self.values = ["pawn_value", "knight_value", "bishop_value", "rook_value", "queen_value"]
        self.center_squares = 1 << 27 | 1 << 28 | 1 << 35 | 1 << 36
        self.debug = debug

    def __rule_material(self, bitboards, occupancy):
        ret = 0
        for piece in range(5):
            piece_white = self.current_board.count_piece_wholeboard(self.WHITE, piece)
            piece_black = self.current_board.count_piece_wholeboard(self.BLACK, piece)
            ret += self.params[self.values[piece]] * (piece_white - piece_black)
        return ret
    
    def __rule_pawnspace(self, bitboards, occupancy):
        white_pawn_squares = self.current_board.bitboard_to_squares(bitboards[self.WHITE][0])
        black_pawn_squares = self.current_board.bitboard_to_squares(bitboards[self.BLACK][0])
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
        nb_center_pawns_white = self.current_board.count_piece_bitboard(center_white_bb)
        nb_center_pawns_black = self.current_board.count_piece_bitboard(center_black_bb)
        return self.params["pawn_center"] * (nb_center_pawns_white - nb_center_pawns_black)
    
    def __rule_squareattacked(self, bitboards, occupancy):
        white_attacks = self.current_board.board_attacked(self.BLACK)
        black_attacks = self.current_board.board_attacked(self.WHITE)
        nb_attacks_white = self.current_board.count_piece_bitboard(white_attacks)
        nb_attacks_black = self.current_board.count_piece_bitboard(black_attacks)
        return self.params["square_attacked"] * (nb_attacks_white - nb_attacks_black)
    
    def __rule_kingsafety(self, bitboards, occupancy):
        white_attacks = self.current_board.board_attacked(self.BLACK)
        black_attacks = self.current_board.board_attacked(self.WHITE)
        count = 0
        for color in [self.WHITE,self.BLACK]:
            king_index = bitboards[color][self.current_board.KING].bit_length() - 1
            king_rank, king_file = divmod(king_index, 8)
            deltas = self.current_board.KING_DELTAS
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
        bishop_white = self.current_board.count_piece_wholeboard(self.WHITE, self.current_board.BISHOP)
        bishop_black = self.current_board.count_piece_wholeboard(self.BLACK, self.current_board.BISHOP)
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
    
    def evaluate(self):
        ret = None
        for move in self.current_board.get_moves(self.current_board.player_turn):
            self.current_board._move(move)
            score = self.assign_score(self.current_board.bitboards, self.current_board.occupancy)
            if ret == None:
                ret = score
                self.current_board._pop()
                continue
            if self.current_board.player_turn == self.BLACK:
                if ret > score:
                    ret = score
                self.current_board._pop()
                continue
            if ret < score:
                ret = score
            self.current_board._pop()
            continue
        if ret == None: # no response found ie check mate or draw
            winning = self.current_board.is_king_checked(self.current_board.player_turn)
            if winning:
                ret = - self.params["check_mate"] * (self.current_board.player_turn * 2 + 1)
            else:
                ret = 0
        return ret

    def make_decision(self, board : ChessGame):
        self.current_board = board
        moves = self.current_board.get_moves(self.current_board.player_turn)
        max_score = None
        to_play = []
        for move in moves:
            self.current_board._move(move)
            player_attacked = (self.current_board.player_turn + 1) % 2
            self.current_board.player_turn = player_attacked
            score = self.evaluate()
            if max_score == None:
                max_score = score
                to_play.append(move)
                self.current_board._pop()
                continue
            if score == max_score:
                to_play.append(move)
                self.current_board._pop()
                continue
            if player_attacked == self.BLACK:
                if max_score < score:
                    max_score = score
                    to_play = [move]
                self.current_board._pop()
                continue
            if max_score > score:
                max_score = score
                to_play = [move]
            self.current_board._pop()
            continue
        return random.choice(to_play)

