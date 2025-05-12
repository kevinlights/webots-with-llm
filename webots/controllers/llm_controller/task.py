import threading
import queue
import time
from intelligent import SimpleAi
from log import SimpleLog

class SimpleTask:
    def __init__(self, ai: SimpleAi, timestep: int = 32):
        self.task_queue = queue.Queue()
        self.processing = False
        self.lock = threading.Lock()
        self.log = SimpleLog()
        self.timestep = timestep
        self.ai = ai

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
        self.processing = False # 永远执行
        while robot.step(self.timestep) != -1:
            try:
                with self.lock:
                    if not self.processing and not self.task_queue.empty():
                        self.processing = True # 开始处理
                        task, callback = self.task_queue.get_nowait()
                        self.execute_task(task)
                        if callback:
                            callback()
                        if self.task_queue.empty():
                            self.log.info("all tasks in current batch completed")
                            self.ai.stop()
                            self.processing = False
            except queue.Empty:
                time.sleep(0.1)
                self.ai.stop()
                self.processing = False
            except Exception as e:
                self.log.error(f"error processing task: {e}")

    def execute_task(self, task):
        self.log.info(f"executing task: {task}")
        # time.sleep(10)
        self.ai._handle_action(task)
        self.processing = False # 结束处理

    def stop_processing(self):
        self.processing = False
