from . import piece

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

    def __init__(self, pieces):
        """Build the board from a list of pieces

        :param pieces: list of pieces on the board
        """
        # TODO check if two pieces are on the same square
        # TODO check if pieces are within board
        self._pieces = pieces
        # TODO default dict?
        self.index = {}
        for piece in pieces:
            self.index[piece.position] = piece

    def __repr__(self):
        return f"<Board pieces={len(self)}>"

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self._pieces)

    def __getitem__(self, key):
        if not isinstance(key, Square):
            key = Square(key)
        return self.index[key]

    def __contains__(self, item):
        """If Board is checked against a Square, it will return True if there's
        a piece on the square, False otherwise. If checked against a tuple of
        (AbstractPiece, Color) it returns true if a piece of that kind and color
        is still on the board.
        """
        if isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[0], piece.AbstractPiece) and isinstance(item[1], Color):
                return item in [(piece, piece.color) for piece in self._pieces]
            else:
                item = Square(item)
        if isinstance(item, Square):
            return item in self.index
        else:
            raise TypeError("Board can only contain (Abstract)Piece or check if Square is empty")

    def __iter__(self):
        """Iterating over the board object returns every square of the board
        and the pieces that's on it. None if the square is empty.
        :returns square, piece:
        """
        self._iter = Square(-1,0)
        return self

    def __next__(self):
        if self._iter.x < BOARD_LEN-1:
            self._iter += (1,0)
        elif self._iter.y < BOARD_LEN-1:
            self._iter = Square(0, self._iter.y+1)
        else:
            raise StopIteration
        return self._iter, self[self._iter] if self._iter in self.index else None

    def pieces(self, kind=None):
        """Returns a list of all pieces on the board. If kind is given (as an
        instance of an Abstract(Piece)) only the pieces of that kind are returned.
        """
        # TODO add color constraint?
        if kind is None:
            return self._pieces
        else:
            return list(filter(lambda a, b=kind: a==b, self._pieces))

    def print(self, unicode=True):
        """Print the board

        :param unicode: use unicode symbols

        """
        # TODO
        # - :param inverted: invert colors for unicode (useful for White-on-Black terminals)
        # - for interactive mode, print up-side-down

        print('  abcdefgh  ')
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
        print('  abcdefgh  ')


