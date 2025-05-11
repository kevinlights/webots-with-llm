from types import FunctionType


class SimpleBot:
    def __init__(
        self,
        mv_fwd: FunctionType,
        mv_back: FunctionType,
        turn_left: FunctionType,
        turn_right: FunctionType,
    ):
        self._mv_fwd = mv_fwd
        self._mv_back = mv_back
        self._turn_left = turn_left
        self._turn_right = turn_right

    def move_forward(self, distance: float):
        return self._mv_fwd(distance)

    def move_back(self, distance: float):
        return self._mv_back(distance)

    def turn_left(self, angle: float):
        return self._turn_left(angle)

    def turn_right(self, angle: float):
        return self._turn_right(angle)
