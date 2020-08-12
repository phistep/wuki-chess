import pytest
from ..board import Color, White, Black, Square, BOARD_LEN, within_board, Board
from ..pieces import Piece, Queen

def test_Color_constants():
    white = Color(Color.WHITE)
    black = Color(Color.BLACK)
    assert white == White
    assert black == Black

def test_Color_negation():
    assert ~White == Black
    assert ~Black == White
    assert White != Black

def test_Color_str():
    assert str(White) == 'w'
    assert str(Black) == 'b'

def test_Color_repr():
    assert repr(White) == '<White>'
    assert repr(Black) == '<Black>'


def test_Square_init_num():
    sq = Square(2,3)
    assert sq.x == 2
    assert sq.y == 3

def test_Square_init_num_tuple():
    sq = Square((2,3))
    assert sq.x == 2
    assert sq.y == 3

def test_Square_init_rank_file():
    sq = Square('c',4)
    assert sq.x == 2
    assert sq.y == 3

def test_Square_init_rank_file_tuple():
    sq = Square(('c',4))
    assert sq.x == 2
    assert sq.y == 3

def test_Square_init_from_Square():
    sq = Square(4,5)
    sq2 = Square(sq)
    assert sq2.x == sq.x
    assert sq2.y == sq.y

def test_Square_init_no_tuple():
    with pytest.raises(ValueError):
        Square('a')

def test_Square_init_wrong_format():
    with pytest.raises(ValueError):
        Square(2, 'a')
    with pytest.raises(ValueError):
        Square('a', '2')

def test_Square_file_rank():
    sq = Square('c',4)
    file_, rank = sq.file_rank()
    assert file_ == 'c'
    assert rank == 4

def test_Square_coords():
    assert Square(4,5).coords() == (4,5)

def test_Square_str():
    assert str(Square(('c',4))) == 'c4'

def test_Square_repr():
    assert repr(Square(('c',4))) == '<Square c4 x=2 y=3>'

def test_Square_hash():
    assert {Square(0,0): 1}

def test_Square_eq():
    assert Square(2,3) == Square(2,3)

def test_Square_eq_tuple():
    assert Square(3,5) == (3,5)
    assert Square('d',2) == (3,1)

def test_Square_eq_incompatible():
    with pytest.raises(TypeError):
        Square(3,4) == (3,4,True)
    with pytest.raises(TypeError):
        Square(3,4) == '34'

def test_Square_add():
    x,y = pos = (3,4)
    dx, dy = diff = (2,3)
    assert Square(pos) + diff == Square(x+dx, y+dy)

def test_Square_add_incompatible():
    with pytest.raises(TypeError):
        Square(0,0) + Square(1,1)
    with pytest.raises(TypeError):
        Square(0,0) + (1,2,3)

def test_Square_within_board():
    assert Square('c',4).within_board() == True

def test_Square_out_of_board():
    assert Square(-1,0).within_board() == False

def test_within_board():
    assert within_board('b',1) == True

def test_within_board_Square_init():
    assert within_board(Square('d', 5)) == True

def test_Square_color():
    assert Square('a',1).color() == Black
    assert Square('b',1).color() == White
    assert Square('h',8).color() == Black

def test_Square_diagonals():
    assert Square('g',2).diagonals() == set([Square('f',1), Square('g',2), Square('h',3), Square('a',8),Square('b',7), Square('c',6), Square('d',5), Square('e',4), Square('f',3), Square('h',1)])
    assert Square('b',5).diagonals() == set([Square('a',4), Square('b',5), Square('c',6), Square('d',7),Square('e',8), Square('a',6), Square('c',4), Square('d',3), Square('e',2), Square('f',1)])

def test_Square_orthogonals():
    sq = Square('c', 7)
    assert sq.orthogonals() == set([Square(x, sq.y) for x in range(BOARD_LEN)]) | set([Square(sq.x, y) for y in range(BOARD_LEN)])

