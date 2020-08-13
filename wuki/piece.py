from .board import White, Black, Square, within_board
from .errors import IllegalMoveError

class AbstractPiece:
    """General type of a piece"""
    def __init__(self):
        """sets .name, .letter, .symbol map, .color"""
        raise NotImplementedError # pragma: no cover

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<AbstractPiece {self.name} ({self.letter})>"

    def __eq__(self, other):
        if isinstance(other, AbstractPiece):
            return self.name == other.name
        else:
            raise TypeError("Can only compare AbstractPiece with another AbstractPiece")

    def possible_moves(self, position, board=None):
        """Returns a list of possible moves of the piece. Some pieces need
        information about the board for this.

        :param Board board: the board on which the piece needs to find its
            possible moves

        :returns moves: a list of Sqaures that the piece could move to
        """
        raise NotImplementedError # pragma: no cover


class Piece(AbstractPiece):
    """Instantiation of general piece type on the board"""

    def __init__(self, piece, color, position):
        """A new piece on the board.

        :param AbstractPiece piece: the kind of piece
        :param Color color: its color
        :param Square square: its position on the board
        """
        self.piece = piece
        self.name = piece.name
        self.color = color
        self.letter = piece.letter.upper() if color is White else piece.letter.lower()
        self.symbol = piece.symbol[color]
        self._piece_moves = piece.possible_moves
        if not isinstance(position, Square):
            position = Square(position)
        if not position.within_board():
            raise ValueError("Piece can only be initialized on a square within the board")
        self.position = position

    def __str__(self):
        return self.letter+str(self.position)

    def __repr__(self):
        return f"<{self.name} color={self.color} position={self.position}>"

    def __eq__(self, other):
        """Two Pieces have to be of the same kind, color and on the same
        position on the board. A Piece and an AbstractPiece have to share the
        type.
        """
        if isinstance(other, Piece):
            return self.name == other.name and self.position == other.position and self.color == other.color
        elif isinstance(other, AbstractPiece):
            return self.name == other.name
        else:
            raise TypeError("Piece can only be compared with Piece or AbstractPiece")

    def possible_moves(self, board=None):
        """Returns a list of possible moves of the piece. Some pieces need
        information about the board for this.

        :param Board board: the board on which the piece needs to find its
            possible moves

        :returns moves: a list of Sqaures that the piece could move to
        """
        return self._piece_moves(self.position, board=board)

    def move_to(self, target):
        """Does not mutate but returns new piece

        :param target: the aquare the pieces should be moved to

        :returns new_piece: new piece object at the updated position

        :raises IllegalMoveError: if move is not possible for te piece
        """
        if target not in self.possible_moves():
            raise IllegalMoveError
        return Piece(self.piece, self.color, target)


class King(AbstractPiece):
    """King moves one square in any direction (orthogonally and diagonally)."""

    def __init__(self):
        self.name = "King"
        self.letter = 'K'
        self.symbol = {White:'♔', Black:'♚'}

    def possible_moves(self, position, board=None):
        moves = [
            position + (+1,  0),
            position + (-1,  0),
            position + ( 0, +1),
            position + ( 0, -1),

            position + (+1, +1),
            position + (-1, +1),
            position + (+1, -1),
            position + (-1, -1),
        ]
        moves = set(filter(within_board, moves))
        return moves


class Queen(AbstractPiece):
    """Queen moves any number of squares in any direction (orthogonally and diagonally)."""

    def __init__(self):
        self.name = "Queen"
        self.letter = 'Q'
        self.symbol = {White:'♕', Black:'♛'}

    def possible_moves(self, position, board=None):
        moves = position.diagonals() | position.orthogonals()
        moves.discard(position)
        return moves


class Rook(AbstractPiece):
    """Rook moves any number of squares orthogonally."""

    def __init__(self):
        self.name = "Rook"
        self.letter = 'R'
        self.symbol = {White:'♖', Black:'♜'}

    def possible_moves(self, position, board=None):
        moves = position.orthogonals()
        moves.discard(position)
        return moves


class Bishop(AbstractPiece):
    """Bishop moves any number of squares diagonally."""

    def __init__(self):
        self.name = "Bishop"
        self.letter = 'B'
        self.symbol = {White:'♗', Black:'♝'}

    def possible_moves(self, position, board=None):
        moves = position.diagonals()
        moves.discard(position)
        return moves


class Knight(AbstractPiece):
    """Knight moves two squares orthogonally and then one square in the other orthogonal direction."""

    def __init__(self):
        self.name = "Knight"
        self.letter = 'N'
        self.symbol = {White:'♘', Black:'♞'}

    def possible_moves(self, position, board=None):
        verticals   = [position + (step, 0)      for step in [-2,+2]]
        horizontals = [position + (0, step) for step in [-2,+2]]
        moves  = [pos + (0, step) for pos in verticals   for step in [-1,+1]]
        moves += [pos + (step, 0) for pos in horizontals for step in [-1,+1]]
        moves = set(filter(within_board, moves))
        return moves


class Pawn(AbstractPiece):
    """Pawn moves one square forward depending on its color.
    If it has not moved yet, it may instead move two squares.
    It can move one square diagonally if its captuiring an opponent's pieces by doing so.
    If it reaches its respecitve last row, it can be promoted to any other piece.
    """
    # TODO add color to super().__repr__()

    def __init__(self, color):
        self.name = "Pawn"
        self.letter = 'P'
        self.color = color
        self.symbol = {White:'♙', Black:'♟'}

    def possible_moves(self, position, board):
        # TODO en passent
        # TODO promotion (raise exception?)
        # TODO two square movement not allowed when blocked by piece
        distance = [1]
        # TODO move this into PlayerColor? or Square/PiecePosition?
        if self.color is White:
            direction = +1
            opponent_row = 7
            starting_row = 1
        else:
            direction = -1
            opponent_row = 0
            starting_row = 6
        if position.y == opponent_row:
            return set([])
        if position.y == starting_row:
            # starting row, can move two squares
            distance.append(2)
        moves = [position + (0, direction*dist) for dist in distance]
        captures = [position + (d, direction) for d in [-1,+1]]
        captures = list(filter(lambda p: p in board and p.color is not self.color, captures))
        moves = set(filter(within_board, moves+captures))
        return moves

