from chess import BISHOP, KING, KNIGHT, PAWN, QUEEN, ROOK, PieceType
from pydantic_settings import BaseSettings


class ChessSettings(BaseSettings):
    PIECES_VALUE: dict[PieceType, float] = {
        PAWN: 1,
        KNIGHT: 3.2,
        BISHOP: 3.3,
        ROOK: 5,
        QUEEN: 9,
        KING: 0,
    }


chess_settings = ChessSettings()
