from chess import C3, C4, C5, C6, D3, D4, D5, D6, E3, E4, E5, E6, F3, F4, F5, F6, Square

squares_center_occupation_value_dict: dict[Square, float] = {}

for k in range(0, 64):
    if k in [
        D4,
        D5,
        E4,
        E5,
    ]:
        squares_center_occupation_value_dict[k] = 1.5
    elif k in [
        C3,
        C4,
        C5,
        C6,
        D3,
        E6,
        F3,
        F4,
        F5,
        F6,
        D6,
        E3,
    ]:
        squares_center_occupation_value_dict[k] = 1
    else:
        squares_center_occupation_value_dict[k] = 0.75
