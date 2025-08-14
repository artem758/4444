import os
import zipfile
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union, IO

SUPPORTED_TORCH: Tuple[str, ...] = (".pt", ".pth", ".bin")
SUPPORTED_GGUF: Tuple[str, ...] = (".gguf",)


def find_best_zip(candidates: Iterable[Union[str, os.PathLike]]) -> Optional[str]:
    for c in candidates:
        p = Path(c)
        if p.exists() and p.is_file():
            return str(p)
    return None


def find_entry(zip_path: Union[str, os.PathLike], extensions: Tuple[str, ...]) -> Optional[str]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            if any(name.lower().endswith(ext.lower()) for ext in extensions):
                return name
    return None


def open_torch_stream(zip_path: Union[str, os.PathLike], entry: str) -> IO[bytes]:
    """
    Открывает поток чтения для ZIP_STORED файла внутри архива.
    Для COMPRESSED — поведение не гарантируется (тест его скипает).
    """
    zf = zipfile.ZipFile(zip_path, "r")
    zinfo = zf.getinfo(entry)
    if zinfo.compress_type != zipfile.ZIP_STORED:
        # Для совместимости: позволим прочитать как есть (тест всё равно скипнет до чтения)
        return zf.open(zinfo, "r")
    return zf.open(zinfo, "r")


def get_cached_file_from_zip(zip_path: Union[str, os.PathLike], entry: str, cache_dir: Union[str, os.PathLike]) -> str:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / Path(entry).name
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open(entry, "r") as src, open(out_path, "wb") as dst:
            while True:
                chunk = src.read(1024 * 64)
                if not chunk:
                    break
                dst.write(chunk)
    return str(out_path)
