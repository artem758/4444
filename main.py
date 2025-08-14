# tests/test_all.py
import traceback

from core.ai import AIEngine
from core.stt import STT
from core.tts import TTS
from core.payment import PaymentSystem
from core.associative_memory import AssociativeMemory
from core.global_memory import GlobalMemory
from core.vision import Vision

errors = []

def log_result(name, success, error=None):
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if error:
        print(f"   ↪ {error.splitlines()[-1]}")
        errors.append((name, error))

def test_ai():
    try:
        ai = AIEngine()
        response = ai.generate("Привет, кто ты?")
        assert isinstance(response, str) and len(response) > 0
        log_result("AIEngine.generate()", True)
    except Exception as e:
        log_result("AIEngine.generate()", False, traceback.format_exc())

def test_stt():
    try:
        stt = STT()
        text = stt.transcribe("samples/test.wav")
        assert isinstance(text, str)
        log_result("STT.transcribe()", True)
    except Exception as e:
        log_result("STT.transcribe()", False, traceback.format_exc())

def test_tts():
    try:
        tts = TTS()
        tts.speak("Тест озвучки")
        log_result("TTS.speak()", True)
    except Exception as e:
        log_result("TTS.speak()", False, traceback.format_exc())

def test_payment():
    try:
        pay = PaymentSystem()
        assert isinstance(pay.is_access_granted(), bool)
        result = pay.activate_family_pass("LVREX-2025-FAMILY")
        assert result is True
        assert pay.is_access_granted() is True
        log_result("PaymentSystem.activate_family_pass()", True)
    except Exception as e:
        log_result("PaymentSystem.activate_family_pass()", False, traceback.format_exc())

def test_memory():
    try:
        mem = AssociativeMemory()
        mem.remember("тест", "ответ")
        assert mem.recall("тест") == "ответ"
        log_result("AssociativeMemory.remember/recall()", True)
    except Exception as e:
        log_result("AssociativeMemory.remember/recall()", False, traceback.format_exc())

def test_global_memory():
    try:
        gm = GlobalMemory()
        contents = gm.list_contents()
        assert isinstance(contents, list)
        log_result("GlobalMemory.list_contents()", True)
    except Exception as e:
        log_result("GlobalMemory.list_contents()", False, traceback.format_exc())

def test_vision():
    try:
        vis = Vision()
        objects = vis.analyze("samples/test.jpg")
        assert isinstance(objects, list)
        log_result("Vision.analyze()", True)
    except Exception as e:
        log_result("Vision.analyze()", False, traceback.format_exc())

def test_interaction():
    try:
        ai = AIEngine()
        mem = AssociativeMemory()
        tts = TTS()
        prompt = "Как заменить ремень ГРМ?"
        response = ai.generate(prompt)
        mem.remember(prompt, response)
        tts.speak(response)
        assert mem.recall(prompt) == response
        log_result("Interaction: AI + Memory + TTS", True)
    except Exception as e:
        log_result("Interaction: AI + Memory + TTS", False, traceback.format_exc())

def final_report():
    print("\n📊 Финальный отчёт:")
    if not errors:
        print("✅ Все тесты прошли успешно. Ошибок нет.")
    else:
        print(f"❌ Обнаружено ошибок: {len(errors)}")
        for name, err in errors:
            print(f"   • {name}: {err.splitlines()[-1]}")

if __name__ == "__main__":
    print("🔍 Запуск глубинных тестов LV-REX...\n")
    test_ai()
    test_stt()
    test_tts()
    test_payment()
    test_memory()
    test_global_memory()
    test_vision()
    test_interaction()
    final_report()
