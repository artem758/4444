# model/lazy_zip_file.py
import io
import os
import struct
import zipfile

class ZipSegmentFile(io.RawIOBase):
    """
    Прямое чтение одиночного файла внутри ZIP без распаковки.
    Требование: entry должен быть ZIP_STORED (без сжатия).
    """
    def __init__(self, zip_path: str, entry_name: str):
        super().__init__()
        self._zip_path = zip_path
        self._entry = entry_name
        self._fh = open(zip_path, "rb")
        self._closed = False

        with zipfile.ZipFile(zip_path, "r") as zf:
            info = zf.getinfo(entry_name)
            if info.compress_type != zipfile.ZIP_STORED:
                raise NotImplementedError(
                    f"'{entry_name}' хранится в ZIP со сжатием (type={info.compress_type}). "
                    "Для стриминга нужен ZIP_STORED (без сжатия)."
                )
            self._size = info.file_size
            self._data_offset = self._compute_data_offset(info)

        self._pos = 0

    def _compute_data_offset(self, info: zipfile.ZipInfo) -> int:
        # Локальный заголовок: 30 байт + имя + extra
        self._fh.seek(info.header_offset)
        header = self._fh.read(30)
        sig, = struct.unpack("<I", header[0:4])
        if sig != 0x04034B50:
            raise ValueError("Неверная сигнатура локального заголовка ZIP")
        fname_len, extra_len = struct.unpack("<HH", header[26:30])
        return info.header_offset + 30 + fname_len + extra_len

    # --- IOBase интерфейс ---
    def readable(self): return True
    def seekable(self): return True
    def writable(self): return False

    def close(self):
        if not self._closed:
            try:
                self._fh.close()
            finally:
                self._closed = True
        super().close()

    @property
    def closed(self): return self._closed

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            new_pos = offset
        elif whence == os.SEEK_CUR:
            new_pos = self._pos + offset
        elif whence == os.SEEK_END:
            new_pos = self._size + offset
        else:
            raise ValueError("invalid whence")
        if new_pos < 0:
            raise ValueError("negative seek position")
        self._pos = min(new_pos, self._size)
        return self._pos

    def read(self, n: int = -1) -> bytes:
        if self._pos >= self._size:
            return b""
        if n is None or n < 0:
            n = self._size - self._pos
        n = min(n, self._size - self._pos)
        self._fh.seek(self._data_offset + self._pos)
        data = self._fh.read(n)
        self._pos += len(data)
        return data

    def readinto(self, b) -> int:
        data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
