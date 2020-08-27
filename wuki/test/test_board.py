import pytest
from math import sqrt

from ..board import Color, White, Black, Square, BOARD_LEN, within_board, Board
from ..piece import Piece, Queen, King, Pawn, Rook
from ..exceptions import IllegalMoveError

from .test_piece import castling_board

def test_Color_constants():
    white = Color(Color.WHITE)
    black = Color(Color.BLACK)
    assert white == White
    assert black == Black

def test_Color_attributes():
    assert White.direction == +1
    assert White.home_y == 0
    assert Black.direction == -1
    assert Black.home_y == BOARD_LEN-1

def test_Color_negation():
    assert ~White == Black
    assert ~Black == White
    assert White != Black

def test_Color_str():
    assert str(White) == 'white'
    assert str(Black) == 'black'

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

def test_Square_init_single_str():
    Square('a4')

def test_Square_init_malformed():
    with pytest.raises(ValueError):
        Square([int])
    with pytest.raises(ValueError):
        Square('z', 5)

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

def test_Square_dist():
    assert Square(0,0).dist(Square(1,0)) == 1.
    assert Square(0,0).dist(Square(0,3)) == 3.
    assert Square(0,0).dist(Square(5,5)) == 5*sqrt(2)

def test_Square_dist_cast():
    assert Square(0,0).dist((1,0)) == 1.
    with pytest.raises(TypeError):
        Square(0,0).dist("string")

def test_Square_blocket_by_ortho():
    board = Board([])
    mover = Square(3,3)
    blocker = Square(3,5)
    blocked = set([square for square, _ in board if square.blocked_by(mover, blocker)])
    assert blocked == set([Square(3,6), Square(3,7)])
    blocker = Square(2,3)
    blocked = set([square for square, _ in board if square.blocked_by(mover, blocker)])
    assert blocked == set([Square(1,3), Square(0,3)])

def test_Square_blocket_by_diag():
    board = Board([])
    mover = Square(3,3)
    blocker = Square(5,5)
    blocked = set([square for square, _ in board if square.blocked_by(mover, blocker)])
    assert blocked == set([Square(6,6), Square(7,7)])
    blocker = Square(1,1)
    blocked = set([square for square, _ in board if square.blocked_by(mover, blocker)])
    assert blocked == set([Square(0,0)])

def test_Board_init():
    pos = Square('d', 5)
    queen = Piece(Queen(), White, pos)
    captive = Piece(Pawn(White), White, pos+(1,1))
    board = Board([queen], captured={White:set([captive]), Black:set()})
    assert board._pieces == {queen}
    assert board.index == {pos:queen}
    assert board.captured[White] == set([captive])

def test_Board_repr():
    assert repr(Board([Piece(Queen(), White, Square('d', 5))])) == '<Board pieces=1 {<Queen color=white position=d5>}>'

def test_Board_str():
    pieces = {Piece(Queen(), White, Square('d', 5))}
    assert str(Board(pieces)) == str(pieces)

def test_Board_eq():
    pieces = [Piece(Queen(), White, Square('a', 3)), Piece(Queen(), Black, Square('b', 3))]
    board = Board(pieces)
    assert board == Board(pieces)
    assert board != Board(pieces[:1])

    board.capture(pieces[0])
    assert board != Board(pieces)
    board2 = Board(pieces)
    board2.capture(pieces[0])
    assert board == board2

def test_Board_getitem():
    pos = Square('d', 5)
    queen = Piece(Queen(), White, pos)
    board = Board([queen])
    assert board[pos] == queen

def test_Board_getitem_not_found():
    with pytest.raises(KeyError):
        Board([])[Square(3,3)]

def test_Board_getitem_cast():
    pos = ('d', 5)
    queen = Piece(Queen(), White, Square(pos))
    board = Board([queen])
    assert board[pos] == queen

def test_Board_contains_Square():
    coord = (3,4)
    pos = Square(coord)
    queen = Piece(Queen(), White, pos)
    board = Board([queen])
    assert pos in board
    assert coord in board
    assert Square(0,0) not in board

def test_Board_contains_AbstractPiece():
    board = Board([Piece(Queen(), White, Square('d', 5))])
    assert Queen() in board
    assert King() not in board

def test_Board_contains_illegal_comparison():
    with pytest.raises(TypeError):
        "string" in Board([])

