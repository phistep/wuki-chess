from helpers import within_board, WHITE, BLACK

class AbstractPiece:
    """General type of a piece"""
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Piece {self.letter}:{self.name}>"

    def possible_moves(self, position):
        raise NotImplemented


class King(AbstractPiece):
    def __init__(self):
        self.name = "King"
        self.letter = 'K'
        self.symbol = {WHITE:'♔', BLACK:'♚'}

    def possible_moves(self, position):
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
    def __init__(self):
        self.name = "Queen"
        self.letter = 'Q'
        self.symbol = {WHITE:'♕', BLACK:'♛'}


class Rook(AbstractPiece):
    def __init__(self):
        self.name = "Rook"
        self.letter = 'R'
        self.symbol = {WHITE:'♖', BLACK:'♜'}


class Bishop(AbstractPiece):
    def __init__(self):
        self.name = "Bishop"
        self.letter = 'B'
        self.symbol = {WHITE:'♗', BLACK:'♝'}


class Knight(AbstractPiece):
    def __init__(self):
        self.name = "Knight"
        self.letter = 'N'
        self.symbol = {WHITE:'♘', BLACK:'♞'}


class Pawn(AbstractPiece):
    def __init__(self, color):
        self.name = "Pawn"
        self.letter = 'P'
        self.color = color
        self.symbol = {WHITE:'♙', BLACK:'♟'}

    def possible_moves(self, position):
        # TODO en passent
        distance = [1]
        if self.color is WHITE:
            direction = +1
            if position[1] == 1:
                distance.append(2)
        else:
            direction = -1
            if position[1] == 6:
                distance.append(2)
        return [(position[0], position[1]+direction*dist) for dist in distance]

