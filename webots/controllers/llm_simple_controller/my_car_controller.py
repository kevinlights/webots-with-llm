from my_car import MyCar
from log import SimpleLog
from llm import SimpleLLM
import time
from utils import function_to_tool
from functools import partial


class MyCarController:
    def __init__(self):
        self.log = SimpleLog()
        self.car = MyCar(log=self.log)
        self.llm = SimpleLLM(log=self.log)
        self.bound_funcs()

        self.thinking = False
        self.log.info(self.get_tool_schemas())

    def on_task_completed(self):
        self.thinking = False

    def bound_funcs(self):
        self.turn_left = partial(self.car.turn_left)
        self.turn_right = partial(self.car.turn_right)
        self.move_forward = partial(self.car.move_forward)
        self.move_back = partial(self.car.move_back)

    def get_tool_schemas(self):
        return [
            function_to_tool(self.car.turn_left),
            function_to_tool(self.car.turn_right),
            function_to_tool(self.car.move_forward),
            function_to_tool(self.car.move_back),
        ]

    def get_tools(self):
        return {
            "turn_left": self.turn_left,
            "turn_right": self.turn_right,
            "move_forward": self.move_forward,
            "move_back": self.move_back,
        }

    def run(self):
        while self.car.robot.step(self.car.timestep) != -1:
            try:
                obstacles = self.car.ps_values_to_text()
                self.log.info(obstacles)

                if not self.thinking:
                    self.thinking = True
                    self.llm.plan(
                        obstacles,
                        tool_schemas=self.get_tool_schemas(),
                        tool_dict=self.get_tools(),
                        model="qwen2.5:3b",
                    )
                    self.on_task_completed()
            except Exception as e:
                self.log.error(f"failed to run main loop: {e}")
                self.thinking = False

            time.sleep(1)
