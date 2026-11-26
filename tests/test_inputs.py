import chess
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tempo.engine.errors import GameOverError, IllegalMoveError, InvalidPositionError
from tempo.engine.inputs import normalize_fen, parse_fen, parse_move

START = chess.STARTING_FEN
CASTLE = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
NO_CASTLING = "4k3/8/8/8/8/8/8/4K2R w - - 0 1"
EN_PASSANT = "4k3/8/8/3Pp3/8/8/8/4K3 w - e6 0 1"
PROMOTION = "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"
PINNED_KNIGHT = "4k3/4r3/8/8/8/8/4N3/4K3 w - - 0 1"
TWO_KNIGHTS = "4k3/8/8/8/8/8/8/1N2KN2 w - - 0 1"
PAWN_OR_BISHOP = "4k3/8/8/B7/8/2n5/1P6/4K3 w - - 0 1"  # bxc3 and Bxc3 are both legal

# Figurines as escapes, so no editor or terminal can garble them
WHITE_KNIGHT = "♘"
FIGURINE = str.maketrans("KQRBN", "♔♕♖♗♘")


# ---------- parse_fen ----------


@pytest.mark.parametrize(
    ("fen", "error", "message"),
    [
        (
            "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
            GameOverError,
            "checkmate",
        ),
        ("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1", GameOverError, "stalemate"),
        ("4k3/8/8/8/8/8/8/2B1K3 w - - 0 1", GameOverError, "neither side can checkmate"),
        ("4k3/8/8/8/8/8/8/7R w - - 0 1", InvalidPositionError, "White has no king"),
        ("4k3/8/8/8/8/8/4R3/4K3 w - - 0 1", InvalidPositionError, "side not to move is in check"),
        ("hello", InvalidPositionError, "can't read this FEN"),
        ("", InvalidPositionError, "can't read this FEN"),
    ],
)
def test_bad_fen(fen, error, message):
    with pytest.raises(error, match=message):
        parse_fen(fen)


def test_valid_fen_has_no_warnings():
    pos = parse_fen(START)
    assert pos.board.fen() == START
    assert pos.warnings == ()


def test_extra_whitespace_is_cleaned():
    assert parse_fen(f"  {START.replace(' ', '   ')}\n").board.fen() == START


def test_impossible_castling_rights_repaired():
    pos = parse_fen("4k3/8/8/8/8/8/8/4K2R w KQkq - 0 1")
    assert pos.board.castling_xfen() == "K"
    assert pos.board.is_valid()
    assert pos.warnings == ("castling rights KQkq aren't possible here; using K",)


def test_impossible_en_passant_square_removed():
    pos = parse_fen("4k3/8/8/8/8/8/8/R3K3 w - e3 0 1")
    assert pos.board.ep_square is None
    assert pos.warnings == ("en passant square e3 isn't possible; removed it",)


def test_missing_fields_assumed_with_warnings():
    pos = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    assert pos.board.turn == chess.WHITE
    assert len(pos.warnings) == 2


def test_normalize_fen_drops_unusable_en_passant_square():
    # e3 is a valid square (White just played e2-e4) but no black pawn can take
    board = parse_fen("4k3/8/8/8/4P3/8/8/4K3 b - e3 0 1").board
    assert normalize_fen(board) == "4k3/8/8/8/4P3/8/8/4K3 b - - 0 1"


# ---------- parse_move: accepted ----------


@pytest.mark.parametrize(
    ("fen", "text", "uci"),
    [
        (START, "Nf3", "g1f3"),
        (START, "nf3", "g1f3"),
        (START, f"{WHITE_KNIGHT}f3", "g1f3"),
        (START, "Nf3!?", "g1f3"),
        (START, "Nf3+", "g1f3"),
        (START, "N-f3", "g1f3"),
        (START, "  e4  ", "e2e4"),
        (START, "e2e4", "e2e4"),
        (START, "E2E4", "e2e4"),
        (CASTLE, "O-O", "e1g1"),
        (CASTLE, "0-0", "e1g1"),
        (CASTLE, "o-o-o", "e1c1"),
        (CASTLE, "e1h1", "e1g1"),
        (EN_PASSANT, "dxe6 e.p.", "d5e6"),
        (PROMOTION, "a8Q", "a7a8q"),
        (PROMOTION, "a8=Q+", "a7a8q"),
        (PROMOTION, "a7a8q", "a7a8q"),
        (TWO_KNIGHTS, "Nbd2", "b1d2"),
        (TWO_KNIGHTS, "nfd2", "f1d2"),
        (PAWN_OR_BISHOP, "bxc3", "b2c3"),  # lowercase b is the pawn, never the bishop
        (PAWN_OR_BISHOP, "Bxc3", "a5c3"),
    ],
)
def test_move_accepted(fen, text, uci):
    assert parse_move(chess.Board(fen), text) == chess.Move.from_uci(uci)


# ---------- parse_move: rejected with a reason ----------


@pytest.mark.parametrize(
    ("fen", "text", "message"),
    [
        (START, "", "empty move"),
        (START, "hello", "can't read the move"),
        (START, "--", "null move"),
        (START, "Nf5", "no knight of yours can go to f5"),
        (START, "e3e4", "there's no piece on e3"),
        (START, "e7e5", "the piece on e7 isn't yours"),
        (START, "g1g3", "the knight on g1 can't go there"),
        (PINNED_KNIGHT, "Nc3", "leaves your king in check"),
        (PINNED_KNIGHT, "e2c3", "leaves your king in check"),
        (TWO_KNIGHTS, "Nd2", "write Nbd2 or Nfd2$"),  # no Kd2 offered
        (PROMOTION, "a7a8", "add the promotion piece: a7a8q"),
        (PROMOTION, "a8", "add the promotion piece: a8=Q"),
        (NO_CASTLING, "O-O", "can't castle"),
        (NO_CASTLING, "e1g1", "can't castle"),
    ],
)
def test_move_rejected(fen, text, message):
    with pytest.raises(IllegalMoveError, match=message):
        parse_move(chess.Board(fen), text)


# ---------- round trip ----------


@st.composite
def positions(draw, max_plies=80):
    board = chess.Board()
    for _ in range(draw(st.integers(0, max_plies))):
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(draw(st.sampled_from(moves)))
    return chess.Board(board.fen())  # drop the history, like FEN input


@settings(deadline=None)
@given(positions())
def test_round_trip(board):
    for move in board.legal_moves:
        san = board.san(move)
        for text in (san, move.uci(), f"{san}!?", san.translate(FIGURINE), f"{move.uci()}+"):
            assert parse_move(board, text) == move, text
