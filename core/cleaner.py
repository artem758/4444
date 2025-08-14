from typing import Any, Dict


class TestCleaner:
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Нормализатор для тестов
        return {k: (v.strip() if isinstance(v, str) else v) for k, v in data.items()}
