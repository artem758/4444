from typing import Any, Dict


class InteractionManager:
    def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "payload": payload}

    def route(self, text: str) -> str:
        return "text" if text and isinstance(text, str) else "unknown"

    def process(self, text: str) -> str:
        return text.strip() if isinstance(text, str) else ""
