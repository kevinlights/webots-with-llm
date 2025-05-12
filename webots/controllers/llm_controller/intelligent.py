from model import SimpleLLM
from bot import SimpleBot
import json
import time
from log import SimpleLog

class SimpleAi:
    def __init__(self, bot: SimpleBot):
        self.llm = SimpleLLM()
        self.robot = bot
        self.log = SimpleLog()

    def _handle_move(self, action: dict):
        assert "distance" in action
        if action["direction"] == "forward":
            return self.robot.move_forward(action["distance"])
        elif action["direction"] == "back":
            return self.robot.move_back(action["distance"])
        return 0

    def _handle_rotate(self, action: dict):
        assert "angle" in action
        if action["direction"] == "left":
            return self.robot.turn_left(action["angle"])
        elif action["direction"] == "right":
            return self.robot.turn_right(action["angle"])
        return 0

    def _handle_action_chain(self, actions: list[dict]):
        total_time = 0
        for i in range(len(actions)):
            action = actions[i]
            total_time += self._handle_action(action)
        return total_time
    
    def stop(self):
        self.robot.stop()

    def _handle_action(self, action: dict):
        self.log.info(f"handle action: {action}")
        assert "type" in action
        assert "direction" in action
        if action["type"] == "move":
            return self._handle_move(action)
        elif action["type"] == "rotate":
            return self._handle_rotate(action)
        else:
            self.log.error(f"invalid action type: {action['type']}")
        return 0

    def think(self, input: str) -> dict:
        self.log.info(f"thinking: {input}")
        start = time.time()
        resp = self.llm.chat(input)
        think_time = time.time() - start
        self.log.info(f"end, think time: {round(think_time, 2)}s")
        action = None
        try:
            action = json.loads(resp)
        except:
            self.log.error(f"invalid action response from LLM: {resp}")

        return action

    def drive(self, input: str) -> dict:
        self.log.info(f"thinking: {input}")
        start = time.time()
        resp = self.llm.drive(input)
        think_time = time.time() - start
        self.log.info(f"end, think time: {round(think_time, 2)}s")
        action = None
        try:
            action = json.loads(resp)
        except:
            self.log.error(f"invalid action response from LLM: {resp}")

        return action

    def think_chain(self, input: str) -> list:
        self.log.info(f"thinking: {input}")
        start = time.time()
        resp = self.llm.plan(input)
        think_time = time.time() - start
        self.log.info(f"end, think time: {round(think_time, 2)}s")
        self.log.info(f"plan result: {resp}")
        actions = []
        try:
            plans = json.loads(resp)
            assert len(plans) > 0
            for plan in plans:
                action = self.think(plan)
                if action:
                    actions.append(action)
        except:
            self.log.error(f"invalid action chain response from LLM: {resp}")

        return actions
