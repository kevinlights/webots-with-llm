import threading
import queue
import time
from my_car import MyRobot


class SimpleTask:
    def __init__(self, log, robot: MyRobot, timestep: int):
        self.log = log
        self.robot = robot
        self.timestep = timestep
        self.task_queue = queue.Queue()
        self.lock = threading.Lock()
        self.processing = False

    def add_task(self, task, callback=None):
        with self.lock:
            self.task_queue.put((task, callback))
            self.log.info(f"added task: {task}")

    # def add_batch(self, tasks):
    #     with self.lock:
    #         for task in tasks:
    #             self.task_queue.put(task)
    #             self.log.info(f"added task: {task}")

    def process_tasks(self):
        self.processing = False  # 永远执行
        last_callback = None
        while self.robot.webot.step(self.timestep) != -1:
            try:
                with self.lock:
                    if not self.processing and not self.task_queue.empty():
                        self.processing = True
                        task, callback = self.task_queue.get_nowait()
                        last_callback = callback
                        self.log.info(f"executing task: {task}")
                        self.robot.handle_task(task)
                        self.processing = False
                        if callback:
                            callback()
                        if self.task_queue.empty():
                            self.log.info(f"all tasks processed")
                            self.robot.stop()
                            self.processing = False
            except queue.Empty:
                self.processing = False
                time.sleep(0.1)
                self.robot.stop()
                if last_callback:
                    last_callback()
            except Exception as e:
                self.processing = False
                self.log.error(f"error processing tasks: {e}")
                time.sleep(0.1)
                self.robot.stop()
                if last_callback:
                    last_callback()

    def stop_processing(self):
        self.processing = False
