import pytest

from ..cli import CLI, BreakInteractiveException
from ..game import Game
from ..board import Square

from .test_game import ambigous_game

@pytest.fixture
def mock_input(request,monkeypatch):
    """Mock the data provided to stdin. After all inputs have been provided,
    the special value `__break__` is passed, so that cli.interactive_loop()
    breaks out of the infinite loop.

    Supply this fixture with arguments by marking the respective test with
    @pytest.mark.interactive_input_data(*input_lines)
    :param *input_lines: lines that are fed one by one to repeated calls of
        input()
    """
    marker = request.node.get_closest_marker('mock_input_data')
    mock_input = iter(list(marker.args)+['__break__'])
    monkeypatch.setattr('builtins.input', lambda _, input_=mock_input: next(input_))


def test_init(tmp_path):
    match_file = tmp_path / 'match.txt'

    cli = CLI([])
    assert cli.args.all_moves == False
    assert cli.args.ascii == False
    assert cli.args.no_color == False
    assert cli.args.match_file == None
    assert cli.args.flip == False
    assert cli.args.move == None
    assert cli.args.auto_save == False
    assert isinstance(cli.game, Game)

    cli = CLI(['-a'])
    assert cli.args.all_moves == True
    cli = CLI(['-A'])
    assert cli.args.ascii == True
    cli = CLI(['-C'])
    assert cli.args.no_color == True
    cli = CLI(['-f', str(match_file)])
    assert cli.args.match_file == str(match_file)
    cli = CLI(['-F'])
    assert cli.args.flip == True
    cli = CLI(['-i'])
    assert cli.args.interactive == True
    cli = CLI(['-m', 'a3'])
    assert cli.args.move == 'a3'
    cli = CLI(['-s'])
    assert cli.args.auto_save == True

def test_main_print(capsys):
    cli = CLI([])
    cli.game.boards[-1].print()
    board_out = capsys.readouterr().out
    cli.main()
    cli_out = capsys.readouterr().out
    assert cli_out == board_out+"\nnext: white\n"

def test_main_print_full_game(capsys):
    cli = CLI(['--all-moves'])
    cli.game = Game(['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'])
    cli.main()
    main_out = capsys.readouterr().out
    cli.print_full_game()
    func_out = capsys.readouterr().out
    assert func_out in main_out

def test_main_move():
    cli = CLI(['--move', 'a4'])
    cli.main()
    assert Square('a', 4) in cli.game.boards[-1]

@pytest.mark.mock_input_data('__break__')
def test_main_interactive(mock_input,capsys):
    cli = CLI(['--interactive'])
    cli.main()
    assert "ype `help` for a list of available commands" in capsys.readouterr().out

def test_print_board(capsys):
    cli = CLI([])
    cli.game.boards[-1].print()
    board_out = capsys.readouterr().out
    cli.print_board()
    cli_out = capsys.readouterr().out
    assert cli_out == board_out

# TODO
@pytest.mark.skip(reason="test not implemented")
def test_print_board_arg():
    assert False

# TODO
# ascii, color, flip
@pytest.mark.skip(reason="test not implemented")
def test_print_board_options():
    assert False

def test_parse_match_file(tmp_path):
    moves_str = """e4 e5
Nf3 Nc6
Bb5
"""
    match_file = tmp_path / 'match.txt'
    match_file.write_text(moves_str)
    moves_list = [move for round_ in moves_str.split('\n') for move in round_.split(' ') if move]
    cli = CLI(['--match-file', str(match_file)])
    assert cli.parse_match_file() == moves_list

def test_write_match_file(tmp_path):
    moves_str = """e2Pe4 e7Pe5
g1Nf3 b8Nc6
f1Bb5
"""
    moves_list = [move for round_ in moves_str.split('\n') for move in round_.split(' ') if move]
    match_file = tmp_path / 'match.txt'
    cli = CLI(['--match-file', str(match_file)])
    cli.game = Game(moves_list)
    cli.write_match_file()
    assert match_file.read_text() == moves_str

