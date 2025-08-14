# core/idiot_guard.py
"""
Идиот-guard: базовые защиты от глупых действий.
"""

from __future__ import annotations

import time
import zipfile
import shlex
import re
from pathlib import Path
from typing import Iterable, Callable, Any
from urllib.parse import urlsplit

# Ограничения
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_MAX_SECONDS = 2.0             # 2 seconds

# Блокируемые хосты (локальные диапазоны)
BLOCKED_HOST_PATTERNS = (
    r"^127\.0\.0\.1($|:)",
    r"^0\.0\.0\.0($|:)",
    r"^\[?[0-9a-fA-F:]+\]?(?::|$)",
    r"^[0:]+$",
    r"^192\.168\.",
    r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
    r"^10\.",
    r"^localhost(:|$)"
)


# --- Безопасный путь ---
def is_safe_path(root: str | Path, user_path: str | Path) -> bool:
    """Проверяет, что user_path лежит внутри root (без выхода через ..)."""
    root_path = Path(root).resolve()
    target = (root_path / user_path).resolve()
    try:
        target.relative_to(root_path)
        return True
    except ValueError:
        return False


# --- Ограничение размера и времени ---
def process_with_limits(
    data: bytes | str,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_seconds: float = DEFAULT_MAX_SECONDS,
    worker: Callable[[bytes | str], Any] | None = None
):
    """Проверяет размер входа и ограничивает время выполнения worker."""
    size = len(data.encode("utf-8")) if isinstance(data, str) else len(data)
    if size > max_bytes:
        raise ValueError(f"Input too large: {size} bytes > {max_bytes}")

    t0 = time.time()
    result = worker(data) if worker else data
    dt = time.time() - t0

    if dt > max_seconds:
        raise TimeoutError(f"Processing too slow: {dt:.3f}s > {max_seconds:.3f}s")
    return result


# --- Фильтр URL ---
def is_blocked_url(url: str) -> bool:
    """Блокирует небезопасные/локальные URL."""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return True

    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return True

    host = parts.netloc.lower()
    host = host.rsplit("@", 1)[-1]  # удаляем userinfo
    host = host.split("]", 1)[0] if host.startswith("[") else host.split(":", 1)[0]

    for pat in BLOCKED_HOST_PATTERNS:
        if re.match(pat, host):
            return True
    return False


# --- Санитизация команд ---
def sanitize_command(cmd: str | Iterable[str]) -> list[str]:
    """Разбирает команду и отклоняет опасные конструкции shell."""
    parts = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    if not parts:
        raise ValueError("Empty command")

    dangerous_tokens = {";", "&&", "||", "|", "`", "$(", ">", "<"}
    for p in parts:
        for d in dangerous_tokens:
            if d in p:
                raise ValueError(f"Dangerous token in arg: {d}")
    return parts


# --- Безопасный запуск команды ---
def safe_run(exec_fn: Callable[[list[str]], Any], cmd: str | Iterable[str]) -> tuple[int, str, str]:
    """Запускает команду через переданную функцию, возвращает (код, stdout, stderr)."""
    parts = sanitize_command(cmd)
    r = exec_fn(parts)

    code = getattr(r, "returncode", 0)
    out = getattr(r, "stdout", "")
    err = getattr(r, "stderr", "")

    if isinstance(out, bytes):
        out = out.decode("utf-8", errors="ignore")
    if isinstance(err, bytes):
        err = err.decode("utf-8", errors="ignore")

    return code, out or "", err or ""


# --- Безопасная распаковка ZIP ---
def safe_extract(zip_path: str | Path, dest_dir: str | Path, max_entry_bytes: int | None = None) -> bool:
    """Безопасно извлекает архив ZIP с защитой от zip-slip, symlink и абсолютных путей."""
    dest = Path(dest_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    def _is_symlink(zi: zipfile.ZipInfo) -> bool:
        return ((zi.external_attr >> 16) & 0o170000) == 0o120000

    with zipfile.ZipFile(zip_path, "r") as zf:
        for zi in zf.infolist():
            name = zi.filename
            if not name.strip():
                continue

            out_path = (dest / name).resolve()
            try:
                out_path.relative_to(dest)
            except ValueError:
                continue  # zip-slip или абсолютный путь

            if _is_symlink(zi):
                continue

            if zi.is_dir():
                out_path.mkdir(parents=True, exist_ok=True)
                continue

            if max_entry_bytes is not None and zi.file_size > max_entry_bytes:
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(zi, "r") as src, open(out_path, "wb") as dst:
                if max_entry_bytes is None:
                    for chunk in iter(lambda: src.read(65536), b""):
                        dst.write(chunk)
                else:
                    remaining = max_entry_bytes
                    while remaining > 0:
                        chunk = src.read(min(65536, remaining))
                        if not chunk:
                            break
                        dst.write(chunk)
                        remaining -= len(chunk)

    return True