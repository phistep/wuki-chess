from .game import Game

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Wuki chess engine')
    parser.add_argument('match_file', type=str, help="Match file containing all previous moves in chess notation")
    parser.add_argument('-m', '--move', action='store_true',
            help='Make a move and store it into the match file')
    #parser.add_argument('-g', '--graphics', action='store_true',
    #        help='Print terminal graphics')
    #parser.add_argument('-p', '--plot', action='store_true',
    #        help='Generate visual representation of the game in match file')
    #parser.add_argument('-i', '--interactive', action='store_true',
    #        help='Take opponent moves for STDIN')
    #parser.add_argument('-I', '--inverted-colors', action='store_true',
    #        help='Print symbols in inverted colors for White-on-Black terminals')
    parser.add_argument('-a', '--ascii', action='store_true',
            help='Use ascii characters and letters instead of unicode chess symbols')
    args = parser.parse_args()

    with open(args.match_file) as match_file:
        # split lines into list elements and remove empty lines
        moves = list(filter(None, match_file.read().split('\n')))
        game = Game(moves)
        print(game)
        print()
        game.print_current_board(unicode=not args.ascii)

