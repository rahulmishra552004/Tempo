import shutil

import chess
import chess.engine

from tempo.engine.models import Line, Score

DEFAULT_PATH = "/usr/games/stockfish"


class StockfishEngine:
    def __init__(self, path: str | None = None, time_limit: float = 0.5) -> None:
        path = path or shutil.which("stockfish") or DEFAULT_PATH
        self._engine = chess.engine.SimpleEngine.popen_uci(path)
        self._limit = chess.engine.Limit(time=time_limit)

    def analyse(self, board: chess.Board, n_lines: int = 3) -> list[Line]:
        infos = self._engine.analyse(board, self._limit, multipv=n_lines)
        lines = []
        for info in infos:
            rel_score = info["score"].relative
            score = Score(mate=rel_score.mate(), cp=rel_score.score())
            moves = [move.uci() for move in info["pv"]]
            line = Line(score=score, moves=moves)
            lines.append(line)
        return lines

    def close(self) -> None:
        self._engine.quit()

    def __enter__(self) -> "StockfishEngine":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