def test_Board_contains_Piece():
    queen_white = Piece(Queen(), White, Square('d', 5))
    queen_black = Piece(Queen(), Black, Square('d', 5))
    queen_white_2 = Piece(Queen(), White, Square('d', 6))
    king = Piece(King(), Black, Square('d', 5))
    board = Board([queen_white])
    assert queen_white in board
    assert queen_black not in board
    assert queen_white_2 not in board
    assert king not in board

def test_Board_iter():
    pos = Square(4, 0)
    queen = Piece(Queen(), White, pos)
    board = Board([queen])
    squares = iter(board)
    assert next(squares) == (Square(0,0), None)
    assert next(squares) == (Square(1,0), None)
    assert next(squares) == (Square(2,0), None)
    assert next(squares) == (Square(3,0), None)
    assert next(squares) == (Square(4,0), queen)
    assert next(squares) == (Square(5,0), None)
    assert next(squares) == (Square(6,0), None)
    assert next(squares) == (Square(7,0), None)
    assert next(squares) == (Square(0,1), None)

def test_Board_iter_stops():
    for _ in Board([]):
        pass

def test_Board_pieces():
    pieces = [Piece(Queen(), White, Square('d', 5)), Piece(King(), Black, Square('a', 1))]
    board = Board(pieces)
    assert board.pieces() == set(pieces)
    assert board.pieces(kind=pieces[0]) == set([pieces[0]])
    assert board.pieces(kind=King()) == set([pieces[1]])
    assert board.pieces(color=White) == set([pieces[0]])
    assert board.pieces(kind=King(), color=White) == set()

def test_Board_add():
    board = Board([])
    pos = Square('d', 5)
    piece_ = Piece(Queen(), White, pos)
    added = board.add(piece_)
    assert board.pieces() == added
    assert board.pieces() == {piece_}
    assert piece_ in board
    assert pos in board
    assert board[pos] == piece_

def test_Board_add_square_taken():
    piece_ = Piece(Queen(), White, Square('d', 5))
    board = Board([piece_])
    with pytest.raises(ValueError):
        board.add(piece_)

def test_Board_capture():
    color = White
    pos = Square('d', 5)
    piece_ = Piece(Queen(), color, pos)
    board = Board([piece_])
    board.capture(piece_)
    assert piece_ not in board
    assert pos not in board
    assert piece_ in board.captured[color]

def test_Board_remove():
    pos = Square('d', 5)
    piece_ = Piece(Queen(), White, pos)
    board = Board([piece_])
    removed = board.remove(piece_)
    assert removed == piece_
    assert board.pieces() == set()
    assert piece_ not in board
    assert pos not in board

def test_Board_remove_not_present():
    piece_ = Piece(Queen(), White, Square('d', 5))
    board = Board([])
    with pytest.raises(KeyError):
        board.remove(piece_)

def test_Board_make_move():
    pos = Square('d', 5)
    queen = Piece(Queen(), White, pos)
    board = Board([queen])
    target = pos+(0,2)
    new_queen = Piece(Queen(), White, target)
    new_board = board.make_move(queen, target)
    assert new_board.pieces() == {new_queen}
    assert queen not in new_board
    assert new_queen in new_board
    assert new_board[target] == new_queen

def test_Board_make_move_illegal():
    pos = Square('d', 5)
    king = Piece(King(), White, pos)
    board = Board([king])
    target = pos+(0,3)
    with pytest.raises(IllegalMoveError):
        board.make_move(king, target)

def test_Bord_make_move_capture():
    color = White
    pos_a = Square(('d', 5))
    pos_b = pos_a+(0,1)
    piece_a = Piece(Queen(), color, pos_a)
    piece_b = Piece(Queen(), ~color, pos_b)
    board = Board([piece_a, piece_b])
    new_board = board.make_move(piece_a, pos_b)
    assert new_board[pos_b] == piece_a.move_to(pos_b, board)
    assert piece_b not in new_board
    assert piece_b in new_board.captured[~color]

def test_Bord_make_move_capture_inherit():
    color = White
    pos_a = Square(('d', 5))
    pos_b = pos_a+(0,1)
    piece_a = Piece(Queen(), color, pos_a)
    piece_b = Piece(Queen(), ~color, pos_b)
    board = Board([piece_a, piece_b])
    new_board = board.make_move(piece_a, pos_b)
    newer_board = new_board.make_move(new_board[pos_b], pos_b+(1,0))
    assert piece_b in newer_board.captured[~color]

def  test_Bord_make_move_capture_self():
    pos_a = Square(('d', 5))
    pos_b = pos_a+(0,1)
    pieces = [Piece(Queen(), White, pos_a), Piece(Queen(), White, pos_b)]
    board = Board(pieces)
    with pytest.raises(IllegalMoveError):
        board.make_move(pieces[0], pos_b)

