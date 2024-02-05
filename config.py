import logging
import sys

from chess import BISHOP, KING, KNIGHT, PAWN, QUEEN, ROOK, PieceType
from pydantic_settings import BaseSettings
from pythonjsonlogger import jsonlogger


class Logger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.logformat = "[%(asctime)s] %(levelname)s %(name)s : %(message)s"
        self.logHandler = logging.StreamHandler(sys.stdout)
        self.formatter = jsonlogger.JsonFormatter(self.logformat)
        self.logHandler.setFormatter(self.formatter)
        self.handlers.clear()
        self.addHandler(self.logHandler)


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
chess_logger = Logger("WoodFish")
