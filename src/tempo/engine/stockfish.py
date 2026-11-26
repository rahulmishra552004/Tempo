import shutil

import chess
import chess.engine

from tempo.engine.errors import EngineError
from tempo.engine.models import Line, Score, score_key

DEFAULT_PATH = "/usr/games/stockfish"


class StockfishEngine:
    def __init__(self, path: str | None = None, nodes: int = 300_000) -> None:
        path = path or shutil.which("stockfish") or DEFAULT_PATH
        self._engine = chess.engine.SimpleEngine.popen_uci(path, timeout=10)
        self._limit = chess.engine.Limit(nodes=nodes)

    def analyse(self, board: chess.Board, n_lines: int = 3) -> list[Line]:
        infos = self._engine.analyse(board, self._limit, multipv=n_lines, game=object())
        lines = []
        for info in infos:
            if not info.get("pv") or "score" not in info:
                continue
            rel_score = info["score"].relative
            score = Score(mate=rel_score.mate(), cp=rel_score.score())
            moves = [move.uci() for move in info["pv"]]
            line = Line(score=score, moves=moves)
            lines.append(line)
        if not lines:
            raise EngineError("the engine returned no usable line")
        return sorted(lines, key=lambda line: score_key(line.score), reverse=True)

    def close(self) -> None:
        self._engine.quit()

    def __enter__(self) -> "StockfishEngine":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
