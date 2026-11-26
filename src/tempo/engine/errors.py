"""The errors Tempo raises on purpose. Callers only need to catch TempoError."""


class TempoError(Exception):
    """Base class for every error Tempo raises on purpose."""


class InvalidPositionError(TempoError):
    """The FEN can't be read, or describes an impossible position."""


class IllegalMoveError(TempoError):
    """The move can't be read, is ambiguous, or isn't legal here."""


class GameOverError(TempoError):
    """The game is already over: checkmate, stalemate, insufficient material, 75-move rule."""


class EngineError(TempoError):
    """The engine crashed, timed out or returned output we can't use."""
