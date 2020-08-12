BOARD_LEN = 8


class Color:
    """Collection of convenience functions for piece colors"""
    WHITE = 0
    BLACK = 1

    def __init__(self, color):
        self.color = color

    def __str__(self):
        """One letter representation of the color"""
        return 'w' if self.color is self.WHITE else 'b'

    def __repr__(self):
        return '<White>' if self.color is self.WHITE else '<Black>'

    def __hash__(self):
        return self.color

    def __invert__(self):
        """ ~ operator, returns opposite color"""
        return Color(1-self.color)

    def __eq__(self, other):
        return self.color == other.color

White = Color(Color.WHITE)
Black = Color(Color.BLACK)


class Square:
    """A square on the board."""

    def __init__(self, x, y=None):
        f"""A Square can be instanciated from a pair of coordinates either in

        - numerical form (x, y) where x and y should lie between 0 and {BOARD_LEN-1},
            0 being the white home row
        - alphanumeric form (file, rank) with file being the column 'a' through 'h'
            and rank bewing the row between 1 and {BOARD_LEN}, 1 being the white
            home row

        No bounds check is made automatically, illegal squares can be instanciated,
        one has to manually check with Square.within_board.

        :param x: either a tuple of coordinates as described above or a vertical coordinate
        :param y: optional if a tuple is passed in x, otherwixze the horizontal coordinate 
        """
        # TODO bounds check?
        #      use __new__ tow return a None object if not within bounds?
        # TODO support two piece string instancation ('b5') and comparison

        if isinstance(x, Square):
            self.x = x.x
            self.y = x.y
            return
        if y is None and isinstance(x, tuple) and len(x) == 2:
            xy = x
        elif y is not None:
            xy = (x, y)
        else:
            raise ValueError("Either x has to be a tuple or x and y coordinates have to be given separately")

        if isinstance(xy[0], int) and isinstance(xy[1], int):
            # coordinates given numerically: (1,4)
            self.x, self.y = xy
        elif isinstance(xy[0], str) and len(xy[0]) == 1 and isinstance(xy[1], int):
            # coordinates given in chess notation: ('b',5)
            self.x = "abcdefgh".index(xy[0])
            self.y = xy[1] - 1
        else:
            raise ValueError("Given coordinates have either (x,y) or (file,rank)")

    def __repr__(self):
        return f"<Square {self} x={self.x} y={self.y}>"

    def __str__(self):
        return ''.join([str(c) for c in self.file_rank()])

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __eq__(self, other):
        if isinstance(other, tuple) and len(other) == 2:
            other = Square(other)
        elif not isinstance(other, Square):
            raise TypeError("Can only compare Square with Square or 2-tuple")
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        """You can only add a tuple of coordinate offsets, not another Square"""
        if not len(other) == 2:
            raise TypeError("Only a tuple of length two can be added to a Sqaure")
        return Square(self.x+other[0], self.y+other[1])

    def file_rank(self):
        """Returns a tuple of (file, rank)/(column, row) representation of the coordinates."""
        # column
        file_ = "abcdefgh"[self.x]
        # row
        rank = self.y + 1
        return (file_, rank)

    def coords(self):
        "Return coordinate tuple (x,y)"
        return self.x, self.y

    def within_board(self):
        """Wether a position is within the bounds of the board"""
        return 0 <= self.x < BOARD_LEN and 0 <= self.y < BOARD_LEN

    def color(self):
        """Returns the color of the square on the board. (0,0)/a1 is Black."""
        return Color((self.x+1)%2 ^ self.y%2)

    def diagonals(self):
        """Gives all diagonally connected positions within the board (including self)"""
        rising   = [Square(self.x+i, self.y+i) for i in range(BOARD_LEN)]
        rising  += [Square(self.x-i, self.y-i) for i in range(BOARD_LEN)]
        falling  = [Square(self.x+i, self.y-i) for i in range(BOARD_LEN)]
        falling += [Square(self.x-i, self.y+i) for i in range(BOARD_LEN)]
        return set(filter(within_board, rising+falling))

    def orthogonals(self):
        """Gives all orthogonally connected positions within the board (including self)"""
        horizontal = [Square(x, self.y) for x in range(BOARD_LEN)]
        vertical =   [Square(self.x, y) for y in range(BOARD_LEN)]
        return set(horizontal + vertical)

def within_board(x, y=None):
    return Square(x,y).within_board()


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
                pos = Square(x,y)
                if pos in self.index:
                    if unicode:
                        symbol = self.index[pos].symbol
                    else:
                        symbol = self.index[pos].letter
                else:
                    if unicode:
                        symbol = '█' if pos.color() == Black else ' '
                    else:
                        symbol = '#' if pos.color() == Black else ' '
                print(symbol, end='')
            print('', y+1)
        print('  abcdefgh')


