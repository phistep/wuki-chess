BOARD_LEN = 8

class PlayerColor:
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
        return PieceColor(1-self.color)

    def __eq__(self, other):
        return self.color == other.color

White = PlayerColor(PlayerColor.WHITE)
Black = PlayerColor(PlayerColor.BLACK)


def within_board(position):
    """Wether a position is within the bounds of the board"""
    return 0 <= position[0] < BOARD_LEN and 0 <= position[1] < BOARD_LEN

def coord(col, row):
    """Chess column/row notation to numerical coordinates"""
    x = "abcdefgh".index(col)
    y = row - 1
    return (x, y)

def square(position):
    """numerical (x,y) tuple to chess column/row notation"""
    x, y = position
    col = "abcdefgh"[x]
    row = y + 1
    return (col, row)

def square_color(position):
    """Returns the color of a square on the board"""
    return PlayerColor((position[0]+1)%2 ^ position[1]%2)

def diagonals(position):
    """Gives all diagonally connected positions (including :param position:)"""
    rising   = [(position[0]+i, position[1]+i) for i in range(BOARD_LEN)]
    rising  += [(position[0]-i, position[1]-i) for i in range(BOARD_LEN)]
    falling  = [(position[0]+i, position[1]-i) for i in range(BOARD_LEN)]
    falling += [(position[0]-i, position[1]+i) for i in range(BOARD_LEN)]
    return set(filter(within_board, rising+falling))

def orthogonals(position):
    """Gives all orthogonally connected positions (including :param position:)"""
    horizontal = [(x, position[1]) for x in range(BOARD_LEN)]
    vertical = [(position[0], y) for y in range(BOARD_LEN)]
    return set(horizontal + vertical)

