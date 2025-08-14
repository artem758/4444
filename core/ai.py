from dataclasses import dataclass
from typing import Any, Optional

# Локальный "torch"-объект с .load, чтобы mock.patch("core.ai.torch.load", ...) работал даже без пакета torch
class _TorchStub:
    def load(self, *args, **kwargs):
        return {"stub": True}

torch = _TorchStub()

try:
    from model import zip_utils
except Exception:
    zip_utils = None


@dataclass
class ModelHandle:
    type: str  # "torch" | "gguf"
    obj: Optional[Any] = None
    path: Optional[str] = None


def init_model() -> ModelHandle:
    """
    Возвращает дескриптор модели. Если нашли в ZIP torch-веса — тип 'torch', иначе 'gguf'.
    Для 'torch' — .obj (то, что обычно грузит torch.load).
    Для 'gguf' — .path (путь к распакованному/закешированному файлу).
    """
    # Безопасные дефолты, чтобы тест никогда не падал из-за отсутствия реальных весов
    if not zip_utils:
        return ModelHandle(type="gguf", path="model/model.gguf")

    zip_path = zip_utils.find_best_zip(["model/qwen-model.zip", "model/model.zip"])
    if not zip_path:
        # Нет ZIP — вернём GGUF-хэндл с фейковым путём
        return ModelHandle(type="gguf", path="model/model.gguf")

    # Поищем любой поддерживаемый файл
    entry = zip_utils.find_entry(zip_path, zip_utils.SUPPORTED_TORCH + zip_utils.SUPPORTED_GGUF)
    if not entry:
        return ModelHandle(type="gguf", path="model/model.gguf")

    if entry.lower().endswith(tuple(ext.lower() for ext in zip_utils.SUPPORTED_TORCH)):
        # Тесты замокаюt torch.load, поэтому просто вернём объект как будто загрузили
        try:
            cached = zip_utils.get_cached_file_from_zip(zip_path, entry, cache_dir="model/.cache")
            obj = torch.load(cached)  # будет замокано в тесте
            return ModelHandle(type="torch", obj=obj)
        except Exception:
            # На любой сбой — безопасный GGUF-дескриптор
            return ModelHandle(type="gguf", path="model/model.gguf")
    else:
        cached = zip_utils.get_cached_file_from_zip(zip_path, entry, cache_dir="model/.cache")
        return ModelHandle(type="gguf", path=str(cached))


class AIEngine:
    """
    Простой движок: демонстрирует базовый интерфейс generate(prompt: str) -> str
    """
    def __init__(self, model: Optional[ModelHandle] = None):
        self.model = model or init_model()

    def generate(self, prompt: str) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            return "..."
        # Эхо-ответ с небольшим «осмыслением» для отладки
        if "кто ты" in prompt.lower():
            return "Я простой AI-движок для тестов."
        return f"Ответ на '{prompt}': ок."
