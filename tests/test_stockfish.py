import shutil
from pathlib import Path

import chess
import pytest

from tempo.engine.models import score_key
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


@pytest.mark.skipif(not has_stockfish, reason="Stockfish not installed")
def test_same_result_twice():
    board = chess.Board()
    with StockfishEngine() as engine:
        assert engine.analyse(board) == engine.analyse(board)


@pytest.mark.skipif(not has_stockfish, reason="Stockfish not installed")
def test_lines_sorted_best_first():
    board = chess.Board("r3k3/5ppp/5n2/1N6/8/8/5PPP/5RK1 w - - 0 1")
    with StockfishEngine() as engine:
        lines = engine.analyse(board)
    keys = [score_key(line.score) for line in lines]
    assert keys == sorted(keys, reverse=True)
    assert lines[0].moves[0] == "b5c7"
