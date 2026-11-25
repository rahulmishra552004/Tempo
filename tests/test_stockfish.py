import shutil
from pathlib import Path

import chess
import pytest

from tempo.engine.stockfish import DEFAULT_PATH, StockfishEngine

has_stockfish = shutil.which("stockfish") is not None or Path(DEFAULT_PATH).exists()


@pytest.mark.skipif(not has_stockfish, reason="Stockfish not installed")
def test_finds_mate_in_one():
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    with StockfishEngine() as engine:
        lines = engine.analyse(board=board)
    assert len(lines) == 3
    assert lines[0].score.mate == 1
    assert lines[0].moves == ["h5f7"]
