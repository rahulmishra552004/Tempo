"""Check user input once, at the edge: FEN text and move text."""

import re
from typing import NamedTuple

import chess

from tempo.engine.errors import GameOverError, IllegalMoveError, InvalidPositionError

REPAIRABLE = chess.STATUS_BAD_CASTLING_RIGHTS | chess.STATUS_INVALID_EP_SQUARE

REJECT = {
    chess.STATUS_EMPTY: "the board is empty",
    chess.STATUS_NO_WHITE_KING: "White has no king",
    chess.STATUS_NO_BLACK_KING: "Black has no king",
    chess.STATUS_TOO_MANY_KINGS: "too many kings",
    chess.STATUS_TOO_MANY_WHITE_PAWNS: "White has more than 8 pawns",
    chess.STATUS_TOO_MANY_BLACK_PAWNS: "Black has more than 8 pawns",
    chess.STATUS_PAWNS_ON_BACKRANK: "a pawn is on the first or last rank",
    chess.STATUS_TOO_MANY_WHITE_PIECES: "White has more than 16 pieces",
    chess.STATUS_TOO_MANY_BLACK_PIECES: "Black has more than 16 pieces",
    chess.STATUS_OPPOSITE_CHECK: "the side not to move is in check",
    chess.STATUS_TOO_MANY_CHECKERS: "the king is checked by too many pieces",
    chess.STATUS_IMPOSSIBLE_CHECK: "this check can't happen in a real game",
}

GAME_OVER = {
    chess.Termination.CHECKMATE: "checkmate",
    chess.Termination.STALEMATE: "stalemate",
    chess.Termination.INSUFFICIENT_MATERIAL: "neither side can checkmate",
    chess.Termination.SEVENTYFIVE_MOVES: "75 moves without a capture or pawn move",
}

# Written as escapes so a terminal or editor can't garble them: ♔♕♖♗♘♚♛♜♝♞
FIGURINES = str.maketrans(
    "♔♕♖♗♘♚♛♜♝♞",
    "KQRBNKQRBN",
)
UCI_RE = re.compile(r"[a-h][1-8][a-h][1-8][qrbn]?")
# piece, from file, from rank, target square, promotion piece
SAN_RE = re.compile(r"([NBRQK])?([a-h])?([1-8])?[x-]?([a-h][1-8])(?:=?([QRBNqrbn]))?")
SUFFIXES = "!?+#"


class ParsedPosition(NamedTuple):
    board: chess.Board
    warnings: tuple[str, ...]


# ---------- FEN ----------


def parse_fen(text: str) -> ParsedPosition:
    """Read a FEN: reject impossible or finished positions, repair harmless fields."""
    fen = " ".join(text.split())
    try:
        board = chess.Board(fen)
    except ValueError as e:
        raise InvalidPositionError(f"can't read this FEN: {e}") from e

    fields = fen.split(" ")
    warnings = _missing_field_warnings(fields)
    warnings += _check_and_repair(board, fields)
    _refuse_game_over(board)
    return ParsedPosition(board=board, warnings=tuple(warnings))


def normalize_fen(board: chess.Board) -> str:
    """The cache key: castling cleaned, en passant square only when the capture is legal."""
    return board.fen()


def _missing_field_warnings(fields: list[str]) -> list[str]:
    warnings = []
    if len(fields) < 2:
        warnings.append("side to move missing; assumed White")
    if len(fields) < 3:
        warnings.append("castling rights missing; assumed none")
    return warnings


def _check_and_repair(board: chess.Board, fields: list[str]) -> list[str]:
    """Raise if the position is impossible; fix harmless fields and say what changed."""
    status = board.status()
    problems = [REJECT.get(flag, flag.name) for flag in status & ~REPAIRABLE]
    if problems:
        raise InvalidPositionError("; ".join(problems))

    warnings = []
    if status & chess.STATUS_BAD_CASTLING_RIGHTS:
        board.castling_rights = board.clean_castling_rights()
        warnings.append(
            f"castling rights {fields[2]} aren't possible here; "
            f"using {board.castling_xfen() or '-'}"
        )
    if status & chess.STATUS_INVALID_EP_SQUARE:
        warnings.append(f"en passant square {fields[3]} isn't possible; removed it")
        board.ep_square = None
    return warnings


def _refuse_game_over(board: chess.Board) -> None:
    outcome = board.outcome()
    if outcome is not None:
        reason = GAME_OVER.get(outcome.termination, outcome.termination.name.lower())
        raise GameOverError(f"the game is over: {reason}")


