from datetime import datetime
import threading


class SimpleLog:
    def __init__(self):
        pass

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def cur_thread(self):
        return threading.current_thread().name

    def debug(self, msg):
        print(f"{self.now()} | DBG | {self.cur_thread()} | {msg}")

    def info(self, msg):
        print(f"{self.now()} | INF\t  | {self.cur_thread()} | {msg}")

    def error(self, msg):
        print(f"{self.now()} | ERR | {self.cur_thread()} | {msg}")
