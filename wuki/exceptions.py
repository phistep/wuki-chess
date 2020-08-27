class IllegalMoveError(Exception):
    """A move cannot be made (piece cannot move to target square)."""
    pass

class MoveParseError(Exception):
    """Malformed move string is not in Algebraic Notation and cannot be parsed."""
    def __init__(self, reason, move):
        self.reason = reason
        self.move = move

class AmbigousMoveError(MoveParseError):
    """Move string cannot be parsed because source piece cannot be infered."""
    pass

class WrongPlayerError(Exception):
    """Wrong player tried to make a move."""
    pass


class GameOverException(Exception):
    """The game is over."""
    def __init__(self, winner, reason='checkmate'):
        #: :type: Color
        #:
        #: The color of the winning party
        self.winner = winner

        #: :type: str
        #:
        #: The reason points out why the game ended. For example a checkmate
        #: by one of the players, a draw where one player cannot move anymore,
        #: etc.
        self.reason = reason

class CheckmateException(GameOverException):
    """The game ended by checkmate."""
    pass

class DrawException(GameOverException):
    """The game ended by remis."""
    def __init__(self, reason):
        self.winner = None
        self.reason = reason

class CheckException(Exception):
    """The player is under check."""
    def __init__(self, player):
        self.player = player
