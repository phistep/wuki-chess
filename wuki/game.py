import re

from . import piece
from .board import White, Black, Square, Board
from .errors import WrongPlayerError, MoveParseError, AmbigousMoveError


class Game:
    """Holds all information about a game.

    A list of moves in Algebraic Notation is parsed and for each move the
    resulting board position is generated. A new move can be added by
    callgin `.make_move`.
    """
    FIRST_PLAYER = White

    def __init__(self, moves):
        """Create a game from an array of [algebraic notation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)) moves

        :param moves: list of single moves in Algebaric Notation
        """

        initial_pieces = []
        for color, row, direction in zip([White, Black], [1, 8], [+1, -1]):
            initial_pieces.extend([
                piece.Piece(piece.Rook(),   color, Square('a', row)),
                piece.Piece(piece.Knight(), color, Square('b', row)),
                piece.Piece(piece.Bishop(), color, Square('c', row)),
                piece.Piece(piece.King(),   color, Square('e', row)),
                piece.Piece(piece.Queen(),  color, Square('d', row)),
                piece.Piece(piece.Bishop(), color, Square('f', row)),
                piece.Piece(piece.Knight(), color, Square('g', row)),
                piece.Piece(piece.Rook(),   color, Square('h', row)),
            ])
            initial_pieces.extend([piece.Piece(piece.Pawn(color), color, Square(col, row+direction)) for col in "abcdefgh"])
        self.boards = [Board(initial_pieces)]

        self.current_player = self.FIRST_PLAYER
        self.moves = list()
        for move in moves:
            self.make_move(move)

    def __repr__(self):
        return f"<Game moves={len(self.moves)} current_player={self.current_player}>"

    def move_str(self, move):
        """Format a move tuple (Piece, Square target) into `a3Qa8`."""
        return '{}{}{}'.format(move[0].position, move[0].letter.upper(), move[1])

    def __str__(self):
        """Algebraic notation of the whole game"""
        moves = [self.move_str(m) for m in self.moves]
        # unfortunately, this does not output a single white move
        #return '\n'.join(w+' '+b for w, b in zip(moves[0::2], moves[1::2]))+'\n'
        rounds = []
        for i in range(0,len(moves),2):
            round_ = moves[i]
            if i+1 < len(moves):
                round_ += ' '+moves[i+1]
            rounds.append(round_)
        return '\n'.join(rounds)+'\n'

    def __len__(self):
        """The length of the game is the number of moves that have been played"""
        return len(self.moves)

    def parse_move(self, move, current_player=None, board=None):
        """Parse a move string in Algebraic Notation and returns the piece to
        be moved and the target squere it should be moved to.

        :param str move: Move in the format
            `<source_piece>?<source_file>?<source_row>?<piece>?<target_file><target_row>`
            `<source_…>` information may be absent or partial source
            `<piece`> missing means a pawn was moved, capital letter!
            e.g. 'd3Qd5' or 'ed5'
        :param Color current_player: Which player makes the move. Important to
            determining source square
        :param Board board: On which board to look for the source square:

        :returns Piece piece: piece to be moved
        :returns Square target: target square to be moved to

        :raises MoveParseError: when move is not in the correct format
        """
        if current_player is None:
            current_player = self.current_player
        if board is None:
            board = self.boards[-1]

        piece_letters = set(p.letter.upper() for p in self.boards[0].pieces())
        move_re = ( "(?P<source_file>[a-h])?"        # source file/col  a
                    "(?P<source_rank>[1-8])?"        # source rank/row  5
                    f"(?P<piece>[{piece_letters}]?)" # piece letter     Q
                    "(?P<target_file>[a-h])"         # target file/col  a
                    "(?P<target_rank>[1-8])"         # target rank/row  9
                    )
        try:
            matches = re.match(move_re, move).groupdict()
        except:
            raise MoveParseError(move, reason='Wrong move format')
        piece_id = matches['piece'] if matches['piece'] else 'P'
        target = Square(matches['target_file'], int(matches['target_rank']))
        if ('source_file' in matches and matches['source_file']
            and 'source_rank' in matches and matches['source_rank']):
            source = Square(matches['source_file'], int(matches['source_rank']))
            piece_ = board[source]
        else:
            possible_pieces = board.pieces()
            possible_pieces = [p for p in possible_pieces if p.color == current_player]
            possible_pieces = [p for p in possible_pieces if p.letter.upper() == piece_id]
            #print({p: p.possible_moves(board) for p in possible_pieces})
            possible_pieces = [p for p in possible_pieces if target in p.possible_moves(board=board)]
            if 'source_file' in matches and matches['source_file']:
                possible_pieces = [p for p in possible_pieces if p.position.file == matches['source_file']]
            if 'source_rank' in matches and matches['source_rank']:
                possible_pieces = [p for p in possible_pieces if p.position.rank == int(matches['source_rank'])]
            possible_pieces = list(possible_pieces)

            if len(possible_pieces) == 1:
                piece_ = possible_pieces[0]
            else:
                raise AmbigousMoveError(move, reason='Source piece inference not possible')
        if not piece_id == piece_.letter.upper():
            raise MoveParseError(move, reason=f"Specified source piece and piece on that square do not match (is {piece_.letter.upper()})")
        if not current_player == piece_.color:
            raise MoveParseError(move, reason="Color of piece at source square does not match current player")
        return piece_, target

    def make_move(self, piece, target=None):
        """Move on the current board.

        :param Piece piece: the piece that is supposed to be moved. It includes
            its position on the board.
            Can also be a string with a move "a1Qa6", then the target parameter
            has to be ommited
        :param Square target: the square the piece to be moved to

        :raises IllegalMoveError: when move cannot be made
        :raises WrongPlayerError: when the color of the pieces is not the one
            of the current player
        """
        if isinstance(piece, str) and target is None:
            piece, target = self.parse_move(piece)
        elif target is None:
            raise ValueError("Either move is passed as string or piece and target have to be supplied")
        if piece.color != self.current_player:
            raise WrongPlayerError(f"current player: {self.current_player}")
        self.moves.append((piece, target))
        self.boards.append(self.boards[-1].make_move(piece, target))
        self.current_player = ~self.current_player

    def print_current_board(self, unicode=True):
        """Print the current board.

        :param unicode: wether to use unicode or ascii symbols
        """
        self.boards[-1].print(unicode)
