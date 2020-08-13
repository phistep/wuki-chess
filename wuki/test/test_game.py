import pytest

from ..game import Game, MoveParseError
from .. import piece
from ..board import White, Black, Board, Square

def test_Game_init_empty():
    game = Game([])
    initial_pieces = [
        piece.Piece(piece.Rook(),   White, Square('a', 1)),
        piece.Piece(piece.Knight(), White, Square('b', 1)),
        piece.Piece(piece.Bishop(), White, Square('c', 1)),
        piece.Piece(piece.King(),   White, Square('e', 1)),
        piece.Piece(piece.Queen(),  White, Square('d', 1)),
        piece.Piece(piece.Bishop(), White, Square('f', 1)),
        piece.Piece(piece.Knight(), White, Square('g', 1)),
        piece.Piece(piece.Rook(),   White, Square('h', 1)),

        piece.Piece(piece.Rook(),   Black, Square('a', 8)),
        piece.Piece(piece.Knight(), Black, Square('b', 8)),
        piece.Piece(piece.Bishop(), Black, Square('c', 8)),
        piece.Piece(piece.King(),   Black, Square('e', 8)),
        piece.Piece(piece.Queen(),  Black, Square('d', 8)),
        piece.Piece(piece.Bishop(), Black, Square('f', 8)),
        piece.Piece(piece.Knight(), Black, Square('g', 8)),
        piece.Piece(piece.Rook(),   Black, Square('h', 8)),
    ]
    initial_pieces.extend([piece.Piece(piece.Pawn(White), White, Square(col, 2)) for col in "abcdefgh"])
    initial_pieces.extend([piece.Piece(piece.Pawn(Black), Black, Square(col, 7)) for col in "abcdefgh"])
    initial_board = Board(initial_pieces)
    # TODO something with the comparison does not work
    assert game.boards[-1] == initial_board
    assert game.current_player == Game.FIRST_PLAYER
    assert len(game.moves) == 0

def test_Game_init_move():
    assert False

def test_Game_parse_move():
    assert Game([]).parse_move('g1Nf3') == (piece.Piece(piece.Knight(), Game.FIRST_PLAYER, Square('g', 1)), Square('f', 3))

def test_Game_parse_move_wrong_piece():
    with pytest.raises(MoveParseError):
        Game([]).parse_move('g1Qf3')

def test_Game_parse_move_wrong_player():
    with pytest.raises(MoveParseError):
        Game([]).parse_move('b8Nc6')
    with pytest.raises(MoveParseError):
        Game([]).parse_move('g1Nf3', current_player=~Game.FIRST_PLAYER)

# TODO test game make_move exceptions
def test_Game_make_move():
    assert False
