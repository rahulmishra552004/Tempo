from typing import Protocol

import chess

from tempo.engine.models import Line


class Engine(Protocol):
    def analyse(self, board: chess.Board, n_lines: int = 3) -> list[Line]: ...

    def close(self) -> None: ...