# ---------- Moves ----------


def parse_move(board: chess.Board, text: str) -> chess.Move:
    """Parse a move in SAN or UCI, forgiving common ways of writing it."""
    move_text = _clean(text)
    if UCI_RE.fullmatch(move_text.lower()):
        move = _parse_uci(board, move_text.lower())
    else:
        move = _parse_san(board, move_text)
    if not move:  # python-chess reads "--" and "Z0" as a null move
        raise IllegalMoveError("a null move isn't a move")
    return move


def _clean(text: str) -> str:
    move_text = text.strip().translate(FIGURINES).rstrip(SUFFIXES)
    move_text = re.sub(r"\s*e\.p\.?$", "", move_text).rstrip(SUFFIXES)
    move_text = re.sub(r"^[oO0]-[oO0]-[oO0]", "O-O-O", move_text)  # long castling first
    move_text = re.sub(r"^[oO0]-[oO0]", "O-O", move_text)
    if not move_text:
        raise IllegalMoveError("empty move")
    return move_text


def _parse_uci(board: chess.Board, uci: str) -> chess.Move:
    move = chess.Move.from_uci(uci)
    piece = board.piece_at(move.from_square)
    from_name = chess.square_name(move.from_square)
    if piece is None:
        raise IllegalMoveError(f"there's no piece on {from_name}")
    if piece.color != board.turn:
        raise IllegalMoveError(f"the piece on {from_name} isn't yours")
    if (
        piece.piece_type == chess.PAWN
        and chess.square_rank(move.to_square) in (0, 7)
        and move.promotion is None
    ):
        raise IllegalMoveError(f"add the promotion piece: {uci}q")
    try:
        return board.parse_uci(uci)
    except chess.IllegalMoveError as e:
        if (
            piece.piece_type == chess.KING
            and chess.square_distance(move.from_square, move.to_square) > 1
        ):
            raise IllegalMoveError("you can't castle that way now") from e
        if board.is_pseudo_legal(move):
            raise IllegalMoveError("that leaves your king in check") from e
        raise IllegalMoveError(
            f"the {chess.piece_name(piece.piece_type)} on {from_name} can't go there"
        ) from e


def _parse_san(board: chess.Board, san: str) -> chess.Move:
    try:
        return board.parse_san(san)
    except chess.InvalidMoveError as e:
        if san[0] in "nrqk":  # never "b": bxc3 is a pawn capture
            return _parse_san(board, san[0].upper() + san[1:])
        raise IllegalMoveError(f"can't read the move {san!r}") from e
    except chess.AmbiguousMoveError as e:
        options = sorted(
            board.san(m).rstrip(SUFFIXES) for m in _san_candidates(board, san, board.legal_moves)
        )
        raise IllegalMoveError(
            f"more than one piece can go there: write {' or '.join(options)}"
        ) from e
    except chess.IllegalMoveError as e:
        raise IllegalMoveError(_illegal_san_reason(board, san)) from e


def _illegal_san_reason(board: chess.Board, san: str) -> str:
    if san.startswith("O-O"):
        return "you can't castle that way now"
    match = SAN_RE.fullmatch(san)
    if match is None:
        return f"{san} isn't a legal move here"
    piece_letter, _, _, target, promotion = match.groups()
    piece_type = chess.PIECE_SYMBOLS.index(piece_letter.lower()) if piece_letter else chess.PAWN
    if not _san_candidates(board, san, board.pseudo_legal_moves):
        return f"no {chess.piece_name(piece_type)} of yours can go to {target}"
    if piece_type == chess.PAWN and target[1] in "18" and promotion is None:
        return f"add the promotion piece: {san}=Q"
    return "that leaves your king in check"


def _san_candidates(board: chess.Board, san: str, moves) -> list[chess.Move]:
    """Moves from `moves` that fit the piece, origin hints and target written in `san`."""
    match = SAN_RE.fullmatch(san)
    if match is None:
        return []
    piece_letter, from_file, from_rank, target, _ = match.groups()
    piece_type = chess.PIECE_SYMBOLS.index(piece_letter.lower()) if piece_letter else chess.PAWN
    return [
        m
        for m in moves
        if m.to_square == chess.parse_square(target)
        and board.piece_type_at(m.from_square) == piece_type
        and (from_file is None or chess.square_file(m.from_square) == "abcdefgh".index(from_file))
        and (from_rank is None or chess.square_rank(m.from_square) == int(from_rank) - 1)
    ]
