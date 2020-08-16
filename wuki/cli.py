import argparse
import readline
from sys import exit

from .game import Game

def parse_match_file(match_file):
    """Parses a match file in Algebraic Notation into a list of move strings.

    :param match_file: the path to the file to be parsed

    :returns moves: a list list of move strings e.g. ['b3']
    """
    with open(match_file) as match:
        rounds = match.read().split('\n')
        return [move for round_ in rounds for move in round_.split(' ') if move]

def write_match_file(match_file, game):
    with open(match_file, 'w') as match:
        return match.write(str(game))

def print_full_game(game, unicode=True):
    """Print all boards of the game

    :param Game game: the game object which contains all the moves and boards
    :param unicode: wether to print unicode or ascii characters
    """
    game.boards[0].print()
    print()
    for n, (board, move) in enumerate(zip(game.boards[1:], game.moves)):
        print(f"{n}. {move[0].color}: {game.move_str(move)}")
        board.print(unicode=unicode)
        print()


def main():
    """Main function that provides the CLI interface.

    Parses commandline arguments, reads the game file, launches interactive
    sessions, etc.
    """

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
    #parser.add_argument('-i', '--interactive', action='store_true',
    #        help='Take opponent moves for STDIN')
    #parser.add_argument('-I', '--inverted-colors', action='store_true',
    #        help='Print symbols in inverted colors for White-on-Black terminals')
    parser.add_argument('-s', '--auto-save', action='store_true',
            help='Automatically save new moves to <match_file>')
    args = parser.parse_args()

    moves = parse_match_file(args.match_file)
    game = Game(moves)
    print(game)

    if args.all_moves:
        print_full_game(game, unicode=not args.ascii)
    else:
        game.print_current_board(unicode=not args.ascii)
        print()

    if args.move:
        game.make_move(args.move)
        game.print_current_board(unicode=not args.ascii)
        print(game)
        if args.auto_save:
            print(write_match_file(args.match_file, game))
        print()

    print('next:', game.current_player)

