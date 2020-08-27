"""
wuki.game
----------------

This module includes the :class:`Game` class, which describes the highest
level of description for a game of chess.
"""

from typing import Union, Tuple
import re

from . import piece
from .board import Color, White, Black, Square, Board
from .exceptions import WrongPlayerError, MoveParseError, AmbigousMoveError
from .exceptions import CheckException, CheckmateException, DrawException


class Game:
    """Holds all information about a game.

    A list of moves in |SAN|_ is parsed and for each move the
    resulting board position is generated. A new move can be added by
    calling :meth:`.make_move`.
    """
    #: :type: Color
    #:
    #: The player who has the first move.
    #: In chess, this is white.
    FIRST_PLAYER = White

    def __init__(self, moves):
        """Create a game from an array of |SAN|_ moves

        :param List[str] moves: list of strings with single moves in |SAN|_
            fromat

        .. automethod:: __len__
        .. automethod:: __str__
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
        #: :type: List[Board]
        #:
        #: The list of all board positions that have been played in this game,
        #: in chronological order.
        self.boards = [Board(initial_pieces)]

        #: :type: Color
        #:
        #: The color of the current player. Is initialized to :attr:`FIRST_PLAYER`
        self.current_player = self.FIRST_PLAYER

        #: :type: List[Tuple[piece.Piece, Square]]
        #:
        #: The moves that have been played, in chronological order.
        self.moves = list()
        for move in moves:
            self.make_move(move)

    def __repr__(self):
        return f"<Game moves={len(self.moves)} current_player={self.current_player}>"

    def move_str(self, move:Tuple[piece.Piece, Square]) -> str:
        """Format a move tuple ``(piece, target)`` into :samp:`a3Qa8`.

        :param move: tuple with a source :class:`~.piece.Piece` and a target
            :class:`.Square`
        
        :returns: a string in |SAN|_ describing the move
        """
        piece_, target = move
        if piece_.piece == piece.King():
            if piece_.position.x - target.x == 2:
                # queenside
                return '0-0-0'
            elif piece_.position.x - target.x == -2:
                # kingside
                return '0-0'
        return '{}{}{}'.format(piece_.position, piece_.letter.upper(), target)

    def __str__(self) -> str:
        """:returns: |SAN|_ of the whole game."""
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

    def __len__(self) -> int:
        """:returns: The length of the game is the number of moves that have been played."""
        return len(self.moves)

    def parse_move(self, move:str, current_player:Color=None, board:Board=None) -> Tuple[piece.Piece, Square]:
        """Parse a move string in |SAN|_ and returns the source
        :class:`~piece.Piece` to be moved and the target :class:`Square` it
        should be moved to.

        A move in |SAN| has the following syntax:

            :samp:`[{<source-piece>}][{<source-file>}][{<source-rank>}][{<piece>}]{<target-file>}{<target-rank>}`.

            - :samp:`{<source-…>}` information may be absent or partial.
            - :samp:`{<piece>}` needs to be a capital letter. Missing means a pawn was moved.

        e.g. :samp:`d3Qd5` or :samp:`ed5`.

        :param move: Move in the |SAN|_ format
        :param current_player: which player makes the move. Important to
            determining source square, defaults to
        :param Board board: On which board to look for the source square:

        :returns:
            - **source** (:class:`~piece.Piece`) -- the piece to be moved
            - **target** (:class:`Square`) -- the square the piece is to be moved to

        :raises MoveParseError: when move is not in the correct format
        """
        if current_player is None:
            current_player = self.current_player
        if board is None:
            board = self.boards[-1]

        # treat castling separately
        if "0-" in move:
            y = current_player.home_y
            king = board[Square(4,y)]

            if move == "0-0":
                # kingside
                target = Square(6,y)
            elif move == "0-0-0":
                # queenside
                target = Square(2,y)

            if target in king.possible_moves(board):
                return king, target
            else:
                raise MoveParseError("Castling not possible", move)

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

    def make_move(self, piece:Union[piece.Piece,str], target:Square=None):
        """Move on the current board.

        :param piece: the piece that is supposed to be moved. It includes
            its position on the board; can also be a string with a move
            :samp:`a1Qa6`, then the ``target`` parameter has to be ommited
        :param target: the square the piece to be moved to

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
        # TODO this is incredibly slow, maybe not do this every round?
        #try:
        #    self.check_state()
        #except CheckException:
        #    # a check does not prevent a new move to be made
        #    pass
        self.boards.append(self.boards[-1].make_move(piece, target))
        self.moves.append((piece, target))
        self.current_player = ~self.current_player

    def undo(self, n:int=1):
        """Undo the last move

        :param n: how many moves to undo
        """
        if len(self.boards) > n and len(self.moves) > n-1:
            del self.boards[-n:]
            del self.moves[-n:]
            self.current_player = self.current_player if n%2==0 else ~self.current_player

    def print_board(self, board:Board=None, **kwargs):
        """Print a board or the current board.

        :param board: a board print, defaults to the current board
        :param \**kwargs: keyword arguments are directly passed to
            :meth:`.Board.print()`
        """
        if board is None:
            board = self.boards[-1]
        board.print(**kwargs)

    def check_state(self, player:Color=None):
        """Checks the current board for a special game state and raises an
        exception if anything unusual is going on.

        :param player: the player to check for, defaults to
            :attr:`current_player`

        :raises GameOverException: When the game is over. The
            :attr:`~.GameOverException.winner` attribute is either
            :data:`~.board.White`, :data:`~.board.Black` or :py:data:`None` for
            remis. This exception also comes in :exc:`.CheckmateException` and
            :exc:`.DrawException` flavors.
        :raises CheckException: When the current player is under check. The
            :attr:`~.exception.CheckmateException.player` attribute is either
            :data:`~.board.Black` or :data:`~.board.White`.
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

