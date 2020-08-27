"""
CLI
===
A commandline application is provided to play the game against another human
or against the ai.
If invoked without options it will just print a setup game and exit.
To make a move, supply one formatted in |SAN|_ by :option:`wuki --move`:

.. code-block:: bash

    $ PYTHONPATH=. bin/wuki -m e4

If you want to continue a game, provide a match file that contains moves in
|SAN|_, a pair of moves per line:

.. code-:block::

    e4 e5
    Nf3 Nc6
    Bb5 a6

And pass it via :option:`wuki --match-file`:

.. code-block:: bash

    $ PYTHONPATH=. bin/wuki -f match.txt

If you want to play against the AI, pass a game file that has black on the turn
and turn the AI on via :option:`wuki --ai`:

.. code-block:: bash

    $ PYTHONPATH=. bin/wuki -f match.txt --ai

This will print the AI's next move and exit.
You probably want to save the output and continue making moves, that's what
:option:`wuki --auto-save` is for:

.. code-block:: bash

    $ PYTHONPATH=. bin/wuki -f match.txt -s --ai -m 'e4'

If you run commands like these multiple times, you continue the same game
over multiple invocations.
But there is also an interactive mode :option:`wuki --interactive`

.. code-block:: bash

    $ PYTHONPATH=. bin/wuki -i

This lets you continously enter moves and prints the current board.
It also has some neat features such as previewing possible moves for pieces.
For more information about all commands that can be used within the interactive
session, type :command:`help`.

For a full list of commandline arguments, refer to :class:`CLI`.
"""
from typing import List

import argparse
import readline
from sys import exit
import atexit

from .game import Game
from .board import Square, Board, White, Black
from .exceptions import IllegalMoveError, MoveParseError, AmbigousMoveError
from . import ai

class BreakInteractiveException(Exception):
    pass

