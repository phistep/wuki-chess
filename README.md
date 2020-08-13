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
	- AbstractPiece.possible_moves() -> legal_moves()
	- Board.possible_moves(player=self.current_player)
	- rules
		- movement can be blocked by other pieces along the way (Piece.possible_moves() not AbstractPiece.possible_moves())
		- en passent
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
		- game end
		- remis!
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
- visualization
	- matplotlib for pdf game output
	- wxpython gui
- package
	- sphinx docs
	- automated tests
	- dependencies, installer
	- package docsting header (author, etc)
