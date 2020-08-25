import cProfile
import pstats
from sys import argv
from wuki.game import Game, White
from wuki.ai import WukiAI

filename = 'ai.profile'

def analyze():
    p = pstats.Stats(filename)
    p.strip_dirs().sort_stats(argv[2] if len(argv)>2 else 'cumulative').print_stats()

if len(argv) > 1 and argv[1] == '-a':
    analyze()
else:
    game = Game([])
    ai = WukiAI(White)
    cProfile.run('ai.get_move(game.boards[-1])', filename=filename)
    analyze()
