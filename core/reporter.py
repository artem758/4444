from typing import Any, Dict, List


class TestReporter:
    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def add(self, item: Dict[str, Any]) -> None:
        self.items.append(item)

    def export(self) -> List[Dict[str, Any]]:
        return list(self.items)
