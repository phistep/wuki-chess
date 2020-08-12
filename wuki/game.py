import re

from . import piece
from .board import White, Black, Square, Board

class Game:
    def __init__(self, moves):
        """Create a game from an array of algebraic notation moves

        :param moves: array of moves in [algebraic notation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess))
        """
        self.moves = moves
        # TODO figure out from game state
        self.own_color = White

        initial_pieces = []
        for color, row, direction in zip([White, Black], [1, 8], [+1, -1]):
            initial_pieces.extend([
                piece.Piece(piece.Rook(),   color, Square('a', row)),
                piece.Piece(piece.Knight(), color, Square('b', row)),
                piece.Piece(piece.Bishop(), color, Square('c', row)),
                piece.Piece(piece.King(),   color, Square('e', row)),
                piece.Piece(piece.Queen(),  color, Square('d', row)),
                piece.Piece(piece.Bishop(), color, Square('f', row)),
                piece.Piece(piece.Knight(), color, Square('g', row)),
                piece.Piece(piece.Rook(),   color, Square('h', row)),
            ])
            initial_pieces.extend([piece.Piece(piece.Pawn(color), color, Square(col, row+direction)) for col in "abcdefgh"])
        self.boards = [Board(initial_pieces)]


    def __repr__(self):
        return f"<Game moves={len(self.moves)} own_color={sefl.own_color}>"

    def __str__(self):
        """Algebraic notation of the whole game"""
        return '\n'.join(self.moves)

    def print_current_board(self, unicode=True, inverted=False):
        self.boards[-1].print(unicode)
