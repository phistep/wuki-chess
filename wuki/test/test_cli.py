import pytest

from .. import cli
from ..game import Game

def test_parse_match_file(tmp_path):
    moves_str = """e4 e5
Nf3 Nc6
Bb5
"""
    match_file = tmp_path / 'match.txt'
    match_file.write_text(moves_str)
    moves_list = ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5']
    assert cli.parse_match_file(match_file) == moves_list

def test_write_match_file(tmp_path):
    moves_str = """e2Pe4 e7Pe5
g1Nf3 b8Nc6
f1Bb5
"""
    moves_list = [move for round_ in moves_str.split('\n') for move in round_.split(' ') if move]
    game = Game(moves_list)
    match_file = tmp_path / 'match.txt'
    cli.write_match_file(match_file, game)
    assert match_file.read_text() == moves_str


# TODO
@pytest.mark.skip(reason="test not implemented")
def test_print_full_game():
    assert False

# TODO test main
# test all command line arguments