def test_Board_make_move_check():
    # nothing special happenes on a check move
    king = Piece(King(), White, Square('a',1))
    attacker = Piece(Queen(), Black, Square('b',8))
    board = Board([king,attacker])
    board.make_move(attacker, Square('a',8))

def test_Board_make_move_castling(castling_board):
    king_w = castling_board[Square('e1')]
    king_b = castling_board[Square('e8')]

    new_board = castling_board.make_move(king_w, Square('c1'))
    assert new_board[Square('c1')] == King()
    assert new_board[Square('d1')] == Rook()
    assert Square('a1') not in new_board

    new_board = castling_board.make_move(king_w, Square('g1'))
    assert new_board[Square('g1')] == King()
    assert new_board[Square('f1')] == Rook()
    assert Square('h1') not in new_board

    new_board = castling_board.make_move(king_b, Square('c8'))
    assert new_board[Square('c8')] == King()
    assert new_board[Square('d8')] == Rook()
    assert Square('a8') not in new_board

    new_board = castling_board.make_move(king_b, Square('g8'))
    assert new_board[Square('g8')] == King()
    assert new_board[Square('f8')] == Rook()
    assert Square('h8') not in new_board

    new_board = castling_board.make_move(king_w, Square('d',1))
    new_board = new_board.make_move(new_board[Square('d',1)], Square('e',1))
    with pytest.raises(IllegalMoveError):
        castling_board.make_move(new_board[Square('e',1)], Square('a',1))


def test_Board_possible_moves():
    # we need kings out of check to get possible moves
    pieces_w = [Piece(Queen(), White, Square('a',1)), Piece(Pawn(White), White, Square('b',2)), Piece(King(), White, Square('e', 1))]
    pieces_b = [Piece(King(), Black, Square('e', 8)), Piece(Pawn(Black), Black, Square('b',7))]
    board = Board(pieces_w+pieces_b)
    assert board.possible_moves(White) == {(p, t) for p in pieces_w for t in p.possible_moves(board)}
    assert board.possible_moves(Black) == {(p, t) for p in pieces_b for t in p.possible_moves(board)}

def test_Board_possible_moves_give_check_King():
    assert Board([Piece(King(), White, Square('a',1))]).possible_moves(White, give_check=True) == set()

def test_Board_possible_moves_give_check_Pawn():
    pos = Square('d',2)
    color = White
    piece = Piece(Pawn(color), color, pos)
    board = Board([piece])
    assert board.possible_moves(color, give_check=True) == {(piece, target) for target in Pawn(color).legal_moves(pos, board, only_attacked=True)}

def test_Board_possible_moves_check():
    pieces = [Piece(King(), White, Square('a', 1)),
            Piece(Rook(), White, Square('b', 5)),
            Piece(Pawn(White), White, Square('b',1)),
            Piece(Pawn(White), White, Square('b',2)),
            Piece(Queen(), Black, Square('a', 8))]
    assert Board(pieces).possible_moves(White) == set([(pieces[1], Square('a', 5))])

def test_Board_is_check_no():
    assert Board([Piece(King(), White, Square('d', 5))]).is_check(White) == False

def test_Board_is_check_yes():
    queen = Piece(Queen(), Black, Square('a', 8))
    board = Board([Piece(King(), White, Square('a', 1)), queen])
    board.print(mark=queen.possible_moves(board))
    assert Board([Piece(King(), White, Square('a', 1)), Piece(Queen(), Black, Square('a', 8))]).is_check(White) == True

def test_Board_is_checkmate_no():
    """This is not a checkmate as a piece can be moved in between."""
    pieces = [Piece(King(), White, Square('a', 1)),
            Piece(Queen(), White, Square('b', 5)),
            Piece(Pawn(White), White, Square('b',1)),
            Piece(Pawn(White), White, Square('b',2)),
            Piece(Queen(), Black, Square('a', 8))]
    assert Board(pieces).is_check(White) == True
    assert Board(pieces).is_checkmate(White) == False

def test_Board_is_checkmate_yes():
    pieces = [Piece(King(), White, Square('a', 1)),
            Piece(Pawn(White), White, Square('h', 4)),
            Piece(Queen(), Black, Square('a', 8)),
            Piece(Queen(), Black, Square('h', 8)),
            Piece(Queen(), Black, Square('h', 1))]
    assert Board(pieces).is_checkmate(White) == True

