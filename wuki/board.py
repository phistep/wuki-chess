from math import sqrt

from . import piece as pc
from .errors import IllegalMoveError

BOARD_LEN = 8

class Color:
    """Collection of convenience functions for piece colors"""
    WHITE = 0
    BLACK = 1

    def __init__(self, color):
        self.color = color
        self.direction = [+1,-1][color]
        self.home_y = [0,BOARD_LEN-1][color]

    def __str__(self):
        """One letter representation of the color"""
        return 'white' if self.color is self.WHITE else 'black'

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
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, tuple) and len(other) == 2:
            other = Square(other)
        elif not isinstance(other, Square):
            raise TypeError(f"Can only compare Square with Square or 2-tuple, not {type(other)}")
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        """You can only add a tuple of coordinate offsets, not another Square"""
        if not len(other) == 2:
            raise TypeError("Only a tuple of length two can be added to a Square")
        return Square(self.x+other[0], self.y+other[1])

    @property
    def file(self):
        """The file/column of the square."""
        return "abcdefgh"[self.x]
    column = file

    @property
    def rank(self):
        """The rank/row of the square."""
        return self.y + 1
    row = rank

    def file_rank(self):
        """Returns a tuple of (file, rank)/(column, row) representation of the coordinates."""
        return (self.file, self.rank)

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

    def dist(self, other):
        """Euclidean distance between this square and another.
        
        :param Square other: the square to measure distance to. Can also be
            provided as 2-tuple, which gets casted to Square

        :returns float dist: euclidean distance sqrt(dx**2 + dy**2)
        """
        if isinstance(other, tuple) and len(other) == 2:
            other = Square(other)
        if not isinstance(other, Square):
            raise TypeError("Distance has to be between two Squares or a 2-tuple")
        return sqrt( (self.x-other.x)**2 + (self.y-other.y)**2 )

    def blocked_by(self, mover, blocker):
        """Check if `blocker` blocks `mover` from moving to `self` in a streight
        line.

        :param Square mover: the position from which the piece in question
            makes a move
        :param Square blocker: position which has a piece that could block the
            move

        :returns bool blocked: wether blocker blocks mover from moving to self
        """
        # unfortunately, this easy solution does _not_ work
        #return mover.dist(self) > mover.dist(blocker)

        # horizontals
        if (self.x == mover.x == blocker.x
            and   (mover.y < blocker.y < self.y
                or mover.y > blocker.y > self.y)):
            return True
        # verticals
        elif (self.y == mover.y == blocker.y
            and   (mover.x < blocker.x < self.x
                or mover.x > blocker.x > self.x)):
            return True
        # diagonals
        elif ((self in mover.diagonals() and blocker in mover.diagonals())
            and (   (mover.x < blocker.x < self.x and mover.y < blocker.y < self.y)    # NE
                 or (mover.x < blocker.x < self.x and mover.y > blocker.y > self.y)    # SE
                 or (mover.x > blocker.x > self.x and mover.y < blocker.y < self.y)    # NW
                 or (mover.x > blocker.x > self.x and mover.y > blocker.y > self.y))): # SW
            return True
        else:
            return False


def within_board(x, y=None):
    return Square(x,y).within_board()


