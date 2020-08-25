from .board import White, Black, Board, Square
from .piece import King, Queen, Rook, Bishop, Knight, Pawn

class WukiAI:
    piece_value = {
            Queen(): 9,
            Rook(): 5,
            Bishop(): 3,
            Knight(): 3,
            Pawn(White): 1,
            Pawn(Black): 1,
            }

    def __init__(self, color):
        self.color = color

    def get_move(self, board, color=None):
        """Get a move for a board position.

        :param Board board: the current boardp position
        :param Color color: which color to get a move for. Defaults to the
            AI objects initialized color

        :returns (Piece source, Square target): a move with a source piece and
            a target square to be input into Game.make_move()
        """

        #print("Trying to think of a good move.")
        if color is None:
            color = self.color
        possible_moves = board.possible_moves(self.color)
        move_rating = dict()
        for move in possible_moves:
            resulting_board = board.make_move(*move, color=self.color)
            score = self.evaluate_board(resulting_board)
            move_rating[move] = score
            #print(move, score)
        best_move = max(move_rating, key=lambda m: move_rating[m])
        return best_move

    def evaluate_board(self, board):
        """Evaluate a board position.

        It calls all self.eval_ functions and adds up their individual scores.

        :param Board board: the board to evaluate.

        :returns int score: a score how well the own color is doing on the boar.
            Higher is better.
        """
        possible_moves = board.possible_moves(self.color)
        evaluators = [getattr(self, f) for f in dir(self) if f.startswith('eval_')]
        results = {f.__name__: f(board, possible_moves) for f in evaluators}
        return sum(results.values())

    def eval_captured(self, board, *args):
        """Pieces oneself captured are scored positively by their value in pawns,
        pieces that the opponent captured (we lost) are scored negativley.
        """
        score = 0
        weight = 10
        for color in [White, Black]:
            for piece in board.captured[color]:
                score += weight * self.piece_value[piece.piece] * (-1 if color is self.color else 1)
        return score

    def eval_center(self, board, *args):
        """Controlling the core center d4,e4,d5,e5 is scored with 3 points,
        the adjacent fields with 1 point.
        """
        score = 0
        weight = 1
        core_center = set([Square('d',5), Square('e',5),
                           Square('d',4), Square('e',4)])
        broad_center = set([Square('c',6), Square('d',6), Square('e',6), Square('f',6),
                            Square('c',5),                               Square('f',5),
                            Square('c',4),                               Square('f',4),
                            Square('c',3), Square('d',3), Square('e',3), Square('f',3)])
        for piece in board.pieces(color=self.color):
            if piece.position in core_center:
                score += 3 * weight
            elif piece.position in broad_center:
                score += 1 * weight
        return score
