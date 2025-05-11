from model import SimpleLLM
from bot import SimpleBot
import json
import time


class SimpleAi:
    def __init__(self, bot: SimpleBot):
        self.llm = SimpleLLM()
        self.robot = bot

    def _handle_move(self, action: dict, think_time: float = 0):
        assert "distance" in action
        if action["direction"] == "forward":
            self.robot.move_forward(action["distance"], think_time)
        if action["direction"] == "back":
            self.robot.move_back(action["distance"], think_time)

    def _handle_rotate(self, action: dict, think_time: float = 0):
        assert "angle" in action
        if action["direction"] == "left":
            self.robot.turn_left(action["angle"], think_time)
        if action["direction"] == "right":
            self.robot.turn_right(action["angle"], think_time)

    def _handle_action(self, action: dict, think_time: float = 0):
        print(f"handle action: {action}")
        assert "type" in action
        assert "direction" in action
        if action["type"] == "move":
            self._handle_move(action, think_time)
        elif action["type"] == "rotate":
            self._handle_rotate(action, think_time)
        else:
            print(f"invalid action type: {action['type']}")

    def think(self, input: str):
        print(f"thinking: {input}")
        start = time.time()
        resp = self.llm.chat(input)
        think_time = time.time() - start
        print(f"end, think time: {round(think_time, 2)}s")
        try:
            action = json.loads(resp)
        except:
            print(f"invalid action response from LLM: {resp}")

        self._handle_action(action, think_time)
