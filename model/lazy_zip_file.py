import zipfile
from typing import IO


class LazyZipFileReader:
    """
    Простой обёрткой над ZipExtFile как "ленивый" стрим.
    """
    def __init__(self, zf: zipfile.ZipFile, entry: str):
        self._zf = zf
        self._entry = entry
        self._fh: IO[bytes] | None = None

    def __enter__(self):
        self._fh = self._zf.open(self._entry, "r")
        return self._fh

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fh:
                self._fh.close()
        finally:
            self._zf.close()
        return False
