import threading
import queue
import time
from controller import Robot
from log import SimpleLog

class SimpleTask:
    def __init__(self, timestep: int = 32):
        self.task_queue = queue.Queue()
        self.processing = False
        self.lock = threading.Lock()
        self.log = SimpleLog()
        self.timestep = timestep

    def add_task(self, task, callback=None):
        with self.lock:
            self.task_queue.put((task, callback))
            self.log.info(f"added task: {task}")

    def add_batch(self, tasks, callback=None):
        with self.lock:
            for task in tasks:
                self.task_queue.put((task, None))
                self.log.info(f"added task: {task}")

    def process_tasks(self, robot):
        self.processing = True
        while self.processing and robot.step(self.timestep) != -1:
            try:
                with self.lock:
                    if not self.task_queue.empty():
                        task, callback = self.task_queue.get_nowait()
                        self.execute_task(task)
                        if callback:
                            callback()
                        if self.task_queue.empty():
                            self.log.info("all tasks in current batch completed")
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                self.log.error(f"error processing task: {e}")

    def execute_task(self, task):
        self.log.info(f"executing task: {task}")
        time.sleep(10)

    def stop_processing(self):
        self.processing = False
