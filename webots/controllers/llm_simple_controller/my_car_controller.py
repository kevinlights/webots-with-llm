from my_car import MyCar
from log import SimpleLog
from llm import SimpleLLM
import time
from utils import function_to_tool
from functools import partial
from task import SimpleTask
import threading


class MyCarController:
    def __init__(self):
        self.log = SimpleLog()
        self.car = MyCar(log=self.log)
        self.llm = SimpleLLM(log=self.log)
        self.task = SimpleTask(log=self.log, robot=self.car, timestep=self.car.timestep)

        self.processing = False
        threading.current_thread().name = "main"
        self.init_task()

    def init_task(self):
        self.task_thread = threading.Thread(
            name="task",
            target=self.task.process_tasks,
            args=[],
        )
        self.task_thread.daemon = True
        self.task_thread.start()

    def on_task_completed(self):
        self.processing = False
        self.log.debug("task completed")

    def run(self):
        while self.car.robot.step(self.car.timestep) != -1:
            try:
                obstacles = self.car.ps_values_to_text()
                self.log.info(obstacles)

                if not self.processing:
                    self.processing = True
                    task = self.llm.plan(
                        obstacles,
                        tool_schemas=self.car.get_tool_schemas(),
                        model="qwen2.5:3b",
                    )
                    self.task.add_task(task, self.on_task_completed)
            except Exception as e:
                self.log.error(f"failed to run main loop: {e}")
                self.processing = False

            time.sleep(1)
        self.task.stop_processing()
        self.task_thread.join()
