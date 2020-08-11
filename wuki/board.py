from .helpers import BOARD_LEN, White, Black, square_color

class Board:
    """Stores a board position"""
    # TODO implement self.__getitem__ for self.index lookup https://docs.python.org/3/reference/datamodel.html#object.__getitem__
    # TODO implement __contains__ for positions (piece @ position) and pieces (kind of piece still on board?)
    # TODO implement __iter__ over all pieces
    # TODO implement iterator over all squares

    def __init__(self, pieces):
        """Build the board from a list of pieces

        :param pieces: list of pieces on the board
        """
        self.pieces = pieces
        self.index = {}
        for piece in pieces:
            self.index[piece.position] = piece

    def __repr__(self):
        return f"<Board pieces={len(self.pieces)}>"

    def __str__(self):
        return self.__repr__

    def print(self, unicode=True):
        """Print the board

        :param unicode: use unicode symbols

        """
        # TODO
        # - :param inverted: invert colors for unicode (useful for White-on-Black terminals)
        # - for interactive mode, print up-side-down

        print('  abcdefgh')
        for y in reversed(range(BOARD_LEN)):
            print(y+1, end=' ')
            for x in range(BOARD_LEN):
                pos = (x,y)
                if pos in self.index:
                    if unicode:
                        symbol = self.index[pos].symbol
                    else:
                        symbol = self.index[pos].letter
                else:
                    if unicode:
                        symbol = '█' if square_color(pos) == Black else ' '
                    else:
                        symbol = '#' if square_color(pos) == Black else ' '
                print(symbol, end='')
            print('', y+1)
        print('  abcdefgh')


