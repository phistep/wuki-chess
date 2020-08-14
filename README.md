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

	$ bin/wuki match.txt

For information about other arguments, ask `bin/wuki --help`.

## Use the Library
For now you gotta read the source. The commandline application is in
`wuki/__init_.py:main()`. The main game logic in `wuki/game.py`.


## TODO
- general
	- use exceptions to handle capturing, promotion, castling, check, checkmate?
	- `Board.possible_moves(player=self.current_player)`
	- rules
		- movement can be blocked by other pieces along the way (`Piece.possible_moves()` not `AbstractPiece.legal_moves()`)
			- Pawns can't capture forward
			- Kings can't move themsleves into check
			- Knights don't care
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
		- game end
		- remis!
		- en passent
	- check game state function
		try:
			game.check_state()?
		except Remis as e:
		except CheckMate, TimeOut as e:

		Exception GameOver
			.winner # <Black> or <White> or None
			.type # Remis or CheckMate or TimeOut
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
	- implement `--make-move`
	- move into `cli.py`
		- parse game into own function (support full Algebraic Notation)
			- read and write
			- comments
			- time
			- markers for check etc.
	- interactive mode
		- auto save to matchfile
		- commands
			- "help" for this help
			- just a move
			- "save <file_name>" to save to file
			- "show <piece>" to highlight possible moves
			- "exit", "quit" to leave
		- two player or ai mode
		- timestamps and time constraint
		- restore input on `IllegalMoveError` or `MoveParseError`
	- matplotlib for pdf game output
	- localization?
	- wxpython gui
	- matplotlib gui?
- package
	- sphinx docs
	- dependencies, installer
	- package docsting header (author, etc)
