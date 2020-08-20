import pytest

from ..piece import AbstractPiece, Piece, King, Queen, Rook, Bishop, Knight, Pawn, all_pieces, piece_by_letter
from ..board import White, Black, BOARD_LEN, Square, Board
from ..exceptions import IllegalMoveError

@pytest.fixture
def castling_board():
    pieces = []
    for y, color in zip([0,7], [White,Black]):
        pieces.extend([
            Piece(King(), color, Square('e',y+1)),
            Piece(Rook(), color, Square('a',y+1)),
            Piece(Rook(), color, Square('h',y+1)),
            ])
        for x in range(BOARD_LEN):
            pieces.append(Piece(Pawn(color), color, Square(x,y)))
    return Board(pieces)


def test_AbstractPiece_eq():
    assert King() == King()
    assert King() != Queen()

def test_AbstractPiece_eq_Piece():
    assert King() == Piece(King(), White, Square(0,0))
    assert King() != Piece(Queen(), White, Square(0,0))

def test_AbstractPiece_eq_illegal():
    with pytest.raises(TypeError):
        King() == "string"

def test_AbstractPiece_str_repr():
    name = 'Name'
    letter = 'N'
    class TestPiece(AbstractPiece):
        def __init__(self):
            self.name = name
            self.letter = letter
    test = TestPiece()
    assert str(test) == name
    assert repr(test) == f'<AbstractPiece {name} ({letter})>'

def test_AbstractPiece_hash():
    assert {King(): 1}
    assert {Pawn(White): 1}


def test_Piece_init():
    pos = Square('a', 1)
    color = White
    abs_piece = King()
    piece_ = Piece(abs_piece, color, pos)
    assert piece_.name == abs_piece.name
    assert piece_.color == color
    assert piece_.piece == abs_piece
    assert piece_.letter == abs_piece.letter if color == White else abs_piece.letter.lower()
    assert piece_.symbol == abs_piece.symbol[color]
    assert piece_.position == pos
    assert piece_.piece.legal_moves == abs_piece.legal_moves

def test_Piece_init_not_within_board():
    with pytest.raises(ValueError):
        Piece(King(), White, Square(-1,-1))

def test_Piece_init_from_tuple():
    pos = (0,0)
    assert Piece(King(), White, pos).position == Square(pos)

def test_Piece_str():
    abs_piece = King()
    pos = Square('a', 1)
    assert str(Piece(abs_piece, White, pos)) == str(pos)+abs_piece.letter

def test_Piece_repr():
    abs_piece = King()
    pos = Square('a', 1)
    color = White
    assert repr(Piece(abs_piece, color, pos)) == f"<{abs_piece.name} color={color} position={pos}>"

def test_Piece_eq_Piece():
    abs_piece = King()
    color = White
    pos = Square('a', 1)
    assert Piece(abs_piece, color, pos) == Piece(abs_piece, color, pos)
    assert Piece(abs_piece, color, pos) != Piece(Queen(), color, pos)
    assert Piece(abs_piece, color, pos) != Piece(abs_piece, ~color, pos)
    assert Piece(abs_piece, color, pos) != Piece(abs_piece, color, pos+(0,1))

def test_Piece_eq_AbstractPiece():
    abs_piece = King()
    piece_ = Piece(abs_piece, White, Square('a', 2))
    assert piece_ == abs_piece
    assert piece_ != Queen()

def test_Piece_eq_illegal():
    with pytest.raises(TypeError):
        Piece(King(), White, Square('a', 1)) == "string"

def test_Piece_hash():
    assert {Piece(King(), White, Square('a', 1)): 1}

def test_Piece_possible_moves():
    abs_piece = King()
    pos = Square('a', 2)
    color = White
    piece_ = Piece(abs_piece, color, pos)
    board = Board([piece_])
    assert piece_.possible_moves(board) == abs_piece.legal_moves(pos, board=board)
    abs_piece = Pawn(color)
    piece_ = Piece(abs_piece, color, pos)
    board = Board([piece_])
    assert piece_.possible_moves(board) == abs_piece.legal_moves(pos, board=board)

def test_Piece_possible_moves_blocked_diag():
    pos = Square('a',1)
    pieces = [Piece(Queen(), White, pos), Piece(Pawn(White), White, pos+(2,2))]
    orthos = pos.orthogonals()
    orthos.discard(pos)
    assert pieces[0].possible_moves(Board(pieces)) == orthos | {pos+(1,1)}

