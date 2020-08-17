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
