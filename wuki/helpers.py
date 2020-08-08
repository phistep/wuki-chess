
WHITE = 0
BLACK = 1
BOARD_LEN = 8

def color_str(color):
    """String representation of a color variable"""
    return 'w' if color is WHITE else 'b'

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
    return (position[0]+1)%2 ^ position[1]%2
