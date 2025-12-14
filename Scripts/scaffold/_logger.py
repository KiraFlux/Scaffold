import sys
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar
from typing import final


@final
@dataclass
class Logger:
    """Logger"""

    name: str

    __intend_size: ClassVar = 4

    __intend: int = field(init=False, default=0)

    def log_info(self, message: str) -> None:
        """Write an Info-level log to stdout"""
        sys.stdout.write(self._format_log("info", message))

    def log_error(self, message: str) -> None:
        """Write an Error-level log to stderr"""
        sys.stderr.write(self._format_log("error", message))

    def push(self) -> None:
        """Push intend"""
        self.__intend += 1

    def pop(self) -> None:
        """Pop intend"""
        self.__intend -= 1
        assert self.__intend >= 0

    def _format_log(self, prefix: str, message: str) -> str:
        return f"[{self.name}:{prefix}]{(' ' * self.__intend_size) * self.__intend} {message}\n"
