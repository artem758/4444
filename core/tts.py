class TTS:
    def synthesize(self, text: str) -> bytes:
        return f"AUDIO:{text}".encode("utf-8")

    def speak(self, text: str) -> bool:
        _ = self.synthesize(text)
        return True
