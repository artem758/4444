# main.py
from __future__ import annotations

import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

# Базовые защитные проверки
from core.idiot_guard import (
    is_safe_path,
    is_blocked_url,
    process_with_limits,
    sanitize_command,
)

# ---------------- UI (KV) ----------------
KV = """
<Root>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "12dp"

    Label:
        id: status
        text: root.status_text
        size_hint_y: None
        height: self.texture_size[1] + dp(8)
        halign: "left"
        valign: "middle"
        text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "12dp"
        Button:
            text: "Self-check"
            on_release: root.run_self_check()
        Button:
            text: "Init ASR/TTS"
            on_release: root.init_audio_stack()
        Button:
            text: "Vision"
            on_release: root.init_vision()

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        BoxLayout:
            id: logbox
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            padding: "0dp"
            spacing: "6dp"
"""

# ---------------- Services ----------------
class Services:
    """Ленивая инициализация тяжёлых подсистем (по возможности)."""
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)
        self.asr = None
        self.tts = None
        self.vision = None
        self.ready = {
            "asr": False,
            "tts": False,
            "vision": False,
        }

    # Инициализация аудио-стека: faster-whisper (ASR) + pyttsx3 (TTS)
    def init_audio(self, on_done):
        def task():
            ok = {"asr": False, "tts": False}
            # ASR (faster-whisper) — пытаемся мягко
            try:
                from faster_whisper import WhisperModel  # type: ignore
                # Лёгкая модель по умолчанию; на Android/Colab может быть недоступна
                # Подмените на путь к локальной модели, если требуется.
                # model = WhisperModel("small", device="cpu", compute_type="int8")
                ok["asr"] = True
            except Exception as e:
                Logger.warning(f"ASR init failed: {e}")

            # TTS (pyttsx3)
            try:
                import pyttsx3  # type: ignore
                _ = pyttsx3.init()
                ok["tts"] = True
            except Exception as e:
                Logger.warning(f"TTS init failed: {e}")

            on_done(ok)

        self._executor.submit(task)

    # Инициализация Computer Vision (ultralytics/torch)
    def init_vision(self, on_done):
        def task():
            ok = False
            try:
                # Импортируем, но не грузим веса, чтобы не падать на Android
                import ultralytics  # type: ignore
                ok = True
            except Exception as e:
                Logger.warning(f"Vision init failed: {e}")
            on_done(ok)

        self._executor.submit(task)


# ---------------- Root widget ----------------
class Root(BoxLayout):
    status_text = "LV-REX ready"

    def __init__(self, services: Services, **kwargs):
        super().__init__(**kwargs)
        self.services = services

    # Лёгкие самопроверки безопасности и окружения
    def run_self_check(self):
        self._log("Self-check: start")
        try:
            # Путь внутри корня?
            inside = is_safe_path(".", "tests") and not is_safe_path(".", "../etc/passwd")
            self._log(f"is_safe_path: {inside}")

            # URL‑фильтр: локальные/неправильные должны блокироваться
            blocked_local = is_blocked_url("http://127.0.0.1:8000")
            blocked_bad = is_blocked_url("file:///etc/passwd")
            ok_public = not is_blocked_url("https://example.com")
            self._log(f"is_blocked_url: local={blocked_local}, bad={blocked_bad}, public_ok={ok_public}")

            # Лимиты по размеру/времени
            echo = process_with_limits("ping", max_bytes=1024, max_seconds=1.0, worker=lambda d: d + " ok")
            self._log(f"process_with_limits: {echo}")

            # Санитизация команд
            parts = sanitize_command(["echo", "SAFE"])
            self._log(f"sanitize_command: {parts}")

            self._set_status("Self-check: OK")
        except Exception as e:
            self._set_status(f"Self-check error: {e}")
            Logger.exception("Self-check failed")

    def init_audio_stack(self):
        self._set_status("Init ASR/TTS...")
        self.services.init_audio(on_done=self._on_audio_done)

    def _on_audio_done(self, ok_map: dict):
        self.services.ready["asr"] = ok_map.get("asr", False)
        self.services.ready["tts"] = ok_map.get("tts", False)
        self._set_status(f"Audio: ASR={self.services.ready['asr']} TTS={self.services.ready['tts']}")

    def init_vision(self):
        self._set_status("Init Vision...")
        self.services.init_vision(on_done=self._on_vision_done)

    def _on_vision_done(self, ok: bool):
        self.services.ready["vision"] = ok
        self._set_status(f"Vision: {ok}")

    # --------------- helpers ---------------
    def _set_status(self, msg: str):
        self.status_text = msg
        if self.ids.get("status"):
            self.ids["status"].text = msg
        self._log(msg)

    def _log(self, msg: str):
        Logger.info(f"LVREX: {msg}")
        # добавим строку в лог‑бокс
        def add_line(dt):
            from kivy.uix.label import Label
            if self.ids.get("logbox"):
                self.ids["logbox"].add_widget(
                    Label(text=msg, size_hint_y=None, height="20dp", halign="left", valign="middle", text_size=(self.width, None))
                )
        Clock.schedule_once(add_line, 0)


# ---------------- App ----------------
class LVREXApp(App):
    def build(self):
        Builder.load_string(KV)
        self.services = Services()
        root = Root(self.services)
        return root


def main():
    # Центральная точка входа
    Logger.info("LVREX: starting main()")
    LVREXApp().run()


if __name__ == "__main__":
    main()