class CLI: 
    """A commandline interface to p lay chess with wuki

    Initializing an object parses commandline arguments and creates a Game
    instance; :meth:`.main()` runs the application.

    Methods prefixed with :meth:`cmd_` are used as user commands in interactive mode.
    """
    def __init__(self, args=None):
        """Initialize CLI by pa rsing commandline arguments and setting up a game

        :param args: you can either supply the arguments from the command
            line by initializing empty, or supply the options via a list of
            strings as in the commandline split at spaces


        .. program:: wuki

        .. option:: -a, --all-moves

            Print all moves in the game.

        .. option:: -A, --ascii

            Use ascii characters and letters instead of unicode chess symbols.

        .. option:: --ai

            Play against AI, you play white.

        .. option:: -C, --no-color
            
            Don't use xterm-265color control sequences for colored output.

        .. option:: -f match_file, --match-file match_file
            
            Match file containing all previous moves in |SAN|_.

        .. option:: -F', '--flip'
            
            Flip the board when it is Black's turn so both players play upward.

        .. option:: -i, --interactive

            Play in an interactive session.
             
        .. option:: -m move , --move move
            
            Make a move in |SAN|_

        .. option:: -s, --auto-save

            Automatically save new moves to the match file provided by
            :option:`--match-file`.
        """
        parser = argparse.ArgumentParser(description='Wuki chess engine')
        parser.add_argument('-a', '--all-moves', action='store_true',
                help = 'Print all moves in the game')
        parser.add_argument('-A', '--ascii', action='store_true',
                help='Use ascii characters and letters instead of unicode chess symbols')
        # TODO rename ascii -U --no-unicode, --all-moves => -A, -a -> --ai
        parser.add_argument('--ai', action='store_true',
                help="Play against AI, you play white.")
        parser.add_argument('-C', '--no-color', action='store_true',
                help="Don't use xterm-265color control sequences for colored output")
        parser.add_argument('-f', '--match-file', type=str,
                help="Match file containing all previous moves in chess notation")
        parser.add_argument('-F', '--flip', action='store_true',
                help="Flip the board when it is Black's turn so both players play upward")
        parser.add_argument('-i', '--interactive', action='store_true',
                help='Play in an interactive session')
        parser.add_argument('-m', '--move', type=str,
                help='Make a move')
        #parser.add_argument('-g', '--gui', action='store_true',
        #        help='Launch GUI')
        parser.add_argument('-s', '--auto-save', action='store_true',
                help='Automatically save new moves to <match_file>')
        #parser.add_argument('-p', '--plot', action='store_true',
        #        help='Generate visual representation of the game in match file')

        #: The parsed commandline arguments
        self.args = parser.parse_args(args)

        moves = self.parse_match_file() if self.args.match_file else []
        #: :type: Game
        #:
        #: The underlying game object that is played on.
        self.game = Game(moves)

        if self.args.ai:
            #: :type: ai.WukiAI
            #:
            #: If played against AI, the AI object is held here
            self.ai = ai.WukiAI(Black)

        atexit.register(self.cmd_exit)

    def main(self):
        """Main function that provides the commandline interface.

        Prints some information about the game, performs moves or runs in
        interactive mode.
        """
        if self.args.all_moves:
            self.print_full_game()
        else:
            self.print_board()
            print()

        if self.args.move:
            self.make_move(self.args.move)

        if self.args.interactive:
            try:
                self.interactive_loop()
            # except GameOverException
            # exit()
            except BreakInteractiveException:
                pass
        else:
            if self.args.ai and self.game.current_player == self.ai.color:
                move = self.ai.get_move(self.game.boards[-1])
                # TODO error handling
                print(self.game.move_str(move))
                self.make_move(self.game.move_str(move))
            else:
                print('next:', self.game.current_player)

    def print_board(self, board:Board=None, **kwargs):
        """Print a board to the screen. If none is given, print current board.

        Printing options that have been set in :data:`args` are respected.

        :param board: a Board, defaults to the current board.
        :param \**kwargs: all other keyword arguments are passed through to
            :meth:`.Board.print()`
        """
        self.game.print_board(
                board=board,
                unicode=not self.args.ascii,
                color=not self.args.no_color,
                upside_down=(self.args.flip and self.game.current_player == Black),
                **kwargs
                )

    def parse_match_file(self) -> List[str]:
        """Parses a match file in Algebraic Notation into a list of move strings.

        :returns moves: a list list of move strings e.g. ['b3']
        """
        try:
            with open(self.args.match_file) as match_file:
                rounds = match_file.read().split('\n')
                return [move for round_ in rounds for move in round_.split(' ') if move]
        except FileNotFoundError:
            return []

    def write_match_file(self):
        """Write the game to the match file provided as commandline argument
        or set in interactive mode.
        """
        with open(self.args.match_file, 'w') as match:
            return match.write(str(self.game))

    def print_full_game(self):
        """Print all boards of the game"""
        self.game.boards[0].print()
        print()
        for n, (board, move) in enumerate(zip(self.game.boards[1:], self.game.moves)):
            print(f"{n}. {move[0].color}: {self.game.move_str(move)}")
            self.print_board(board)
            print()

    def make_move(self, move):
        """Make a move on the board, maybe save it and print the new current board

        :param move: either move string or tuple of (Piece source, Square target)
            See :meth:`.Game.make_move()` for details.
        """
        self.game.make_move(move)
        self.print_board()
        if self.args.auto_save:
            self.write_match_file()
        print()

    def interactive_loop(self):
        """Query user for moves continously until game is over.

        This is a :py:mod:`readline` based interface.
        You can issue commands, which are forwareded to the :meth:`cmd_`
        methods of this class.

        The special value :samp:`__break__` will break out of the loop.
        """
        # TODO :raises GameOverException:

        print("Type `help` for a list of available commands.")
        while True:
            try:
                if self.args.ai:
                    if self.game.current_player == self.ai.color:
                        move = self.ai.get_move(self.game.boards[-1])
                        # TODO error handling
                        print(f"\nAI ({self.ai.color}): {self.game.move_str(move)}")
                        self.make_move(self.game.move_str(move))
                command_line = input(f'You ({self.game.current_player}): ')
                parts = command_line.split(' ')

                # special command to break out of the interactive loop without
                # exiting the program. used for testing and debugging
                if parts[0] == '__break__':
                    raise BreakInteractiveException

                run_command = getattr(self, 'cmd_'+parts[0])
                run_command(*parts[1:])
            except AttributeError:
                # no command of that name found, default to cmd_move
                self.cmd_move(parts[0])

    def cmd_help(self, *args):
        """help: Print this help"""
        available_commands = [f for f in dir(self) if f.startswith('cmd_')]
        helps = [getattr(self, f).__doc__ for f in available_commands]
        print("Available commands:")
        print('  '+'\n  '.join(helps))

    def cmd_move(self, *args):
        """[move ]<move>: Make a <move> on the board: [<source_file>][<source_rank>]<piece><target_file><target_rank> (e.g. 'move d3Qe5' or 'a5')"""
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
        """show <file><rank>: highlight all possible moves for piece on square with file and rank (e.g. 'show a3')."""
        try:
            file_, rank = args[0]
            position = Square(file_, int(rank))
            board = self.game.boards[-1]
            possible_moves = board[position].possible_moves(board)
            # for debugging: show blocked legal moves instead of possible moves
            #possible_moves = [sq for sq, _ in board for p in board.pieces() if sq.blocked_by(position, p.position)]
            self.print_board(board=board, mark=possible_moves)
        except ValueError:
            print("Wrong location format. Try `help`.")
        except:
            print(f"No piece on square {position} or wrong location format. Try `help`.")

    def cmd_save(self, *args):
        """save [<file>]: auto save the game to match file provided at startup or to <file>"""
        if args:
            self.args.match_file = args[0]
        if self.args.match_file:
            self.args.auto_save = True
            self.write_match_file()
            print(f"Auto saving to `{self.args.match_file}`")
        else:
            print("No match file given")

    def cmd_undo(self, *args):
        """undo: undo the last move"""
        self.game.undo(2 if self.args.ai else 1)
        if self.args.auto_save:
            self.write_match_file()
        self.print_board()

    def cmd_print(self, *args):
        """print: print the current game in Standard Algebraic Notation"""
        print(self.game)

    def cmd_exit(self, *args):
        """exit: quit the program (you can also use ctrl+D)"""
        exit(0)

