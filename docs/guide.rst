Chess Terminology
=================
Before we get started, let's introduce some chess specific terminology that is
used throughout this documentation.
More information on chess terminology can be found at
`Wikipedia: Glossary of chess <https://en.wikipedia.org/wiki/Glossary_of_chess>`_.

.. glossary::
    Square
        A field on the board of chess. The board has 8×8=64 squares.

    File
        The column in which a square on the board lies. Labeled `a` through `h`.

    Rank
        The row in which a square on the board lies. Labeled `1` through `8`.

    Capture
        When a piece is taken off the board after an opponent piece moved onto
        its spot.


.. Installing
.. ==========


Executables
===========

.. automodule:: wuki.cli
    :noindex:

.. automodule:: wuki.gui
    :noindex:

Using the API
=============

The class hirarchy works as follows:

1. :class:`.game.Game` stores all the info of a game.
   It sets up an initial board and parses moves from a list passed at init to
   reach the current game state.
   From there you can use :meth:`.game.Game.make_move()` to further progress the game.

2. Internally a game holds an instance of :class:`.board.Board` for each board position
   encountered throught the game.
   You get the current board from :attr:`.game.Game.boards[-1]`.
   :meth:`.game.Game.make_move()` just checks if the color of the piece to be moved
   matches the current player and then forwards the call to
   :meth:`.board.Board.make_move()`.
3. A :class:`.board.Board` is made up of a set of :class:`.piece.Piece`\ s.
   These hold their type (:class:`.piece.AbstractPiece` subclasses), position on the board
   :class:`.board.Square` and color :class:`.board.Color`.
   :meth:`.board.Board.make_move()` checks the target square for pieces and handles the
   capturing, but forwards the movement to :meth:`.piece.Piece.move_to()`
4. :meth:`.piece.Piece.move_to()` checks if the move is possible by calling
   :meth:`.piece.Piece.possible_moves()`, which gives a list of all possible moves
   for that piece on that board. It checks the underlying
   :meth:`.piece.AbstractPiece.legal_move()` for all moves according to the piece types
   movement patterns and removes the onces that are blocked by other pieces on
   the board and other forbidden moves (like kings cannot move into check).
5. Another important method is :meth:`.board.Board.possible_moves()` which returns
   a list of all possible moves on the board for a certain player.
   It checks for check and only returns moves that end up not in check.

So your workflow might look something like

.. code-block:: python

    from wuki.game import Game
    from wuki.board import Board, Square
    from wiki.piece import White, Queen
    
    game = Game(['e4', 'e5', 'Nf3'])
    game.print_board()
    game.make_move('Nc6')
    game.print_board()

Instead of moving pieces until you reached your desired board constellation,
you can simply manipulate the internal data:

.. code-block:: python

    # is this cheating?
    game.boards[-1].add(Piece(Queen(), White, Square('d4')))
    game.print_board()

Boards are construced from a list of :class:`.Piece`\ s:

.. code-block:: python

    king = Pice(King(), White, Square('a1'))
    queen = Pice(Queen(), White, Square('b2'))
    board = Board([king, queen])
    board.print()

The AI is based on the following concept:
After initializing, an :class:`.ai.WukiAI` object can be queried for a move
:class:`.ai.WukiAI.get_move()` with a :class:`.board.Board`.
It takes that board position and generates all possible moves it can make and
their resulting board positions.
Then it evaluates each of these board positions on a number of criteria
(:search:`ai.WukiAI.eval_ <ai.WukiAI.eval\_*>` methods) and chooses the move with the highghest score.

Settung up a game against the AI works like this:

.. code-block:: python

    from wiki.board import Black
    from wuki.ai import WukiAI
    from wuki.game import Game
    
    ai = WukiAI(Black)
    game = Game([])
    
    # playing as white
    game.make_move('e4')
    game.print_board()
    
    ai_move = ai.get_move(game.boards[-1])
    game.make_move(\*ai_move)
    game.print_board()

