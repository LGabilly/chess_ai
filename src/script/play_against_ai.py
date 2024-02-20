from chess import BLACK, WHITE

from models.ChessGame import ChessGame

game = ChessGame()

color = input("White or Black")
if color.lower() not in {"white", "black"}:
    print("Bravo le veau")
    exit()

color_bool = WHITE if color.lower() == "white" else BLACK
while game.board.is_game_over:
    print(game.board.unicode())
    if game.current_turn == color_bool:
        san_string = input("Your san moves:")
        game.play_human_move(san_string)
    else:
        game.play_ai_move()

print(game.board.unicode())
