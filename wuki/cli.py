import argparse
import readline
from sys import exit

from .game import Game
from .board import Square, Board
from .errors import IllegalMoveError, MoveParseError, AmbigousMoveError

class CLI:
    """A commandline interface to play chess with wuki

    Initializing an object parses commandline arguments. .main() runs the
    application.

    Methods prefixed with `cmd_` are used as user commands in interactive mode.
    """
    def __init__(self):
        """Initialize CLI by parsing commandline arguments and setting up a game"""
        parser = argparse.ArgumentParser(description='Wuki chess engine')
        parser.add_argument('match_file', type=str,
                help="Match file containing all previous moves in chess notation")
        parser.add_argument('-a', '--all-moves', action='store_true',
                help = 'Print all moves in the game')
        parser.add_argument('-A', '--ascii', action='store_true',
                help='Use ascii characters and letters instead of unicode chess symbols')
        parser.add_argument('-m', '--move', type=str,
                help='Make a move and store it into the match file')
        #parser.add_argument('-g', '--gui', action='store_true',
        #        help='Launch GUI')
        #parser.add_argument('-p', '--plot', action='store_true',
        #        help='Generate visual representation of the game in match file')
        parser.add_argument('-i', '--interactive', action='store_true',
                help='Take opponent moves for STDIN')
        #parser.add_argument('-I', '--inverted-colors', action='store_true',
        #        help='Print symbols in inverted colors for White-on-Black terminals')
        parser.add_argument('-s', '--auto-save', action='store_true',
                help='Automatically save new moves to <match_file>')
        self.args = parser.parse_args()
        moves = self.parse_match_file()
        self.game = Game(moves)

    def main(self):
        """Main function that provides the CLI interface.

        Prints some information about the game, performs moves or runs in
        interactive mode.
        """
        print(self.game)

        if self.args.all_moves:
            print_full_game()
        else:
            self.game.print_current_board()
            print()

        if self.args.move:
            self.make_move(self.args.move)

        if self.args.interactive:
            try:
                self.interactive_loop()
            # except GameOverException
            # exit()
            except Exception as e:
                raise e

        print('next:', self.game.current_player)

    def parse_match_file(self):
        """Parses a match file in Algebraic Notation into a list of move strings.

        :param match_file: the path to the file to be parsed

        :returns moves: a list list of move strings e.g. ['b3']
        """
        with open(self.args.match_file) as match_file:
            rounds = match_file.read().split('\n')
            return [move for round_ in rounds for move in round_.split(' ') if move]

    def write_match_file(self):
        # TODO docstring
        with open(self.args.match_file, 'w') as match:
            return match.write(str(self.game))

    def print_full_game(self):
        """Print all boards of the game"""
        self.game.boards[0].print()
        print()
        for n, (board, move) in enumerate(zip(self.game.boards[1:], self.game.moves)):
            print(f"{n}. {move[0].color}: {game.move_str(move)}")
            self.print(unicode=unicode)
            print()

    def make_move(self, move):
        # TODO docstring
        self.game.make_move(move)
        self.game.print_current_board(unicode=not self.args.ascii)
        if self.args.auto_save:
            write_match_file(args.match_file, self.game)
        print()

    def interactive_loop(self):
        """Query user for moves continously until game is over.

        :param unicode: wether to print unicode or ascii characters
        :param auto_save: None or a path to a file the session should be saved to

        :param game: A running game to start the session with. Defaults to new game
        """
        # TODO :raises GameOverException:

        self.cmd_help()
        while True:
            command_line = input(f'{self.game.current_player}: ')
            parts = command_line.split(' ')
            try:
                run_command = getattr(self, 'cmd_'+parts[0])
                run_command(*parts[1:])
            except AttributeError:
                self.cmd_move(parts[0])

    def cmd_help(self, *args):
        """help: Print this help"""
        available_commands = [f for f in dir(self) if f.startswith('cmd_')]
        helps = [getattr(self, f).__doc__ for f in available_commands]
        print("Available commands:")
        print('  '+'\n  '.join(helps))

    def cmd_move(self, *args):
        """[move ]<move>: Make a <move> on the board: [<source_file>][<source_rank>]<piece><target_file><target_rank>"""
        try:
            self.make_move(args[0])
        except AmbigousMoveError:
            print("Unable to infere the piece you want to move. Specify its current location.")
        except MoveParseError as e:
            print("Wrong move format. Try `help`")
            #print(e.reason)
        except IllegalMoveError:
            print("Illegal move, try again")

    def cmd_show(self, *args):
        """show <piece>: highlight all possible moves for <piece>: <file><rank>"""
        file_, rank = args[0]
        position = Square(file_, int(rank))
        board = self.game.boards[-1]
        possible_moves = board[position].possible_moves(board)
        board.print(mark=possible_moves, unicode=not self.args.ascii)

    def cmd_save(self, *args):
        """save [<file>]: auto save the game to match file provided at startup or to <file>"""
        if args:
            self.args.match_file = args[0]
        if self.args.match_file:
            self.write_match_file()
        else:
            print("No match file given")

    def cmd_exit(self, *args):
        """exit: quit the program"""
        exit()
