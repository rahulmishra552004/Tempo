import chess
import pytest

from tempo.engine.errors import EngineError
from tempo.engine.fake import FakeEngine
from tempo.engine.models import Line, Score

LINES = [
    Line(score=Score(cp=35), moves=["e2e4", "e7e5"]),
    Line(score=Score(cp=20), moves=["d2d4"]),
]


def test_returns_lines_for_known_fen():
    engine = FakeEngine({chess.STARTING_FEN: LINES})
    assert engine.analyse(chess.Board()) == LINES


def test_n_lines_limits_result():
    engine = FakeEngine({chess.STARTING_FEN: LINES})
    assert engine.analyse(chess.Board(), n_lines=1) == LINES[:1]


def test_fen_keys_are_normalized():
    # Impossible castling rights: the board's own FEN drops them to "K"
    engine = FakeEngine({"4k3/8/8/8/8/8/8/4K2R w KQkq - 0 1": LINES})
    assert engine.analyse(chess.Board("4k3/8/8/8/8/8/8/4K2R w K - 0 1")) == LINES


def test_unknown_fen_raises():
    engine = FakeEngine({})
    with pytest.raises(EngineError, match="no lines"):
        engine.analyse(chess.Board())
