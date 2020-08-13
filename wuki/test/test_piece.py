from .. import piece
from ..board import White, Black, Square

def test_AbstractPiece_eq():
    assert piece.King() == piece.King()
    assert piece.King() != piece.Queen()

def test_AbstractPiece_eq_Piece():
    assert piece.King() == piece.Piece(piece.King(), White, Square(0,0))
    assert piece.King() != piece.Piece(piece.Queen(), White, Square(0,0))


def test_King_init():
    king = piece.King()
    assert king.name == "King"
    assert king.letter == 'K'
    assert king.symbol[White] == '♔'
    assert king.symbol[Black] == '♚'

def test_King_possible_moves():
    king = piece.King()
    assert king.possible_moves(Square(4,4)) == set([(3,4), (5,4), (4,3), (4,5), (3,3), (5,5), (3,5), (5,3)])
    assert king.possible_moves(Square(0,4)) == set([(0,3), (0,5), (1,3), (1,4), (1,5)])
    assert king.possible_moves(Square(7,7)) == set([(7,6), (6,7), (6,6)])
