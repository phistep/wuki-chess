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

    def __hash__(self):
        return hash(self.name)

    def legal_moves(self, position, board=None):
        """Returns a list of possible moves of the piece. Some pieces need
        information about the board for this.

        :param Square position: the position on the board from which the move
            shall be made
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
        if not isinstance(position, Square):
            position = Square(position)
        if not position.within_board():
            raise ValueError("Piece can only be initialized on a square within the board")
        self.position = position

    def __str__(self):
        return str(self.position)+self.letter

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

    def __hash__(self):
        return hash((self.letter, self.color, self.position))

    def possible_moves(self, board):
        """Returns a list of possible moves of the piece. All legal moves
        within the movement pattern of the respective piece are considered.
        All squares that are blocked off by other pieces are removed.

        :param Board board: the board on which the piece needs to find its
            possible moves

        :returns moves: a list of Sqaures that the piece could move to
        """
        mover = self.position
        legal_moves = self.piece.legal_moves(self.position, board)
        possible_moves = legal_moves.copy()
        # own pieces cannot by captured
        possible_moves = set([s for s in possible_moves if (s in board and board[s].color is not self.color) or s not in board])
        if self == Knight():
            # Knights don't get blocked by other pieces
            pass
        elif self == King():
            # TODO Kings can castle under specific circumstances
            # Kings cannot move themselves into check
            for square_in_check in board.possible_moves(~self.color, give_check=True):
                possible_moves.discard(square_in_check)
            try:
                # treat opponent King separately to avoid infinite recursion
                # use opponent's King's `.legal_moves` instead of possible_moves
                # to avoid recursion. Wether blocked or not, two Kings can
                # never sit adjacent.
                opponent_king = [p for p in board.pieces(King()) if p.color is not self.color][0]
                for square_in_check in opponent_king.piece.legal_moves(opponent_king.position, board):
                    possible_moves.discard(square_in_check)
            except:
                # Board has no opponent King. While not being legal, this can
                # happend for debug/testing purposes and we don't care
                pass
        elif self == Pawn(self.color):
            # Pawns cannot capture where they walk, opponent pieces block them
            one_step = self.position + (0, 1*self.color.direction)
            two_step = self.position + (0, 2*self.color.direction)
            if one_step in board:
                possible_moves.discard(one_step)
                # if square in front is taken, pawn cann also not walk two steps
                possible_moves.discard(two_step)
            if two_step in board:
                possible_moves.discard(two_step)
        else:
            # remove orthogonally and diagonally blocked squares for all other
            # pieces, opponent pieces block, but can be captured
            for blocker in [s for s in legal_moves if s in board]:
                for blocked in [s for s in legal_moves if s.blocked_by(mover, blocker)]:
                    possible_moves.discard(blocked)
        return possible_moves

    def move_to(self, target, board):
        """Does not mutate but returns new piece

        :param target: the aquare the pieces should be moved to

        :returns new_piece: new piece object at the updated position

        :raises IllegalMoveError: if move is not possible for te piece
        """
        if target not in self.possible_moves(board):
            raise IllegalMoveError(str(self)+str(target))
        return Piece(self.piece, self.color, target)


class King(AbstractPiece):
    """King moves one square in any direction (orthogonally and diagonally)."""

    def __init__(self):
        self.name = "King"
        self.letter = 'K'
        self.symbol = {White:'♔', Black:'♚'}

    def legal_moves(self, position, board=None):
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

    def legal_moves(self, position, board=None):
        moves = position.diagonals() | position.orthogonals()
        moves.discard(position)
        return moves


class Rook(AbstractPiece):
    """Rook moves any number of squares orthogonally."""

    def __init__(self):
        self.name = "Rook"
        self.letter = 'R'
        self.symbol = {White:'♖', Black:'♜'}

    def legal_moves(self, position, board=None):
        moves = position.orthogonals()
        moves.discard(position)
        return moves


class Bishop(AbstractPiece):
    """Bishop moves any number of squares diagonally."""

    def __init__(self):
        self.name = "Bishop"
        self.letter = 'B'
        self.symbol = {White:'♗', Black:'♝'}

    def legal_moves(self, position, board=None):
        moves = position.diagonals()
        moves.discard(position)
        return moves


class Knight(AbstractPiece):
    """Knight moves two squares orthogonally and then one square in the other orthogonal direction."""

    def __init__(self):
        self.name = "Knight"
        self.letter = 'N'
        self.symbol = {White:'♘', Black:'♞'}

    def legal_moves(self, position, board=None):
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
    def __init__(self, color):
        self.name = "Pawn"
        self.letter = 'P'
        self.color = color
        self.symbol = {White:'♙', Black:'♟'}

    def __repr__(self):
        return super().__repr__()[:-1]+f" color={self.color}>"

    def __hash__(self):
        return hash((self.name, self.color))

    def legal_moves(self, position, board, only_attacked=False):
        """:param bool only_attacked: outputs only the attacked squares which the
            pawn could capture and not the ones it could move to (for all other
            pieces the two sets are idential)
        """
        # TODO en passent
        # TODO promotion (raise exception?)
        captures = [position + (d, self.color.direction) for d in [-1,+1]]
        if only_attacked:
            return set(filter(within_board, captures))
        captures = [sq for sq in captures if sq in board and board[sq].color is not self.color]

        distance = [1]
        if position.y == (~self.color).home_y: # opponent row
            # opponent home row, pawn promotion
            return set([])
        if position.y == self.color.home_y+self.color.direction:
            # starting row, can move two squares
            distance.append(2)
        moves = [position + (0, self.color.direction*dist) for dist in distance]
        moves = set(filter(within_board, moves+captures))
        return moves