def test_Piece_possible_moves_blocked_ortho():
    pos = Square('a',1)
    pieces = [Piece(Rook(), White, pos), Piece(Pawn(White), White, pos+(2,0)), Piece(Pawn(White), White, pos+(0,2))]
    assert pieces[0].possible_moves(Board(pieces)) == set([pos+(1,0), pos+(0,1)])

def test_Piece_possible_moves_capture():
    attacker = Piece(Rook(), White, Square(0,0))
    captive = Piece(Rook(), ~attacker.color, Square(1,0))
    ally = Piece(Pawn(attacker.color), attacker.color, Square(0,1))
    assert attacker.possible_moves(Board([attacker, captive, ally])) == set([captive.position])

def test_Piece_possible_moves_blocked_no_capture():
    attacker = Piece(Rook(), White, Square('d',1))
    noncaptive = Piece(Queen(), ~attacker.color, Square('d',8))
    blockers = [Piece(Pawn(attacker.color), attacker.color, attacker.position+(-1,0)),
                Piece(Pawn(attacker.color), attacker.color, attacker.position+( 1,0)),
                # bug strikes again
                Piece(Pawn(~attacker.color), ~attacker.color, attacker.position+( 0,5)),
                Piece(Pawn( attacker.color),  attacker.color, attacker.position+( 0,2)),]
    board = Board([attacker]+[noncaptive]+blockers)
    assert attacker.possible_moves(board) == set([attacker.position+(0,1)])

def test_Piece_possible_moves_Pawn():
    pos = Square('a',2)
    pieces = [Piece(Pawn(White), White, pos), Piece(Pawn(White), Black, pos+(0,1)), Piece(Pawn(White), Black, pos+(1,1))]
    assert pieces[0].possible_moves(Board(pieces)) == set([pos+(1,1)])
    pieces = [Piece(Pawn(White), White, pos), Piece(Pawn(White), Black, pos+(0,2))]
    assert pieces[0].possible_moves(Board(pieces)) == set([pos+(0,1)])

def test_Piece_possible_moves_Pawn_capture():
    attacker = Piece(Pawn(White), White, Square(0,0))
    captive = Piece(Pawn(~attacker.color), ~attacker.color, Square(1,1))
    ally = Piece(Pawn(attacker.color), attacker.color, Square(0,1))
    assert attacker.possible_moves(Board([attacker, captive, ally])) == set([captive.position])

def test_Piece_possible_moves_blocked_Knight():
    pos = Square('a',1)
    pos_capture = pos + (1,2)
    pos_no_capture = pos + (2,1)
    pieces = [Piece(Knight(), White, pos), Piece(Pawn(White), White, pos+(1,1)), Piece(Pawn(White), White, pos_no_capture), Piece(Pawn(Black), Black, pos_capture)]
    assert pieces[0].possible_moves(Board(pieces)) == set([pos_capture])

def test_Piece_possible_moves_King():
    pieces = [Piece(King(), White, Square(6,0)),
            Piece(Bishop(), White, Square(4,0)),
            Piece(King(), Black, Square(4,2)),
            Piece(Bishop(), Black, Square(6,2)),
            ]
    board = Board(pieces)
    assert pieces[0].possible_moves(board) == set(map(Square,[(5,0), (6,1), (7,0)]))
    assert pieces[2].possible_moves(board) == set(map(Square,[(3,2), (3,3), (4,1), (4,3), (5,2), (5,3)]))

def test_Piece_possible_moves_King_and_Pawn():
    # this is an edge case since Kings need to take "attacked" squares under
    # account when moving
    king = Piece(King(), Black, Square(4,2))
    pawn = Piece(Pawn(White), White, Square(4,0)) # don't ask me how it got there
    board = Board([king,pawn])
    assert king.possible_moves(board) == set(map(Square,[(3,2), (3,3), (4,1), (4,3), (5,2), (5,3)]))


# TODO this sems to be a board test, not a piece test
@pytest.mark.skip(reason="not implemented")
def test_Piece_possible_moves_castling(castling_board):
    king_w = castling_board[Square('e',1)]
    king_b = castling_board[Square('e',8)]

    new_board = castling_board.make_move(king_w, Square('a',1))
    assert new_board[Square('a',1)] == King()
    assert new_board[Square('b',1)] == Rook()

    new_board = castling_board.make_move(king_w, Square('h',1))
    assert new_board[Square('h',1)] == King()
    assert new_board[Square('g',1)] == Rook()

    new_board = castling_board.make_move(king_b, Square('a',8))
    assert new_board[Square('a',8)] == King()
    assert new_board[Square('b',8)] == Rook()

    new_board = castling_board.make_move(king_b, Square('h',8))
    assert new_board[Square('h',8)] == King()
    assert new_board[Square('g',8)] == Rook()

    new_board = castling_board.make_move(king_w, Square('d',1))
    with pytest.raises(IllegalMoveError):
        castling_board.make_move(new_board[Square('d',1)], Square('a',1))


