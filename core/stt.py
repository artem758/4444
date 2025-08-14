from typing import Optional


class STT:
    def transcribe(self, audio_bytes: bytes) -> str:
        return "<text>"

    def from_file(self, path: str, lang: Optional[str] = None) -> str:
        return "<text:from_file>"