class Board:
    """Stores a board position.

    Adding and removing of pieces is done via .add()/.remove(), to move piecese
    around according to the rules of the game, use .make_move(). One can
    iterate over the hole board using iter() or over its pieces by using
    iter(Board.pieces()). Supports indexing board[Square(x,y)] and member
    checking Piece in Board.
    """
    def __init__(self, pieces, captured=None):
        """Build the board from a list of pieces

        :param pieces: list of pieces on the board
        """
        # TODO check if two pieces are on the same square
        # TODO check if pieces are within board
        self._pieces = set(pieces)
        self.index = dict()
        for piece in self._pieces:
            self.index[piece.position] = piece
        if captured:
            # make a deep copy because lists are mutable
            self.captured = {White:captured[White].copy(), Black:captured[Black].copy()}
        else:
            self.captured = {White:set(), Black:set()}

    def __repr__(self):
        return f"<Board pieces={len(self)} {self._pieces}>"

    def __str__(self):
        return str(self._pieces)

    def __len__(self):
        """Returns number of pieces still on the board."""
        return len(self._pieces)

    def __eq__(self, other):
        return self._pieces == other._pieces and self.captured == other.captured

    def __getitem__(self, key):
        """Returns piece on the key square"""
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
            item = Square(item)
        if isinstance(item, Square):
            return item in self.index
        elif isinstance(item, pc.AbstractPiece):
            # we have to cast to list since set.__contains__ compares hashes
            # and these are different for Piece and AbstractPiece.
            # by forcing the set into a list, Piece.__eq__() is used element-
            # wise on the list and can give us fuzzy equivalence
            return item in list(self._pieces)
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

    def remove(self, piece):
        """Remove a piece from the board.

        :param piece: the piece to be removed from the board

        :returns piece: the piece that was removed

        :raises KeyError: if the piece is not on the board
        """
        del self.index[piece.position]
        self._pieces.remove(piece)
        assert piece not in self
        assert piece.position not in self.index
        return piece

    def capture(self, piece):
        """Capture a piece. It's removed from the board and added to the
        .caputured list.

        :param piece: the piece to be marked as captured

        :returns piece: the captured piece
        """
        self.remove(piece)
        # This disables comparisons
        #piece.position = None
        self.captured[piece.color].add(piece)
        return piece

    def add(self, piece):
        """Add a piece to the board.
        
        :param piece: the piece to be added

        :returns pieces: the current list of pieces after the new one was added

        :raises ValueError: if the target square already has a piece on it
        """
        if piece.position in self:
            raise ValueError("Target square already has a piece on it")
        self._pieces.add(piece)
        self.index[piece.position] = piece
        assert piece in self
        assert self.index[piece.position] == piece
        return piece

    def pieces(self, kind=None, color=None):
        """Returns a list of all pieces on the board. If kind is given (as an
        instance of an Abstract(Piece)) only the pieces of that kind are returned.
        If color is given, only pieces of that color are returned.

        :param kind: If a Piece or AbstractPiece is given, only pieces of that
            kind are returned
        :param  color: only pieces of that color are returned

        :returns: set of pieces on the board matching the conditions
        """
        return set([p for p in self._pieces if (p == kind if kind is not None else True) and (p.color == color if color is not None else True)])

    def make_move(self, piece, target, color=None):
        """Move on the current board and return the new board. This does not
        mutate the current object!

        :param Piece piece: the Piece that is supposed to be moved. It includes its
            position on the board
        :param Square target: the quare where the pieces is to be moved to

        :returns Board new_board: The new board after the move

        :raises IllegalMoveError: when move cannot be made
        """
        # TODO check for check, checkmate
        new_board = Board(self._pieces, captured=self.captured)
        if target in new_board:
            # there is something on the board
            if new_board[target].color == piece.color:
                raise IllegalMoveError("Cannot capture own piece {self[target]}")
            else:
                # capturing the piece
                new_board.capture(new_board[target])
        new_board.remove(piece)
        piece = piece.move_to(target, board=self)
        new_board.add(piece)
        return new_board

    def possible_moves(self, player, give_check=False):
        """Return a set of all possible moves a player could make.

        :param Color player: possible moves for this player.
        :param bool give: Retrun the squares that give check to the _other_
            player. For pawns, only squares that are under attack not squares
            that can be moved to are included. Don't take Kings' movement into
            account. Needed to stop recursion when finding possible moves for a
            King().possible_moves and stops the recursion.

        :returns: a set of possible moves {(Piece piece, Sqaure target)}
        """
        possible_moves = set()
        for piece in [p for p in self.pieces() if p.color == player]:
            if give_check and piece == pc.King():
                # We need to ignore King()s in order to check which squares are
                # blocked for the other King because people are attacking it.
                pass
            elif give_check and piece == pc.Pawn(player):
                # When returning only the squares that would give check if the
                # opponent king moved to it, we need to look at the quares a
                # Pawn can capture at not move to.
                # we can use Pawn().legal_moves() here, since the only way they
                # could be blocked (as usually determined by Piece.possible_moves())
                # is by a friendly piece s
                possible_moves |= piece.piece.legal_moves(piece.position, self, only_attacked=True)
            else:
                possible_moves |= piece.possible_moves(self)
        return possible_moves

    def print(self, unicode=True, color=True, mark=[], upside_down=False):
        """Print the board

        :param bool unicode: use unicode symbols
        :param bool color: wether to use xterm-265color control sequences for
            foreground-on-background coloring of the board
        :param List[Sqaure] mark: list of Sqaures to be marked (drawn in a
            shaded color)
        :param bool upside_down: wether to print upside down (for black to see
            it from their perspecitve)
        """
        def colored_symbol(square, mark=[]):
            if color:
                # 8 bit
                #bg_color = {White:47, Black:40}
                #fg_color = {White:37, Black:30}
                #fg_mark = {White:31, Black:31}
                #bg_mark = {White:43, Black:43}
                #return f"\x1b[48;{fg};{bg}m{symbol}\x1b[0m"

                # xterm-256color
                fg_color = {White:255, Black:16}
                #fg_mark = {White:196, Black:196}
                fg_mark = fg_color
                bg_color = {White:249, Black:239}
                # bg_mark = {White:112, Black:22} # green
                # bg_mark = {White:160, Black:52} # red
                bg_mark = {White:220, Black:130} # yellow

                if unicode:
                    symbol = self[square].piece.symbol[Black] if square in self else ' ' # always use black symbol as it is fully colored
                else:
                    symbol = self[square].letter if square in self else ' '
                if square in mark:
                    fg_color = fg_mark
                    bg_color = bg_mark
                fg = fg_color[self[square].color] if square in self else fg_color[White] # doesn't matter if the square is empty anyway
                bg = bg_color[square.color()]
                return f"\x1b[38;5;{fg}m\x1b[48;5;{bg}m{symbol}\x1b[0m"
            else:
                if unicode:
                    square_symbol = {White: ' ', Black: '█'}
                    square_symbol_marked = {White: '░', Black: '▓'}
                else:
                    square_symbol = {White: ' ', Black: '#'}
                    square_symbol_marked = {White: '.', Black: '@'}
                if square in self:
                    return self[square].symbol if unicode else self[square].letter
                else:
                    return square_symbol_marked[square.color()] if square in mark else square_symbol[square.color()]

        print(' abcdefgh ')
        for y in range(BOARD_LEN) if upside_down else reversed(range(BOARD_LEN)):
            print(y+1, end='')
            for x in range(BOARD_LEN):
                square = Square(x,y)
                print(colored_symbol(square, mark=mark), end='')
            print(y+1)
        print(' abcdefgh ')
        print('captured:')
        for color in [White,Black]:
            captured_symbols = [p.symbol if unicode else p.letter for p in self.captured[~color]]
            print(f'  {color}:', ''.join(captured_symbols) if captured_symbols else 'none')


