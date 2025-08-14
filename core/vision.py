from typing import Any, Dict, List


class Vision:
    def analyze(self, image: bytes) -> Dict[str, Any]:
        return {"labels": ["object"], "confidence": [0.9]}

    def detect(self, image: bytes) -> List[Dict[str, Any]]:
        return [{"bbox": [0, 0, 10, 10], "label": "object", "score": 0.9}]

    def classify(self, image: bytes) -> Dict[str, float]:
        return {"object": 0.9}
