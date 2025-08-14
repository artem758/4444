from typing import Any


class _BaseRouter:
    def route(self, x: Any) -> str:
        return "ok"

    def handle(self, x: Any) -> Any:
        return {"ok": True, "data": x}


class SpeechRouter(_BaseRouter):
    pass


class TextRouter(_BaseRouter):
    pass


class MemoryRouter(_BaseRouter):
    pass
