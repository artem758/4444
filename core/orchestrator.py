from typing import Any, Optional

try:
    from core.ai import AIEngine
except Exception:
    AIEngine = None


class Orchestrator:
    """
    Тонкая обёртка над AIEngine — демонстрация связки.
    """
    def __init__(self, engine: Optional[AIEngine] = None):
        self.engine = engine or (AIEngine() if AIEngine else None)

    def run_inference(self, text: str) -> Any:
        if self.engine is None:
            return {"ok": True, "echo": text}
        return self.engine.generate(text)


# Совместимость с импортами из старого теста
class TestOrchestrator(Orchestrator):
    pass
