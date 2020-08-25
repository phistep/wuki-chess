import re

from . import piece
from .board import White, Black, Square, Board
from .exceptions import WrongPlayerError, MoveParseError, AmbigousMoveError
from .exceptions import CheckException, CheckmateException, DrawException


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
            raise MoveParseError('Wrong move format', move)
        piece_id = matches['piece'] if matches['piece'] else ('P' if current_player is White else 'p')
        target = Square(matches['target_file'], int(matches['target_rank']))
        if ('source_file' in matches and matches['source_file']
            and 'source_rank' in matches and matches['source_rank']):
            source = Square(matches['source_file'], int(matches['source_rank']))
            piece_ = board[source]
        else:
            possible_pieces = board.pieces(kind=piece.piece_by_letter[piece_id], color=current_player)
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
                raise AmbigousMoveError('Source piece inference not possible', move)
        if not piece_id.upper() == piece_.letter.upper():
            raise MoveParseError(f"Specified source piece and piece on that square do not match (is {piece_.letter.upper()})", move)
        if not current_player == piece_.color:
            print(repr(piece_))
            raise MoveParseError("Color of piece at source square does not match current player", move)
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
        :raises GameOverException: when the game is over and no move can be made
            anymore
        """
        if isinstance(piece, str) and target is None:
            piece, target = self.parse_move(piece)
        elif target is None:
            raise ValueError("Either move is passed as string or piece and target have to be supplied")
        if piece.color != self.current_player:
            raise WrongPlayerError(f"current player: {self.current_player}")
        try:
            # TODO this is incredibly slow, maybe not do this every round?
            #self.check_state()
            pass
        except CheckException:
            # a check does not prevent a new move to be made
            pass
        self.boards.append(self.boards[-1].make_move(piece, target))
        self.moves.append((piece, target))
        self.current_player = ~self.current_player

    def undo(self, n=1):
        """Undo the last move

        :param n: how many moves to undo
        """
        if len(self.boards) > n and len(self.moves) > n-1:
            del self.boards[-n:]
            del self.moves[-n:]
            self.current_player = self.current_player if n%2==0 else ~self.current_player

    def print_board(self, board=None, **kwargs):
        """Print a board or the current board.

        :param board: a board print, defaults to the current board
        :param **kwargs: keyword arguments are directly passed to Board.print()
        """
        if board is None:
            board = self.boards[-1]
        board.print(**kwargs)

    def check_state(self, player=None):
        """Checks the current board for a special game state and raises an
        exception if anything unusual is going on.

        :param player: the player to check for

        :raises GameOverException: When the game is over. The .winner attribute
            is either White, Black or None for remis. This exception also comes
            in CheckmateException, WhiteWinsException, BlackWinsException and
            DrawException flavors.
        :raises CheckException: When the current color is under check. The
            .player attribute is either Black or White.
        """
        if player is None:
            player = self.current_player
        current_board = self.boards[-1]
        if current_board.is_stalemate(player):
            raise DrawException(reason=f'stalemate {player}')
        # TODO a lot of other reasons for a draw
        if current_board.is_checkmate(player):
            raise CheckmateException(player)
        if current_board.is_check(player):
            raise CheckException(player)

