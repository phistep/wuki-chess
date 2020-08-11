from .. import helpers

def test_PlayerColor():
    white = helpers.PlayerColor(helpers.PlayerColor.WHITE)
    black = helpers.PlayerColor(helpers.PlayerColor.BLACK)
    assert white == helpers.White
    assert black == helpers.Black
    assert ~white == black
    assert ~black == white
    assert white != black
    assert str(white) == 'w'
    assert str(black) == 'b'
