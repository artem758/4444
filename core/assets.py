from pathlib import Path
from typing import Optional


class AssetManager:
    def __init__(self, base_dir: str = "assets"):
        self.base = Path(base_dir)

    def resolve(self, name: str) -> Path:
        return (self.base / name).resolve()

    def exists(self, name: str) -> bool:
        return self.resolve(name).exists()

    def get(self, name: str) -> Optional[Path]:
        p = self.resolve(name)
        return p if p.exists() else None
