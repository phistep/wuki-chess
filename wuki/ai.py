from random import sample
from pprint import pprint

from .board import Board

class WukiAI:
    def __init__(self, color):
        self.color = color
        print(f"Hi, I'm Wuki, playing {self.color}.")

    def get_move(self, board, color=None):
        print("Trying to think of a good move.")
        if color is None:
            color = self.color
        possible_moves = board.possible_moves(self.color)
        #print("possible moves:", possible_moves)
        move = None
        while move is None:
            move = sample(possible_moves, 1)[0]
            print("random move:", move)
            possible_moves.discard(move)
            new_board = board.make_move(*move, color=self.color)
            if new_board.is_checkmate(self.color):
                print("board is checkmate for myself, trying a different move")
                move = None
            print("I decided on a move:", move)
        return move
