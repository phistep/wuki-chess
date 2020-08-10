

# TODO
# - general
#   - this todo list into README.md
#   - use exceptions to handle capturing, promotion, castling, check, checkmate?
#   - should AbstractPiece.possible_moves() check for opponent pieces or one layer above?
#   - PiecePosition/Square
#       - __add__, __sub__, with tuples
#       - .diagonals(), .orthogonals() etc
#       - automatic bounds check
#       - to/from python/chess coordinates
#       - color
#       - rows/cols -> ranks/files https://www.dummies.com/games/chess/naming-ranks-and-files-in-chess/
#   - separate files
#       - Game, PlayerColor -> game.py
#       - Board, PiecePosition/Sqaure -> board.py
#       - Piece, AbstractPiece, King, Queen, ... -> piece.py
#       - AI into own file and class, gets Game, returns Game/move string
# - rules
#   - en passent
#   - pawn promotion
#   - castling (add .touched attribute to Piece(), also simplifies pawn initial two square movement)
# - parse game file
#   - setup initial board 
#   - store all pieces and their positions (build index)
#   - regex parse each move line
#   - move each piece (check validity) (pawn promotion, castling, en passent)
#   - store each board position separately
# - find next move
#   - go through all own pieces and generate list of all possible moves and board positions
#       - remove moves that land on pieces that are on the board from the list returned by Piece.possible_moves()
#       - add castling if possible (goes in Board())
#       - handle pawn promotion (goes in Piece() and Pawn()?
#           .move_to() in Piece() calls self.piece.move_to()
#            AbstractPiece.move_to() just pass in other piece types, raises PawnPromotionException
#   - lookahead
#   - evaluation function for each board position
#       - implement each as own function, sum total score,
#       - allow black/whitelist for strategies
#       - allow to pass list of custom strategy functions
#           - check
#           - checkmate
#           - capturing
#           - pawn promotion
#           - double pawns
#           - attacks
#           - cover
# - visualization
#   - unicode for TUI
#   - matplotlib for pdf game output
# - package
#   - sphinx docs
#   - automated tests
#   - actual python package structure + executables
#       - helpers.py -> common.py
#       - __init__ only contains loading code, separate program from library
#       - dependencies, installer

import re

import pieces
from helpers import BOARD_LEN, White, Black, coord, square_color

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
                Piece(pieces.Rook(),   color, coord('a', row)),
                Piece(pieces.Knight(), color, coord('b', row)),
                Piece(pieces.Bishop(), color, coord('c', row)),
                Piece(pieces.King(),   color, coord('e', row)),
                Piece(pieces.Queen(),  color, coord('d', row)),
                Piece(pieces.Bishop(), color, coord('f', row)),
                Piece(pieces.Knight(), color, coord('g', row)),
                Piece(pieces.Rook(),   color, coord('h', row)),
            ])
            initial_pieces.extend([Piece(pieces.Pawn(color), color, coord(col, row+direction)) for col in "abcdefgh"])
        self.boards = [Board(initial_pieces)]


    def __repr__(self):
        return f"<Game moves={len(self.moves)} own_color={sefl.own_color}>"

    def __str__(self):
        """Algebraic notation of the whole game"""
        return '\n'.join(self.moves)

    def print_current_board(self, unicode=True, inverted=False):
        self.boards[-1].print(unicode)


class Piece:
    """Instantiation of general piece type on the board"""

    def __init__(self, piece, color, position):
        self.name = piece.name
        self.color = color
        self.letter = piece.letter.upper() if color is White else piece.letter.lower()
        self.symbol = piece.symbol[color]
        self._piece_moves = piece.possible_moves
        self.position = position

    def __str__(self):
        return f"{self.letter}{''.join([str(x) for x in _square(self.position)])}"

    def __repr__(self):
        return f"<{self.name} color={self.color} position={self.position}>"

    def possible_moves(self, position=None):
        if position:
            return self._piece_moves(position)
        else:
            return self._piece_moves(self.position)


class Board:
    """Stores a board position"""
    # TODO implement self.__getitem__ for self.index lookup https://docs.python.org/3/reference/datamodel.html#object.__getitem__
    # TODO implement __contains__ for positions (piece @ position) and pieces (kind of piece still on board?)
    # TODO implement __iter__ over all pieces
    # TODO implement iterator over all squares

    def __init__(self, pieces):
        """Build the board from a list of pieces

        :param pieces: list of pieces on the board
        """
        self.pieces = pieces
        self.index = {}
        for piece in pieces:
            self.index[piece.position] = piece

    def __repr__(self):
        return f"<Board pieces={len(self.pieces)}>"

    def __str__(self):
        return self.__repr__

    def print(self, unicode=True):
        """Print the board

        :param unicode: use unicode symbols

        """
        # TODO
        # - :param inverted: invert colors for unicode (useful for White-on-Black terminals)
        # - for interactive mode, print up-side-down

        print('  abcdefgh')
        for y in reversed(range(BOARD_LEN)):
            print(y+1, end=' ')
            for x in range(BOARD_LEN):
                pos = (x,y)
                if pos in self.index:
                    if unicode:
                        symbol = self.index[pos].symbol
                    else:
                        symbol = self.index[pos].letter
                else:
                    if unicode:
                        symbol = '█' if square_color(pos) is Black else ' '
                    else:
                        symbol = '#' if square_color(pos) is Black else ' '
                print(symbol, end='')
            print('', y+1)
        print('  abcdefgh')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Wuki chess engine')
    parser.add_argument('match_file', type=str, help="Match file containing all previous moves in chess notation")
    parser.add_argument('-m', '--move', action='store_true',
            help='Make a move and store it into the match file')
    #parser.add_argument('-g', '--graphics', action='store_true',
    #        help='Print terminal graphics')
    #parser.add_argument('-p', '--plot', action='store_true',
    #        help='Generate visual representation of the game in match file')
    #parser.add_argument('-i', '--interactive', action='store_true',
    #        help='Take opponent moves for STDIN')
    #parser.add_argument('-I', '--inverted-colors', action='store_true',
    #        help='Print symbols in inverted colors for White-on-Black terminals')
    parser.add_argument('-a', '--ascii', action='store_true',
            help='Use ascii characters and letters instead of unicode chess symbols')
    args = parser.parse_args()

    with open(args.match_file) as match_file:
        # split lines into list elements and remove empty lines
        moves = list(filter(None, match_file.read().split('\n')))
        game = Game(moves)
        print(game)
        print()
        game.print_current_board(unicode=not args.ascii)
