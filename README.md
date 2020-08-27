# wuki
_a toy chess engine_

## How to Run
A commandline application is supplied to continue a game from a supplied match
file. The file contains moves in [Algebraic Notation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)),
a pair of moves per line

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

For all the extra fancy-pants out there, a minimal GUI based on [`wxPython`](https://wxpython.org/)
is also supplied.
It should work on all major platforms, but has only been tested with Linux/GTK.
For now, you always play white against the AI.

	$ PYTHONPATH=. bin/wuki-gui

For information about other arguments, ask `bin/wuki --help`.


## Use the Library
For now you gotta read the source. The commandline application is in
`wuki/cli.py:CLI.main()`. The main game logic in `wuki/game.py`. The AI is
impllemented in `wuki/ai.py:WukiAI`

The class hirarchy works as follows:
1. `game.Game` stores all the info of a game.
It sets up an initial board and parses moves from a list passed at init to
reach the current game state.
From there you can use `game.Game.make_move()` to further progress the game.
2. Internally a game holds an instance of `board.Board` for each board position
encountered throught the game.
You get the current board from `game.Game.boards[-1]`.
`game.Game.make_move()` just checks if the color of the piece to be moved
matches the current player and then forwards the call to
`board.Board.make_move()`.
3. A `board.Board` is made up of a set of `piece.Piece`s.
These hold their type (`piece.AbstractPiece` subclasses), position on the board
`board.Square` and color `board.Color`.
`board.Board.make_move()` checks the target square for pieces and handles the
capturing, but forwards the movement to `piece.Piece.move_to()`
4. `piece.Piece.move_to()` checks if the move is possible by calling
`piece.Piece.possible_moves()`, which gives a list of all possible moves
for that piece on that board. It checks the underlying
`piece.AbstractPiece.legal_move()` for all moves according to the piece types
movement patterns and removes the onces that are blocked by other pieces on
the board and other forbidden moves (like kings cannot move into check).
5. Another important method is `board.Board.possible_moves()` which returns
a list of all possible moves on the board for a certain player.
It checks for check and only returns moves that end up not in check.

So your workflow might look something like
```python
from wuki.game import Game
from wuki.board import Board, Square
from wiki.piece import White, Queen

game = Game(['e4', 'e5', 'Nf3'])
game.print_board()
game.make_move('Nc6')
game.print_board()

# is this cheating?
game.boards[-1].add(Piece(Queen, White, Square('d4')))
game.print_board()
```

The AI is based on the following concept:
After initializing, an `ai.WukiAI` object can be queried for a move
`ai.WukiAI.get_move()` with a `board.Board`.
It takes that board position and generates all possible moves it can make and
their resulting board positions.
Then it evaluates each of these board positions on a number of criteria
(`ai.WukiAI.eval_*` methods) and chooses the move with the highghest score.

Settung up a game against the AI works like this:
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

## TODO
- general
	- check game state function super slow, how to realisticly use it in Game.make_move()
		- move is_stalemate and is_checkmate into Game / just into check_state
		- dont check is_check and king.possible_moves twice
		- profile blocked_by
	- in make_move shortcut the legality checks if you know the move comes from possible_moves (caching like in VAMP evaluation)
	- give reasons to IllegalMoveError(reason=""), eg check, wrong moving
	- rules
		- pawn promotion (goes in `Piece` and `Pawn`?
			- use exceptions to handle promotion?
			`Piece.move_to()` calls `AbstractPece.move_to()`
			`AbstractPiece.move_to()` just pass in other piece types, raises `PawnPromotionException`
		- draw
			- threefold repitition: same player has same board three times in a row
			- fifty-move rule: 50 moves without captire or pawn move
			- no path to checkmate (ooph)
		- en passent
	- different verbosity for ai and cli https://docs.python.org/3/howto/logging.html
	- check and checkmate gamefile parsing and writing
	- Color.__negate__() -> __not__()
- cli
	- support Portable game notation
		- read and write
		- comments
		- time
		- markers for check etc.
	- interactive mode
		- colorize last move
		- check into prompt, checkmate support
		- use https://docs.python.org/3/library/cmd.html
		- cmd_show: when arguments black/white show all possible movable pieces for player
		- add color block to prompt
		- timestamps and time constraint
		- restore input on `IllegalMoveError` or `MoveParseError`
		- trap ^C
	- convenience flags
		- -q --quiet: only print a move if there is one (by --move or by AI)
		- -w --white-ai,  -b --black-ai, -r --random-ai
		- -W --white-name, -B --black-name (for prompt, pgn file)
		- bong cloud opening
	- box drawing https://en.wikipedia.org/wiki/Box-drawing_character
	- matplotlib for pdf game output
	- localization?
	- online mode (host server, play against players/ais)
- gui
	- update UI before AI starts to think
	- loading indicator for AI
	- undo
	- select/load/save game file
	- show current player
	- select opponent: human/ai
	- show captured
	- pawn promotion
	- handle game end
	- icon, app name, about, etc
- ai
	- lookahead
	- evaluation function for each board position
		- init with map for weight for each eval function
		- allow black/whitelist for strategies
		- allow to pass list of custom strategy functions
			- check
			- checkmate
			- capturing (only equal weight or uncovered)
			- pawn promotion
			- double pawns
			- attacks
			- cover
			- freedom of movement
			- pawn walk if noone in front -> promotion
		- error
			Traceback (most recent call last):
			  File "/home/phistep/Projects/chess/wuki/gui.py", line 101, in OnClick
				self.MakeAIMove()
			  File "/home/phistep/Projects/chess/wuki/gui.py", line 149, in MakeAIMove
				piece, target = self.ai.get_move(self.game.boards[-1])
			  File "/home/phistep/Projects/chess/wuki/ai.py", line 35, in get_move
				score = self.evaluate_board(resulting_board)
			  File "/home/phistep/Projects/chess/wuki/ai.py", line 54, in evaluate_board
				results = {f.__name__: f(board, possible_moves) for f in evaluators}
			  File "/home/phistep/Projects/chess/wuki/ai.py", line 54, in <dictcomp>
				results = {f.__name__: f(board, possible_moves) for f in evaluators}
			  File "/home/phistep/Projects/chess/wuki/ai.py", line 65, in eval_captured
				score += weight * self.piece_value[piece.piece] * (-1 if color is self.color else 1)
			KeyError: <AbstractPiece King (K)>
	- multicore evaluation (niceness on unix)
		import multiprocessing as mp
		if not args.processes:
			args.processes = mp.cpu_count()
		with mp.Pool(args.processes) as worker:
			worker.map(run_job, jobs)
- package
	- better readme (rst, examples, todo into own file?)
	- sphinx docs -> ghpages
	- dependencies, installer
	- package docsting header (author, etc)
