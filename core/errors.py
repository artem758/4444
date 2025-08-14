from typing import Callable, Any


class ErrorHandler:
    def handle(self, exc: Exception) -> str:
        return f"{exc.__class__.__name__}: {exc}"

    def wrap(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return self.handle(e)
        return inner

    def report(self, message: str) -> bool:
        # Заглушка для интеграции с репортерами
        return True
