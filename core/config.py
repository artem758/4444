import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    def __init__(self, path: str = "config.json"):
        self.path = Path(path)
        self._cfg: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            self._cfg = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._cfg = {}
        return self._cfg

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._cfg.get(key, default)

    def validate(self) -> bool:
        # Минимальная валидация
        return isinstance(self._cfg, dict)
