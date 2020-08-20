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

	$ PYTHONPATH=. bin/wuki match.txt

For information about other arguments, ask `bin/wuki --help`.

## Use the Library
For now you gotta read the source. The commandline application is in
`wuki/__init_.py:main()`. The main game logic in `wuki/game.py`.


## TODO
- general
	- check game state function super slow, how to realisticly use it in Game.make_move()
		- move is_stalemate and is_checkmate into Game / just into check_state
		- dont check is_check and king.possible_moves twice
	- don't always run slow tests
	- Color.__negate__() -> __not__()
	- use exceptions to handle promotion, castling?
	- give reasons to IllegalMoveError(reason=""), eg check, wrong moving
	- check and checkmate gamefile parsing and writing
	- rules
		- draw!
			- one player has no possible moves but is not in check
			- both players have empty Game.possible_moves()
			- threefold repitition: same player has same board three times in a row
			- fifty-move rule: 50 moves without captire or pawn move
			- no path to checkmate (ooph)
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
			- cannot move when touched
			- cannot move through check!
		- en passent
- find next move
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
- cli
	- --quiet: only print a move if there is one (by --move or by AI)
	- cmd_show: when no arguments show all possible movable pieces for player
	- check into prompt, checkmate support
	- add color block to prompt
	- box drawing https://en.wikipedia.org/wiki/Box-drawing_character
	- parse match_file into own function (support full Algebraic Notation)
	- support Portable game notation
		- read and write
		- comments
		- time
		- markers for check etc.
	- interactive mode
		- two player or ai mode
		- timestamps and time constraint
		- restore input on `IllegalMoveError` or `MoveParseError`
		- trap ^C
	- matplotlib for pdf game output
	- localization?
	- wxpython gui
	- matplotlib gui?
	- online mode (host server, play against players/ais)
- package
	- sphinx docs -> ghpages
	- dependencies, installer
	- package docsting header (author, etc)
