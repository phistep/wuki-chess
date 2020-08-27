# wuki
_a toy chess engine_

## How to Run
A commandline application is supplied to continue a game from a supplied match
file. The file contains moves in
[Standard Algebraic Notation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)),
a pair of moves per line:

	e4 e5
	Nf3 Nc6
	Bb5 a6

The file is supplied as a commandline argument.

	$ PYTHONPATH=. bin/wuki -f match.txt

If you want to play against the AI, pass a game file that has black on the turn
and turn the AI on

	$ PYTHONPATH=. bin/wuki -f match.txt --ai

This will print the AI's next move and exit.
You probably want to save the output and continue making moves, so how about

	$ PYTHONPATH=. bin/wuki -f match.txt -s --ai -m 'e4'

If you run commands like these multiple times, you contune the same game
over multiple invocations.
But there is also an interactive mode

	$ PYTHONPATH=. bin/wuki -f match.txt -s --ai -i

This lets you continously enter moves and prints the current board.
It also has some neat features such as previewing possible moves for pieces.
For more information about all commands that can be used within the interactive
session, type `help`.

For information about other arguments, ask `bin/wuki --help`.

For all the extra fancy-pants out there, a minimal GUI based on
[`wxPython`](https://wxpython.org/) is also supplied.
It should work on all major platforms, but has only been tested with Linux/GTK.
For now, you always play white against the AI.

	$ PYTHONPATH=. bin/wuki-gui

For more information about the proveded executables, please refer to the
[User Guide](./docs/guide.rst#executables).


## Using the Library
For a thorough description of the structure of the library and more examples,
please refer to the [User Guide](./docs/guide.rst#using-the-api).

Simply setting up a game and moving some pieces around works like this:
```python
from wuki.game import Game
from wuki.board import Board, Square
from wiki.piece import White, Queen

game = Game(['e4', 'e5', 'Nf3'])
game.print_board()
game.make_move('Nc6')
game.print_board()
```

Instead of moving pieces until you reached your desired board constellation,
you can simply manipulate the internal data:
```python
# is this cheating?
game.boards[-1].add(Piece(Queen(), White, Square('d4')))
game.print_board()
```
Boards are construced from a list of `Piece`s:
```python
king = Pice(King(), White, Square('a1'))
queen = Pice(Queen(), White, Square('b2'))
board = Board([king, queen])
board.print()
```

Setting up a game against the AI works like this:
```python
from wiki.board import Black
from wuki.ai import WukiAI
from wuki.game import Game

ai = WukiAI(Black)
game = Game([])

# playing as white
game.make_move('e4')
game.print_board()

ai_move = ai.get_move(game.boards[-1])
game.make_move(*ai_move)
game.print_board()
```

## API Documentation
Please refer to the full [API Documentation](./docs/api.rst).
This project uses [Sphinx](https://sphinx-doc.org) to automatically generate
the documentation from the source code.
So install Sphinx, and run `make html` in `./docs/` to get documentation in
`[./docs/_build/html/index.html](./docs/_build/html/index.html)`.
Alternatively you can use Pythons internal
[help()](https://docs.python.org/3/library/functions.html#help) function
to access the docstrings, or read the source directly.
