from datetime import datetime
import threading


class SimpleLog:
    def __init__(self):
        pass

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def cur_thread(self):
        return threading.currentThread.__name__

    def debug(self, msg):
        print(f"{self.now()} | debug | {self.cur_thread} | {msg}")

    def info(self, msg):
        print(f"{self.now()} | info | {self.cur_thread} | {msg}")

    def error(self, msg):
        print(f"{self.now()} | error | {self.cur_thread} | {msg}")
