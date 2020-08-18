import pytest

from ..game import Game
from .. import piece
from ..board import White, Black, Board, Square
from ..errors import MoveParseError, WrongPlayerError, IllegalMoveError, AmbigousMoveError

@pytest.fixture
def moves():
    return ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6']

@pytest.fixture
def ambigous_game():
    pieces = [piece.Piece(piece.Knight(), White, Square('f',7)), piece.Piece(piece.Knight(), White, Square('d',3))]
    game = Game([])
    game.boards[-1] = Board(pieces)
    return game


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
    assert game.boards[-1] == initial_board
    assert game.current_player == Game.FIRST_PLAYER
    assert len(game.moves) == 0

def test_Game_init_move():
    game = Game(['g1Nf3'])
    target = Square('f', 3)
    assert len(game.boards) == 2
    assert target not in game.boards[0]
    assert target in game.boards[1]
    assert game.boards[1][target] == piece.Piece(piece.Knight(), Game.FIRST_PLAYER, target)

def test_Game_repr(moves):
    assert repr(Game(moves)) == '<Game moves=6 current_player=white>'

def test_Game_str():
    moves_str = """e2Pe4 e7Pe5
g1Nf3 b8Nc6
f1Bb5 a7Pa6
"""
    moves_list = [move for round_ in moves_str.split('\n') for move in round_.split(' ') if move]
    print(moves_list)
    assert str(Game(moves_list)) == moves_str
    moves_str = """e2Pe4 e7Pe5
g1Nf3 b8Nc6
f1Bb5
"""
    moves_list = [move for round_ in moves_str.split('\n') for move in round_.split(' ') if move]
    print(moves_list)
    assert str(Game(moves_list)) == moves_str

def test_Game_parse_move():
    assert Game([]).parse_move('g1Nf3') == (piece.Piece(piece.Knight(), Game.FIRST_PLAYER, Square('g', 1)), Square('f', 3))

def test_Game_parse_move_wrong_format():
    move = 'string'
    with pytest.raises(MoveParseError) as error:
        Game([]).parse_move('string')
    assert error.value.move == move
    assert error.value.reason == 'Wrong move format'

def test_Game_parse_move_wrong_piece():
    move = 'g1Qf3'
    with pytest.raises(MoveParseError) as error:
        Game([]).parse_move(move)
    assert error.value.move == move
    assert "Specified source piece and piece on that square do not match (is None)"

def test_Game_parse_move_wrong_player():
    with pytest.raises(MoveParseError):
        Game([]).parse_move('b8Nc6')
    with pytest.raises(MoveParseError):
        Game([]).parse_move('g1Nf3', current_player=~Game.FIRST_PLAYER)

def test_Game_parse_move_inference_impossible(ambigous_game):
    move = 'Ne5'
    with pytest.raises(AmbigousMoveError) as error:
        ambigous_game.parse_move('Ne5', current_player=White)
    assert error.value.move == move
    assert error.value.reason == 'Source piece inference not possible'

def test_Game_parse_mave_inference_hint(ambigous_game):
    assert ambigous_game.parse_move('fNe5') == (piece.Piece(piece.Knight(), White, Square('f',7)), Square('e',5))
    assert ambigous_game.parse_move('3Ne5') == (piece.Piece(piece.Knight(), White, Square('d',3)), Square('e',5))

def test_Game_move_str():
    game = Game([])
    assert game.move_str((piece.Piece(piece.Queen(), White, Square('a',1)),Square('a',3))) == 'a1Qa3'

def test_Game_len_make_move():
    game = Game([])
    assert len(game) == 0
    game.make_move(game.boards[-1][Square('a',2)], Square('a',3))
    assert len(game) == 1
    assert Square('a',3) in game.boards[-1]
    game.make_move(game.boards[-1][Square('b',7)], Square('b',5))
    assert len(game) == 2
    assert Square('b',5) in game.boards[-1]

def test_Game_make_move_str():
    game = Game([])
    game.make_move('a2Pa3')
    assert Square('a',3) in game.boards[-1]
    with pytest.raises(ValueError):
        game.make_move(23)

def test_Game_make_move_illegal_move():
    game = Game([])
    with pytest.raises(IllegalMoveError):
        game.make_move(game.boards[-1][Square('a',2)], Square('a',6))

def test_Game_make_move_wrong_player():
    game = Game([])
    with pytest.raises(WrongPlayerError):
        game.make_move(game.boards[-1][Square('a',7)], Square('a',6))

def test_Game_make_move_capture():
    game = Game(['d4', 'e5', 'e5', 'd6', 'e3'])
    captive = game.boards[2][Square('e', 5)]
    for b in game.boards:
        b.print()
    assert game.boards[0].captured[Black] == set()
    assert game.boards[1].captured[Black] == set()
    assert game.boards[2].captured[Black] == set()
    assert game.boards[3].captured[Black] == set([captive])
    assert game.boards[4].captured[Black] == set([captive])
    assert game.boards[5].captured[Black] == set([captive])

def test_Game_print_board(capsys):
    game = Game([])
    game.print_board(unicode=True)
    game_out = capsys.readouterr().out
    game.boards[-1].print(unicode=True)
    board_out = capsys.readouterr().out
    assert game_out == board_out

def test_Game_print_board_arg(capsys):
    game = Game([])
    game.print_board()
    game_out = capsys.readouterr().out
    Board(game.boards[-1].pieces()).print()
    board_out = capsys.readouterr().out
    assert game_out == board_out

def test_Game_print_board_ascii(capsys):
    game = Game([])
    game.print_board(unicode=False)
    game_out = capsys.readouterr().out
    game.boards[-1].print(unicode=False)
    board_out = capsys.readouterr().out
    assert game_out == board_out

def test_Game_undo():
    game = Game([])
    game.make_move('e4')
    assert len(game) == 1
    game.undo()
    assert len(game) == 0
