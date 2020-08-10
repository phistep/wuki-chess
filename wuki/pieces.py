from helpers import White, Black, within_board, diagonals, orthogonals, square

class AbstractPiece:
    """General type of a piece"""
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Piece {self.letter}:{self.name}>"

    def possible_moves(self, position, board=None):
        """Returns a set of new possible positions."""
        raise NotImplemented


class King(AbstractPiece):
    """King moves one square in any direction (orthogonally and diagonally)."""

    def __init__(self):
        self.name = "King"
        self.letter = 'K'
        self.symbol = {White:'♔', Black:'♚'}

    def possible_moves(self, position, board=None):
        moves = [
            (position[0]+1, position[1]),
            (position[0]-1, position[1]),
            (position[0]  , position[1]+1),
            (position[0]  , position[1]-1),

            (position[0]+1, position[1]+1),
            (position[0]-1, position[1]+1),
            (position[0]+1, position[1]-1),
            (position[0]-1, position[1]-1),
        ]
        moves = list(filter(within_board, moves))
        return moves


class Queen(AbstractPiece):
    """Queen moves any number of squares in any direction (orthogonally and diagonally)."""

    def __init__(self):
        self.name = "Queen"
        self.letter = 'Q'
        self.symbol = {White:'♕', Black:'♛'}

    def possible_moves(self, position, board=None):
        moves = diagonals(position) + orthogonals(position)
        moves.discard(position)
        return moves


class Rook(AbstractPiece):
    """Rook moves any number of squares orthogonally."""

    def __init__(self):
        self.name = "Rook"
        self.letter = 'R'
        self.symbol = {White:'♖', Black:'♜'}

    def possible_moves(self, position, board=None):
        return orthogonals(position).discard(position)


class Bishop(AbstractPiece):
    """Bishop moves any number of sqaures diagonally."""

    def __init__(self):
        self.name = "Bishop"
        self.letter = 'B'
        self.symbol = {White:'♗', Black:'♝'}

    def possible_moves(self, position, board=None):
        return diagonals(position).discard(position)


class Knight(AbstractPiece):
    """Knight moves two squares orthogonally and then one square in the other orthogonal direction."""

    def __init__(self):
        self.name = "Knight"
        self.letter = 'N'
        self.symbol = {White:'♘', Black:'♞'}

    def possible_moves(self, position, board=None):
        verticals   = [(position[0]+step, position[1])      for step in [-2,+2]]
        horizontals = [(position[0],      position[1]+step) for step in [-2,+2]]
        moves  = [(pos[0],      pos[1]+step) for pos in verticals   for step in [-1,+1]]
        moves += [(pos[0]+step, pos[1])      for pos in horizontals for step in [-1,+1]]
        moves = list(filter(within_board, moves))
        return moves


class Pawn(AbstractPiece):
    """Pawn moves one square forward depending on its color.
    If it has not moved yet, it may instead move two sqaures.
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
        if position[1] == opponent_row:
            return []
        if position[1] == starting_row:
            # starting row, can move two squares
            distance.append(2)
        moves = [(position[0], position[1]+direction*dist) for dist in distance]
        # TODO test capturing
        captures = [(position[0]+d, position[1]+direction) for d in [-1,+1]]
        captures = list(filter(lambda p: p in board and p.color is not self.color, captures))
        moves = set(filter(within_board, moves+captures))
        return moves

