from typing import Tuple, List


def room_rectangle(origin: Tuple[float, float], width: float, height: float):
    x, y = origin
    return [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)]
