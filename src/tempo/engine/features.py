from typing import Literal

import chess
from pydantic import BaseModel, ConfigDict, Field

PIECE_VALUE = {
    "queen": 9,
    "rook": 5,
    "bishop": 3,
    "knight": 3,
    "pawn": 1,
}


class Pieces(BaseModel):
    model_config = ConfigDict(frozen=True)

    queen: int = Field(ge=0)
    rook: int = Field(ge=0)
    bishop: int = Field(ge=0)
    knight: int = Field(ge=0)
    pawn: int = Field(ge=0, le=8)


class LoosePiece(BaseModel):
    model_config = ConfigDict(frozen=True)

    piece: str
    square: str
    reason: Literal["hanging", "attacked by cheaper piece"]


class SideStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    color: chess.Color
    material: int
    pieces: Pieces
    loose: list[LoosePiece]


def side_status(board: chess.Board, color: chess.Color) -> SideStatus:
    return SideStatus(
        color=color,
        material=_get_material(board, color),
        pieces=_get_pieces(board, color),
        loose=_get_loose_pieces(board, color),
    )


def _get_material(board: chess.Board, color: chess.Color) -> int:
    material = 0
    for piece in chess.PIECE_TYPES:
        if piece == chess.KING:
            continue
        piece_name = chess.piece_name(piece)
        piece_count = len(board.pieces(piece, color))
        material += PIECE_VALUE[piece_name] * piece_count
    return material


def _get_pieces(board: chess.Board, color: chess.Color) -> dict:
    pieces = {}
    for piece in chess.PIECE_TYPES:
        if piece == chess.KING:
            continue
        piece_name = chess.piece_name(piece)
        piece_count = len(board.pieces(piece, color))
        pieces[piece_name] = piece_count
    return pieces


def _get_loose_pieces(board: chess.Board, color: chess.Color) -> list[LoosePiece]:
    loose = []
    piece_map = board.piece_map(mask=board.occupied_co[color])
    for square, piece in piece_map:
        if piece is chess.KING:
            continue
        check_loose = _is_loose_piece(board=board, color=color, piece=piece, square=square)
        if check_loose:
            loose.append(
                LoosePiece(
                    piece=chess.piece_name(piece),
                    square=chess.square_name(square),
                    reason=check_loose,
                )
            )
    return loose


def _is_loose_piece(
    board: chess.Board, color: chess.Color, piece: chess.Piece, square: chess.Square
) -> str | None:
    pass
