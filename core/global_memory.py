import json
from pathlib import Path
from typing import Any, Dict


class GlobalMemory:
    def __init__(self, path: str = "global_memory.json"):
        self.path = Path(path)
        self.data: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def update(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()
