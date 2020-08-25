import pytest

from ..ai import WukiAI
from ..board import White, Black, Square, Board
from ..piece import Piece, King, Queen

AI_COLOR = White

@pytest.fixture()
def ai_and_kings():
    ai = WukiAI(AI_COLOR)
    kings = [Piece(King(), White, Square('e', 1)),
             Piece(King(), Black, Square('e', 8))]
    return ai, kings


def test_eval_captured(ai_and_kings):
    ai, kings = ai_and_kings
    piece_own = Piece(Queen(), AI_COLOR, Square('a',1))
    piece_opp = Piece(Queen(), ~AI_COLOR, Square('a',8))
    board = Board(kings+[piece_own, piece_opp])
    board.capture(piece_opp)
    assert ai.eval_captured(board) == 10*ai.piece_value[piece_opp.piece]
    board.capture(piece_own)
    assert ai.eval_captured(board) == 0

def test_eval_center(ai_and_kings):
    ai, kings = ai_and_kings
    board = Board(kings)
    assert ai.eval_center(board) == 0
    board.add(Piece(Queen(), AI_COLOR, Square('d', 4)))
    assert ai.eval_center(board) == 3
    board.add(Piece(Queen(), AI_COLOR, Square('d',6)))
    assert ai.eval_center(board) == 4

