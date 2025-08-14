import numpy as np
import wave
import os

def generate_dummy_wav(filename="samples/test.wav", mode="silence", duration=2.0):
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    if mode == "silence":
        audio = np.zeros_like(t)
    elif mode == "noise":
        audio = np.random.uniform(-1, 1, size=t.shape)
    elif mode == "tone":
        audio = np.sin(2 * np.pi * 440 * t)
    else:
        raise ValueError("Unknown mode")

    audio = (audio * 32767).astype(np.int16)

    os.makedirs("samples", exist_ok=True)
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ WAV-файл создан: {filename} ({mode})")

if __name__ == "__main__":
    generate_dummy_wav(mode="noise")
