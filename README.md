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
	- Color.__negate__() -> __not__()
	- use exceptions to handle capturing, promotion, castling, check, checkmate?
	- give reasons to IllegalMoveError(reason=""), eg check, wrong moving
	- Board.pieces(kind=None, color=None) filter for color
	- rules
		- check
			- check has to be terminated
				- move king out of check
				- move piece inbetween attacker and king
			- cannot move a piece that puts your own piece into check
			-> resulting move has to have not check
			- no: Board should not contain game logic only piece logic
				- in Board.make_move(piece_, target): self.check = piece_.color
				- @property Game.check(): self.boards[-1].check
			- yes: Game has the game logic
				- in Game.make_move(piece_, target): self.check = piece_.color
			- manipulate Game.possible_moves to only include king if self.check == current_player
		- game end
			- loose game when Game.possible_moves() is empty
		- remis!
			- both players have empty Game.possible_moves()
		- pawn promotion
		- castling (add `.touched` attribute to `Piece`, also simplifies pawn initial two square movement)
			- cannot move when touched
			- cannot move through check!
		- en passent
	- check game state function
		try:
			board.check_state(current_player)?
		except Check:
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
	- parse match_file into own function (support full Algebraic Notation)
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
	- online mode (host server, play against players/ais)
- package
	- sphinx docs
	- dependencies, installer
	- package docsting header (author, etc)
