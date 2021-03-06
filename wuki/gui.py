"""
GUI
---
Using the optional dependency `wxPython <https://wxpython.org>`_, |wuki| comes
with a minimal GUI that should work on all major operating systems (Linux,
macOS and Windows).
Run it from the commandline:

.. code-block:: bash

    PYTHONPATH=. bin/wuki-gui

It takes no arguments.

For now you can only play against the AI and you always play white.
Select a piece to move by clicking on it, then select a square to move to.
You will only be able to make legal moves.
When a piece is selected for movement, possible moves are highlighted in
yellow.
If you want to cancel the move and select another piece, just click on the
selected piece again to deselect it.
The last move the AI made is highlighted in blue.
"""
import wx
from .game import Game
from .board import BOARD_LEN, Square, Black, White
from . import ai

class GUI(wx.Frame):
    ColourFgWhite = wx.Colour(255,255,255)
    ColourFgBlack = wx.Colour(0,0,0)
    ColourBgWhite = wx.Colour(200,200,200)
    ColourBgBlack = wx.Colour(100,100,100)
    ColourBgHighlight = wx.Colour(200,200,0)
    ColourBgHist = wx.Colour(70,130,180)

    def __init__(self, parent=None):
        """Setup a Game, an AI and render the board."""
        super(GUI, self).__init__(parent, title="Wuki Chess", size=(512,512))
        self.ai = ai.WukiAI(Black)
        self.buttons = {}
        self.highlighted = []
        self.last_move_squares = []
        self.move_source = None
        self.game = Game([])
        self.SetupBoard()

    def SetupBoard(self):
        """Render buttons forming the current board position"""
        board = self.game.boards[-1]
        panel = wx.Panel(self)
        grid = wx.GridSizer(BOARD_LEN+2, BOARD_LEN+2, 0, 0)

        for file_ in " abcdefgh ":
            grid.Add(wx.StaticText(panel, label=file_), 0, wx.ALIGN_CENTER)

        for rank in reversed(range(BOARD_LEN)):
            grid.Add(wx.StaticText(panel, label=str(rank+1)), 0, wx.ALIGN_CENTER)
            for file_ in range(BOARD_LEN):
                position = Square(file_, rank)
                button = wx.ToggleButton(panel, label='')
                button.Bind(wx.EVT_TOGGLEBUTTON, self.OnClick)
                button.square = position
                font = button.GetFont()
                font.Scale(3)
                button.SetFont(font)
                square_color = self.ColourBgWhite if position.color() == White else self.ColourBgBlack
                button.SetBackgroundColour(square_color)
                button.SetToolTip(wx.ToolTip(str(position)))
                self.buttons[position] = button
                self.UpdateButton(position)
                grid.Add(button, 0, wx.EXPAND)
            grid.Add(wx.StaticText(panel, label=str(rank+1)), 0, wx.ALIGN_CENTER)

        for file_ in " abcdefgh ":
            grid.Add(wx.StaticText(panel, label=file_), 0, wx.ALIGN_CENTER)

        panel.SetSizer(grid)

    def UpdateButton(self, position):
        """Update a buttons label (piece) and colors based on its position
        
        :param Square position: the game square the button represents
        """
        board = self.game.boards[-1]
        button = self.buttons[position]
        button.SetValue(False)
        if position in board:
            piece = board[position]
            button.SetLabel(piece.piece.symbol[Black])
            piece_color = self.ColourFgWhite if piece.color == White else self.ColourFgBlack
            button.SetForegroundColour(piece_color)
            if piece.color != self.game.current_player:
                button.Disable()
        else:
            button.SetLabel('')
            button.Disable()

    def UpdateBoard(self):
        """Call UpdateButton on all self.buttons"""
        for button in self.buttons:
            self.UpdateButton(button)

    def ResetButtonBg(self, position):
        """Reset a buttons background color, i.e. remove any highlighting and
        set to the color of the square it represents

        :param Square position: the game square the button represents
        """
        square_color = self.ColourBgWhite if position.color() == White else self.ColourBgBlack
        self.buttons[position].SetBackgroundColour(square_color)

    def OnClick(self, event):
        """Event handler for board button press. Either selects or deselects
        a piece for moving or selects its target and performs the move.
        """
        button = event.GetEventObject()
        board = self.game.boards[-1]

        if button.GetValue():
            # button is pressed for the first time: source or target selection
            if self.move_source:
                # source piece already selected, this button is target, make move
                source = board[self.move_source]
                target = button.square
                self.MakeMove(source, target)
                self.move_source = None
                # TODO UI needs to update _before_ AI starts thinking
                self.MakeAIMove()
            else:
                # no source piece selected yet, this button is source
                self.move_source = button.square
                for possible_move in board[self.move_source].possible_moves(board):
                    self.highlighted.append(self.buttons[possible_move])
                for b in self.buttons.values():
                    b.Disable()
                button.Enable()
                self.Highlight()
        else:
            # pressed same button again, deselecting source piece
            self.move_source = None
            self.Highlight(False)
            self.EnablePlayer()

    def Highlight(self, highlight=True):
        """Highlight all squares that are in self.highlighted and
        self.last_move_squares.

        :param highlight: bool wether to enable or clear the highlighting
            (only affects self.highlighted)
        """
        for square in self.last_move_squares:
            self.buttons[square].SetBackgroundColour(self.ColourBgHist)
        for button in self.highlighted:
            if highlight:
                button.Enable()
                button.SetBackgroundColour(self.ColourBgHighlight)
            else:
                button.Disable()
                self.ResetButtonBg(button.square)
                self.highlighted = []

    def MakeMove(self, source, target):
        """Make a move and update the board state accordingly

        :param Piece source: the source Piece
        :param Square target: the target Square
        """
        self.game.make_move(source, target)
        self.Highlight(False)
        self.EnablePlayer()
        self.UpdateBoard()

    def MakeAIMove(self):
        """Let the AI make a move"""
        piece, target = self.ai.get_move(self.game.boards[-1])
        self.MakeMove(piece, target)
        for s in self.last_move_squares:
            self.ResetButtonBg(s)
        self.last_move_squares = [piece.position, target]
        self.Highlight()

    def EnablePlayer(self, player=None):
        """Enable all buttons for the current or provided player and disable
        all the opponent's ones

        :param player: the player for which to enable the buttons
        """
        if player is None:
            player = self.game.current_player
        board = self.game.boards[-1]
        for position, button in self.buttons.items():
            if position in board and board[position].color == player:
                button.Enable()
            else:
                button.Disable()

if __name__ == "__main__":
    app = wx.App()
    GUI().Show()
    app.MainLoop()
