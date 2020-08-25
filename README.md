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

For information about other arguments, ask `bin/wuki --help`.

## Use the Library
For now you gotta read the source. The commandline application is in
`wuki/cli.py:CLI.main()`. The main game logic in `wuki/game.py`.


## TODO
- general
	- check game state function super slow, how to realisticly use it in Game.make_move()
		- move is_stalemate and is_checkmate into Game / just into check_state
		- dont check is_check and king.possible_moves twice
		- profiling https://docs.python.org/3/library/profile.html
	- in make_move shortcut the legality checks if you know the move comes from possible_moves (caching like in VAMP evaluation)
	- don't always run slow tests
	- Color.__negate__() -> __not__()
	- use exceptions to handle promotion, castling?
	- give reasons to IllegalMoveError(reason=""), eg check, wrong moving
	- check and checkmate gamefile parsing and writing
	- rules
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
			- cannot move when touched
			- cannot move through check!
		- draw
			- threefold repitition: same player has same board three times in a row
			- fifty-move rule: 50 moves without captire or pawn move
			- no path to checkmate (ooph)
		- en passent
	- different verbosity for ai and cli https://docs.python.org/3/howto/logging.html
- cli
	- support Portable game notation
		- read and write
		- comments
		- time
		- markers for check etc.
	- interactive mode
		- check into prompt, checkmate support
		- use https://docs.python.org/3/library/cmd.html
		- cmd_show: when arguments black/white show all possible movable pieces for player
		- add color block to prompt
		- two player or ai mode
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
	- select/load/save game file
	- show current player
	- select opponent: human/ai
	- show captured
	- pawn promotion
	- handle game end
- ai
	- go through all own pieces and generate list of all possible moves and board positions
		- remove moves that land on pieces that are on the board from the list returned by `Piece.possible_moves()`
		- add castling if possible (goes in `Board`
		- handle pawn promotion (goes in `Piece` and `Pawn`?
			`Piece.move_to()` calls `AbstractPece.move_to()`
			`AbstractPiece.move_to()` just pass in other piece types, raises `PawnPromotionException`
	- lookahead
	- evaluation function for each board position
		- implement each as own function, sum total score,
		- allow black/whitelist for strategies
		- allow to pass list of custom strategy functions
			- check
			- checkmate
			- capturing
			- pawn promotion
			- double pawns
			- attacks
			- cover
			- freedom of movement
			- control over center
- package
	- better readme (rst, examples, todo into own file?)
	- sphinx docs -> ghpages
	- dependencies, installer
	- package docsting header (author, etc)