def test_Piece_move_to():
    pos = Square('d', 5)
    piece_ = Piece(Queen(), White, pos)
    target = pos+(0,3)
    new_piece = piece_.move_to(target, Board([piece_]))
    assert new_piece == Piece(Queen(), White, target)
    assert new_piece.position == target
    assert piece_ != new_piece
    assert piece_.position == pos

def test_Piece_move_to_illegal():
    pos = Square('d', 5)
    king = Piece(King(), White, pos)
    target = pos+(0,3)
    with pytest.raises(IllegalMoveError):
        king.move_to(target, Board([king]))


def test_King_init():
    king = King()
    assert king.name == "King"
    assert king.letter == 'K'
    assert king.symbol[White] == '♔'
    assert king.symbol[Black] == '♚'

def test_King_legal_moves():
    king = King()
    assert king.legal_moves(Square(4,4)) == set([(3,4), (5,4), (4,3), (4,5), (3,3), (5,5), (3,5), (5,3)])
    assert king.legal_moves(Square(0,4)) == set([(0,3), (0,5), (1,3), (1,4), (1,5)])
    assert king.legal_moves(Square(7,7)) == set([(7,6), (6,7), (6,6)])

@pytest.mark.skip(reason="not implemented")
def test_King_legal_moves_castling(castling_board):
    # even though some Squares are blocked by other pices, the AbstractPiece does not care about this
    assert King().legal_moves(Square('e',1), board=castling_board) == set(map(Square, [('a',1), ('h',1), ('d',1), ('f',1), ('d',2), ('e',2), ('f',2)]))
    assert King().legal_moves(Square('e',8), board=castling_board) == set(map(Square, [('a',8), ('h',8), ('d',8), ('f',8), ('d',7), ('e',7), ('f',7)]))


def test_Queen_init():
    queen = Queen()
    assert queen.name == "Queen"
    assert queen.letter == 'Q'
    assert queen.symbol[White] == '♕'
    assert queen.symbol[Black] == '♛'

def test_Queen_legal_moves():
    assert Queen().legal_moves(Square(4,4)) == set([
        (0,4), (1,4), (2,4), (3,4), (5,4), (6,4), (7,4),
        (4,0), (4,1), (4,2), (4,3), (4,5), (4,6), (4,7),
        (0,0), (1,1), (2,2), (3,3), (5,5), (6,6), (7,7),
        (7,1), (6,2), (5,3), (3,5), (2,6), (1,7),
        ])


def test_Rook_init():
    rook = Rook()
    assert rook.name == "Rook"
    assert rook.letter == 'R'
    assert rook.symbol[White] == '♖'
    assert rook.symbol[Black] == '♜'

def test_Rook_legal_moves():
    assert Rook().legal_moves(Square(4,4)) == set([(0,4), (1,4), (2,4), (3,4), (5,4), (6,4), (7,4), (4,0), (4,1), (4,2), (4,3), (4,5), (4,6), (4,7)])


def test_Bishop_init():
    bishop = Bishop()
    assert bishop.name == "Bishop"
    assert bishop.letter == 'B'
    assert bishop.symbol[White] == '♗'
    assert bishop.symbol[Black] == '♝'

def test_Bishop_legal_moves():
    assert Bishop().legal_moves(Square(6,1)) == set([(5,0), (7,2), (7,0), (5,2), (4,3), (3,4), (2,5), (1,6), (0,7)])


def test_Knight_init():
    knight = Knight()
    assert knight.name == "Knight"
    assert knight.letter == 'N'
    assert knight.symbol[White] == '♘'
    assert knight.symbol[Black] == '♞'

def test_Knight_legal_moves():
    knight = Knight()
    assert knight.legal_moves(Square('f', 3)) == set(map(Square,[('e',5), ('d',4), ('d', 2), ('e',1), ('g', 1), ('h',2), ('h',4), ('g',5)]))
    assert knight.legal_moves(Square('g', 1)) == set(map(Square,[('e',2), ('f',3), ('h', 3)]))


