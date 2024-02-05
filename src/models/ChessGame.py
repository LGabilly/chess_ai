import numpy as np
from chess import BLACK, PIECE_TYPES, WHITE, Board, Color, PieceType
from pydantic import BaseModel, ConfigDict

from config import chess_logger, chess_settings
from src.utils.board_position import squares_center_occupation_value_dict


class ChessGame(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    board: Board = Board()
    current_turn: Color = board.turn

    def _get_player_pieces(self, color: Color) -> dict[PieceType, int]:
        """All pieces number grouped by types

        Returns:
            dict[PieceType, int]:
            {
                PAWN: 8,
                KNIGHT: 2,
                BISHOP: 2,
                ROOK: 2,
                QUEEN: 1,
                KING: 1
            }
        """
        res = {}
        for piece_type in PIECE_TYPES:
            res[piece_type] = len(self.board.pieces(piece_type, color))

        return res

    def _score_player_materials_value(self, color: Color) -> float:
        """Total values of material

        Returns:
            float: sum of all pieces types values multi by pieces types count number
        """
        pieces = self._get_player_pieces(color=color)
        pieces_values = sum(
            [
                piece_number * chess_settings.PIECES_VALUE.get(piece_type, 0)
                for (piece_type, piece_number) in pieces.items()
            ]
        )

        return pieces_values

    def _score_player_threat(self, color: Color) -> float:
        """Total attacks on a player pieces

        Returns:
            float: Number of attacks on each pieces multiplied by piece value
        """
        res = 0.0
        for square, piece in self.board.piece_map().items():
            if piece.color == color:
                piece_value = chess_settings.PIECES_VALUE.get(piece.piece_type, 0)
                num_attackers = len(self.board.attackers(not color, square=square))
                res += piece_value * num_attackers

        return res

    def _score_player_center_occupation(self, color: Color) -> float:
        """Get the center occupation score

        Args:
            color (Color): color for which we compute the score
            (should be either self.board.turn or not self.board.turn)

        Returns:
            float: Pieces values multiplied by the square position multiplier
        """
        res = 0.0
        for square, piece in self.board.piece_map().items():
            if piece.color == color:
                piece_value = chess_settings.PIECES_VALUE.get(piece.piece_type, 0)
                square_value = squares_center_occupation_value_dict.get(square, 0)
                res += piece_value * square_value
        return res

    def score(
        self, color: Color, ponderation: list[float] = [-1, 1, 0.5, -0.5, 0.5]
    ) -> float:
        """Return position score for a player

        Args:
            color (Color): player color
            ponderation (list[float]):
            ponderation you wish to use on all score sub function

        Returns:
            float: The position evaluation for a position
        """

        enemy_material_score = self._score_player_materials_value(not color)
        player_material_score = self._score_player_materials_value(color)
        self._score_player_threat(color)
        self._score_player_threat(not color)
        self._score_player_center_occupation(color)

        score = (
            ponderation[0] * enemy_material_score
            + ponderation[1] * player_material_score
            # + ponderation[2] * player_offensive_threat
            # + ponderation[3] * player_defensive_vulnerability
            # + ponderation[4] * player_center_occupation
        )

        chess_logger.info(
            f"""
            enemy_material_score {ponderation[0]} * {enemy_material_score} = {ponderation[0] * enemy_material_score}
            enemy_material_score {ponderation[1]} * {player_material_score} = {ponderation[1] * player_material_score}
            """
        )

        if self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition():
            return 0

        if self.board.is_checkmate():
            return np.inf

        return score

    def _best_provided_moves(
        self, moves, color: Color, ponderation: list[float] = [-1, 1, 0.5, -0.5, 0.5]
    ):
        best_cand = moves[0]
        self.board.push(best_cand)
        best_score_cand = self.score(color, ponderation)
        self.board.pop()

        for move in moves:
            self.board.push(move)
            cand_score = self.score(color, ponderation)
            if cand_score > best_score_cand:
                best_cand = move
                best_score_cand = cand_score

            self.board.pop()

        return best_cand


if __name__ == "__main__":
    game = ChessGame()

    game.board.push_san("e4")
    game.board.push_san("d5")
    game.board.push_san("e4d5")
    game.board.push_san("d8d5")
    game.board.push_san("f1c4")

    chess_logger.info(f"{game._score_player_threat(WHITE)=}")
    chess_logger.info(f"{game._score_player_threat(BLACK)=}")

    chess_logger.info(f"{game._score_player_center_occupation(WHITE)=}")
    chess_logger.info(f"{game._score_player_center_occupation(BLACK)=}")

    chess_logger.info(f"{game._score_player_materials_value(WHITE)=}")
    chess_logger.info(f"{game._score_player_materials_value(BLACK)=}")

    chess_logger.info(f"{game.score(WHITE)=}")
    chess_logger.info(f"{game.score(BLACK)=}")

    all_legal_moves = list(game.board.legal_moves)
    chess_logger.info(f"{game._best_provided_moves(all_legal_moves, game.board.turn)=}")
