import numpy as np
from chess import PIECE_TYPES, Board, Color, Move, PieceType
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
        player_offensive_threat = self._score_player_threat(color)
        player_defensive_vulnerability = self._score_player_threat(not color)
        player_center_occupation = self._score_player_center_occupation(color)

        score = (
            ponderation[0] * enemy_material_score
            + ponderation[1] * player_material_score
            + ponderation[2] * player_offensive_threat
            + ponderation[3] * player_defensive_vulnerability
            + ponderation[4] * player_center_occupation
        )

        chess_logger.info(
            f"enemy_material_score {ponderation[0]} * {enemy_material_score} = {ponderation[0] * enemy_material_score}"
        )
        chess_logger.info(
            f"player_material_score {ponderation[1]} * {player_material_score} = {ponderation[1] * player_material_score}"
        )

        if self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition():
            return 0

        if self.board.is_checkmate():
            return np.inf

        return score

    def _best_provided_moves(
        self,
        moves: list[Move],
        color: Color,
        ponderation: list[float] = [-1, 1, 0.5, -0.5, 0.5],
    ):
        """
        Find the best move from a list of provided moves.

        Args:
            moves (list): A list of moves to choose from.
            color (Color): The color of the player making the move.
            ponderation (list, optional): A list of ponderation values for scoring. Defaults to [-1, 1, 0.5, -0.5, 0.5].

        Returns:
            The best move from the provided list.
        """
        best_cand = moves[0]
        chess_logger.info(best_cand.uci())
        self.board.push(best_cand)
        best_score_cand = self.score(color, ponderation)
        self.board.pop()

        for move in moves[1:]:
            self.board.push(move)
            chess_logger.info(move.uci())
            cand_score = self.score(color, ponderation)
            if cand_score > best_score_cand:
                best_cand = move
                best_score_cand = cand_score

            self.board.pop()

        return best_cand

    def play_ai_move(self):
        """
        Play an AI move in the chess game.

        This method selects the best move for the AI player based on the current position of the chessboard.
        It evaluates all legal moves and chooses the move with the highest score.
        The score is calculated using the position evaluation function, which takes into account factors such as material value, threats, and center occupation.

        Returns:
            None

        Raises:
            None
        """
        all_legal_moves = list(self.board.legal_moves)
        best_move = self._best_provided_moves(all_legal_moves, self.current_turn)
        self.board.push(best_move)
        self.current_turn = not self.current_turn

    def play_human_move(self, san_string: str):
        """
        Play a move made by a human player in the chess game.

        This method takes a string representation of a move in Standard Algebraic Notation (SAN) and applies it to the chessboard.
        It first retrieves all legal moves for the current position and logs them using the chess logger.
        Then, it pushes the move to the chessboard using the push_san() method.
        Finally, it updates the current turn to the opposite color.

        Args:
            san_string (str): The move to be played in Standard Algebraic Notation (SAN).

        Returns:
            None

        Raises:
            None
        """
        all_legal_moves = list(self.board.legal_moves)
        chess_logger.info({move.uci() for move in all_legal_moves})
        self.board.push_san(san_string)
        self.current_turn = not self.current_turn


if __name__ == "__main__":
    game = ChessGame()

    game.board.push_san("e4")
    game.board.push_san("d5")
    game.board.push_san("e4d5")
    game.board.push_san("d8d5")
    game.board.push_san("f1c4")

    all_legal_moves = list(game.board.legal_moves)
    chess_logger.info(f"{game._best_provided_moves(all_legal_moves, game.board.turn)=}")
    game.play_human_move("g8f6")
    game.play_ai_move()
    print(game.board.unicode())