# TODO
@pytest.mark.skip(reason="test not implemented")
def test_print_full_game():
    assert False

def test_make_move():
    cli = CLI([])
    cli.make_move('a4')
    assert Square('a', 4) in cli.game.boards[-1]

def test_make_move_auto_save(tmp_path):
    match_file = tmp_path / 'match.txt'
    cli = CLI(['--auto-save', '--match-file', str(match_file)])
    move = 'a2Pa4'
    cli.make_move(move)
    assert match_file.read_text().rstrip('\n') == move

@pytest.mark.mock_input_data('a4')
def test_interactive_loop_move(mock_input):
    cli = CLI(['--interactive'])
    with pytest.raises(BreakInteractiveException):
        cli.interactive_loop()
    assert Square('a', 4) in cli.game.boards[-1]

@pytest.mark.mock_input_data('exit')
def test_interactive_loop_exit(mock_input):
    cli = CLI(['--interactive'])
    with pytest.raises(SystemExit) as e:
        cli.interactive_loop()
    assert e.value.code == 0

def test_cmd_help(capsys):
    help_text = """Available commands:
  exit: quit the program (you can also use ctrl+D)
  help: Print this help
  [move ]<move>: Make a <move> on the board: [<source_file>][<source_rank>]<piece><target_file><target_rank> (e.g. 'move d3Qe5' or 'a5')
  save [<file>]: auto save the game to match file provided at startup or to <file>
  show <file><rank>: highlight all possible moves for piece on square with file and rank (e.g. 'show a3').
"""
    CLI([]).cmd_help()
    assert help_text in capsys.readouterr().out

def test_cmd_move():
    cli = CLI([])
    cli.cmd_move('a4')
    assert Square('a', 4) in cli.game.boards[-1]

def test_cmd_move_ambigous(capsys,ambigous_game):
    cli = CLI([])
    cli.game = ambigous_game
    cli.cmd_move('Ne5')
    assert "Unable to infere the piece you want to move" in capsys.readouterr().out

def test_cmd_move_malformed(capsys):
    cli = CLI([])
    cli.cmd_move('string')
    assert "Wrong move format" in capsys.readouterr().out

def test_cmd_move_illegal(capsys):
    cli = CLI([])
    cli.cmd_move('d2Pd8')
    assert "Illegal move" in capsys.readouterr().out

def test_cmd_show(capsys):
    pos = Square('a', 2)
    cli = CLI([])
    board = cli.game.boards[-1]
    board.print(mark=board[pos].possible_moves(board))
    board_out = capsys.readouterr().out
    cli.cmd_show(str(pos))
    cli_out = capsys.readouterr().out
    assert cli_out == board_out

def test_cmd_show_malformed(capsys):
    cli = CLI([])
    cli.cmd_show('string')
    assert "rong location format" in capsys.readouterr().out
    cli.cmd_show('d4')
    assert "No piece on square d4" in capsys.readouterr().out

def test_cmd_save(tmp_path, capsys):
    match_file = tmp_path / 'match.txt'
    cli = CLI(['--match-file', str(match_file)])
    move = 'a2Pa4'
    cli.game = Game([move])
    cli.cmd_save()
    assert match_file.read_text().rstrip('\n') == move
    assert f"saving to `{cli.args.match_file}`" in capsys.readouterr().out

def test_cmd_save_filename(tmp_path):
    match_file = tmp_path / 'match.txt'
    cli = CLI([])
    move = 'a2Pa4'
    cli.game = Game([move])
    cli.cmd_save(str(match_file))
    assert cli.args.match_file == str(match_file)
    assert cli.args.auto_save == True
    assert match_file.read_text().rstrip('\n') == move

def test_cmd_save_missing(capsys):
    cli = CLI([])
    cli.cmd_save()
    assert f"No match file" in capsys.readouterr().out

def test_cmd_exit():
    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as e:
        # need to pass empty arguments here. Otherwise the pytest command line
        # arguments are parsed which results in a wrong exit code.
        CLI([]).cmd_exit()
    assert e.value.code == 0
