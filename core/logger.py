from typing import Any


class Logger:
    def __init__(self):
        self.last = ""

    def log(self, level: str, msg: str, *args: Any) -> None:
        self.last = f"[{level.upper()}] {msg}"

    def info(self, msg: str) -> None:
        self.log("info", msg)

    def warn(self, msg: str) -> None:
        self.log("warn", msg)

    def error(self, msg: str) -> None:
        self.log("error", msg)

    def debug(self, msg: str) -> None:
        self.log("debug", msg)
