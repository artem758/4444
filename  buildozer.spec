[app]
title = LV-REX
package.name = lvrex
package.domain = com.lvrex.app   # обратный домен (можно так)
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,txt,wav,bin,gguf,pt,pth,json
version = 1.0
version.code = 1
requirements = python3,kivy==2.3.0,llama-cpp-python==0.2.23,faster-whisper==1.0.2,pyttsx3==2.90,pyaudio==0.2.14,numpy==1.26.4,ultralytics==8.0.203,pdfplumber==0.11.4,cryptography==42.0.5,qrcode==7.4.2,torch
orientation = sensor
fullscreen = 0
# Поставь путь к иконке 512x512 PNG:
icon.filename = assets/icon.png
presplash.filename = assets/icon.png

# Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO

# Главный файл
entrypoint = main.py

# Если хочешь использовать микрофон:
# android.permissions = RECORD_AUDIO

[buildozer]
log_level = 2
warn_on_root = 1

[app.android]
# Минимальная версия Android
android.minapi = 21
# Целевая версия
android.api = 33
# Архитектуры: arm64-v8a и armeabi-v7a (по умолчанию обе)
# android.arch = armeabi-v7a, arm64-v8a