def test_Board_is_stalemate():
    pieces = [Piece(King(), White, Square('a', 1)),
            Piece(Rook(), Black, Square('b', 2)),
            Piece(King(), Black, Square('c', 3))]
    assert Board(pieces).is_stalemate(White) == True
    assert Board(pieces).is_checkmate(White) == False

def test_Board_print(capsys):
    board = Board([Piece(Queen(), White, Square('d', 5))])
    board.print()
    assert capsys.readouterr().out == """ abcdefgh 
8\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m8
7\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m7
6\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m6
5\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m♛\x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m5
4\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m4
3\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m3
2\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m2
1\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m1
 abcdefgh 
captured:
  white: none
  black: none
"""

def test_Board_print_ascii(capsys):
    board = Board([Piece(Queen(), White, Square('d', 5))])
    board.print(unicode=False, color=False)
    assert capsys.readouterr().out == """ abcdefgh 
8 # # # #8
7# # # # 7
6 # # # #6
5# #Q# # 5
4 # # # #4
3# # # # 3
2 # # # #2
1# # # # 1
 abcdefgh 
captured:
  white: none
  black: none
"""

def test_Board_print_mark_color(capsys):
    Board([Piece(Queen(), White, Square('a', 1)), Piece(Queen(), Black, Square('b', 2))]).print(mark=[(0,0), (0,1), (1,0), (1,1)])
    assert capsys.readouterr().out == """ abcdefgh 
8\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m8
7\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m7
6\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m6
5\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m5
4\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m4
3\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m3
2\x1b[38;5;255m\x1b[48;5;220m \x1b[0m\x1b[38;5;16m\x1b[48;5;130m♛\x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m2
1\x1b[38;5;255m\x1b[48;5;130m♛\x1b[0m\x1b[38;5;255m\x1b[48;5;220m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m\x1b[38;5;255m\x1b[48;5;239m \x1b[0m\x1b[38;5;255m\x1b[48;5;249m \x1b[0m1
 abcdefgh 
captured:
  white: none
  black: none
"""

def test_Board_print_mark_unicode(capsys):
    Board([]).print(unicode=True, color=False, mark=[(0,0), (0,1), (1,0), (1,1)])
    assert capsys.readouterr().out == """ abcdefgh 
8 █ █ █ █8
7█ █ █ █ 7
6 █ █ █ █6
5█ █ █ █ 5
4 █ █ █ █4
3█ █ █ █ 3
2░▓ █ █ █2
1▓░█ █ █ 1
 abcdefgh 
captured:
  white: none
  black: none
"""

def test_Board_print_mark_ascii(capsys):
    Board([]).print(unicode=False, color=False, mark=[(0,0), (0,1), (1,0), (1,1)])
    assert capsys.readouterr().out == """ abcdefgh 
8 # # # #8
7# # # # 7
6 # # # #6
5# # # # 5
4 # # # #4
3# # # # 3
2.@ # # #2
1@.# # # 1
 abcdefgh 
captured:
  white: none
  black: none
"""

def test_Board_print_captured(capsys):
    piece = Piece(Queen(), White, Square('d', 5))
    board = Board([piece])
    board.capture(piece)
    board.print(unicode=True, color=False)
    assert capsys.readouterr().out == """ abcdefgh 
8 █ █ █ █8
7█ █ █ █ 7
6 █ █ █ █6
5█ █ █ █ 5
4 █ █ █ █4
3█ █ █ █ 3
2 █ █ █ █2
1█ █ █ █ 1
 abcdefgh 
captured:
  white: none
  black: ♕
"""

def test_Board_print_captured_ascii(capsys):
    piece = Piece(Queen(), White, Square('d', 5))
    board = Board([piece])
    board.capture(piece)
    board.print(unicode=False, color=False)
    assert capsys.readouterr().out == """ abcdefgh 
8 # # # #8
7# # # # 7
6 # # # #6
5# # # # 5
4 # # # #4
3# # # # 3
2 # # # #2
1# # # # 1
 abcdefgh 
captured:
  white: none
  black: Q
"""

def test_Board_upside_down(capsys):
    Board([Piece(Queen(), White, Square('a', 1))]).print(unicode=True, color=False, upside_down=True)
    assert capsys.readouterr().out == """ abcdefgh 
1♕ █ █ █ 1
2 █ █ █ █2
3█ █ █ █ 3
4 █ █ █ █4
5█ █ █ █ 5
6 █ █ █ █6
7█ █ █ █ 7
8 █ █ █ █8
 abcdefgh 
captured:
  white: none
  black: none
"""
