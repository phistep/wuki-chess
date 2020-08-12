# wuki
_a toy chess engine_

## TODO
- general
	- use exceptions to handle capturing, promotion, castling, check, checkmate?
	- should `AbstractPiece.possible_moves()` check for opponent pieces or one layer above?
	- rules
		- en passent
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
- parse game file
	- setup initial board
	- store all pieces and their positions (build index)
	- regex parse each move line
	- move each piece (check validity) (pawn promotion, castling, en passent)
	- store each board position separately
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
	- unicode for TUI
	- matplotlib for pdf game output
- package
	- sphinx docs
	- automated tests
	- actual python package structure + executables
		- helpers.py -> common.py
		- dependencies, installer
