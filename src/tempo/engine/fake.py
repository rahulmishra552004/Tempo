import chess

from tempo.engine.errors import EngineError
from tempo.engine.models import Line


class FakeEngine:
    def __init__(self, lines_by_fen: dict[str, list[Line]]) -> None:
        self._lines = {chess.Board(fen).fen(): lines for fen, lines in lines_by_fen.items()}

    def analyse(self, board: chess.Board, n_lines: int = 3) -> list[Line]:
        try:
            return self._lines[board.fen()][:n_lines]
        except KeyError:
            raise EngineError(f"fake engine has no lines for {board.fen()}") from None

    def close(self) -> None:
        pass
