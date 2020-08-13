class IllegalMoveError(Exception):
    """A move cannot be made (piece cannot move to target square)."""
    pass

class MoveParseError(Exception):
    """Malformed move string is not in Algebraic Notation and cannot be parsed."""
    pass

class WrongPlayerError(Exception):
    """Wrong player tried to make a move."""
    pass