def test_Pawn_init():
    color = White
    pawn = Pawn(color)
    assert pawn.name == "Pawn"
    assert pawn.letter == 'P'
    assert pawn.symbol[White] == '♙'
    assert pawn.symbol[Black] == '♟'
    assert pawn.color == color

def test_Pawn_repr():
    color = White
    assert repr(Pawn(color)) == f"<AbstractPiece Pawn (P) color={color}>"


def test_Pawn_legal_moves():
    pawn_w = Pawn(White)
    assert pawn_w.legal_moves(Square('e',2), board=Board([])) == set([Square('e',3), Square('e',4)])
    assert pawn_w.legal_moves(Square('c',4), board=Board([])) == set([Square('c',5)])
    assert pawn_w.legal_moves(Square('d',8), board=Board([])) == set([])
    pawn_b = Pawn(Black)
    assert pawn_b.legal_moves(Square('g',7), board=Board([])) == set([Square('g',6), Square('g',5)])
    assert pawn_b.legal_moves(Square('a',6), board=Board([])) == set([Square('a',5)])
    assert pawn_b.legal_moves(Square('d',1), board=Board([])) == set([])

def test_Pawn_legal_moves_only_attacked():
    pos = Square('b',2)
    color = White
    assert Pawn(color).legal_moves(pos, Board([]), only_attacked=True) == set([pos+(-1,color.direction), pos+(+1,color.direction)])

def test_Pawn_legal_moves_capture():
    pieces = [
            Piece(Pawn(White), White, Square('d',5)),
            Piece(Pawn(Black), Black, Square('c',6)),
            Piece(Pawn(Black), Black, Square('e',6)),
        ]
    board = Board(pieces)
    assert Pawn(White).legal_moves(pieces[0].position, board) == set([pieces[1].position, pieces[2].position, pieces[0].position+(0,+1)])
    assert Pawn(Black).legal_moves(pieces[1].position, board) == set([pieces[0].position, pieces[1].position+(0,-1)])
    assert Pawn(Black).legal_moves(pieces[2].position, board) == set([pieces[0].position, pieces[2].position+(0,-1)])

@pytest.mark.skip(reason="not implemented")
def test_Pawn_legal_moves_en_passent():
    pawn_w = Piece(Pawn(White), White, Square('d',5))
    pawn_b = Piece(Pawn(Black), Black, Square('c',7))
    board = Board([pawn_w, pawn_b])
    board = board.make_move(pawn_b, Square('c',5))
    assert Pawn(White).possible_moves(pawn_w.position, board=board) == set([Square('c',6), Square('d',6)])

    pawn_w = Piece(Pawn(White), White, Square('d',5))
    pawn_b = Piece(Pawn(Black), Black, Square('c',7))
    board = Board([pawn_w, pawn_b])
    board = board.make_move(pawn_b, Square('c',6))
    board = board.make_move(board[Square('c',6)], Square('c',7))
    assert Pawn(White).possible_moves(pawn_w.position, board=board) == set([Square('d',6)])

    pawn_w = Piece(Pawn(White), White, Square('d',5))
    pawn_b = Piece(Pawn(Black), Black, Square('e',7))
    board = Board([pawn_w, pawn_b])
    board = board.make_move(pawn_b, Square('e',5))
    assert Pawn(White).possible_moves(pawn_w.position, board=board) == set([Square('e',6), Square('d',6)])

    pawn_w = Piece(Pawn(White), White, Square('c',1))
    pawn_b = Piece(Pawn(Black), Black, Square('d',4))
    board = Board([pawn_w, pawn_b])
    board = board.make_move(pawn_w, Square('c',4))
    assert Pawn(Black).possible_moves(pawn_b.position, board=board) == set([Square('c',4), Square('d',4)])

    pawn_w = Piece(Pawn(White), White, Square('e',1))
    pawn_b = Piece(Pawn(Black), Black, Square('d',4))
    board = Board([pawn_w, pawn_b])
    board = board.make_move(pawn_w, Square('e',4))
    assert Pawn(Black).possible_moves(pawn_b.position, board=board) == set([Square('e',4), Square('d',4)])

def test_all_pieces_set():
    assert all_pieces == set([King(), Queen(), Bishop(), Knight(), Rook(), Pawn(White), Pawn(Black)])

def test_piece_by_letter():
    for p in all_pieces:
        assert piece_by_letter[p.letter] == p

