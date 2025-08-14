# tests/test_all.py
import os
import sys
import logging
import unittest
import importlib
import inspect
import zipfile
import traceback
from pathlib import Path
from contextlib import contextmanager
from unittest import mock

# ------------------------------------------------------------------------------
# ЛОГИ
# ------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "tests" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "test_report.txt"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Убедимся, что корень проекта в PYTHONPATH
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ------------------------------------------------------------------------------
# ХЕЛПЕРЫ
# ------------------------------------------------------------------------------
def safe_import(module_path: str):
    try:
        return importlib.import_module(module_path)
    except Exception as e:
        logging.exception(f"Import failed: {module_path} -> {e}")
        return None

def find_class(module, candidates):
    if not module:
        return None
    for name in candidates:
        if hasattr(module, name):
            return getattr(module, name)
    return None

@contextmanager
def cwd(path: Path):
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)

def project_path(*parts) -> Path:
    return ROOT.joinpath(*parts)


# ------------------------------------------------------------------------------
# КОНСТАНТЫ
# ------------------------------------------------------------------------------
MODEL_DIR = project_path("model")
ZIP_CANDIDATES = [
    MODEL_DIR / "qwen-model.zip",
    MODEL_DIR / "model.zip",
]
FALLBACK_PT = MODEL_DIR / "model.pt"
FALLBACK_GGUF = MODEL_DIR / "model.gguf"


# ------------------------------------------------------------------------------
# ТЕСТЫ
# ------------------------------------------------------------------------------
class TestEnvironment(unittest.TestCase):
    def test_logs_directory_and_file(self):
        logging.info("Smoke: writing to log")
        self.assertTrue(LOG_DIR.exists(), "logs dir must exist")
        self.assertTrue(LOG_FILE.exists(), "log file should be created by logging.basicConfig")


class TestImports(unittest.TestCase):
    def test_core_modules_import(self):
        modules = [
            "core.ai",
            "core.orchestrator",
            "core.assets",
            "core.associative_memory",
            "core.cleaner",
            "core.config",
            "core.errors",
            "core.global_memory",
            "core.interaction",
            "core.logger",
            "core.memory",
            "core.payment",
            "core.prompt",
            "core.reporter",
            "core.router",
            "core.session",
            "core.stt",
            "core.tts",
            "core.vision",
            # Модельные утилиты (если есть)
            "model.zip_utils",
            "model.lazy_zip_file",
        ]
        for m in modules:
            with self.subTest(module=m):
                mod = safe_import(m)
                self.assertIsNotNone(mod, f"Cannot import {m}")


class TestModelZipIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zip_path = None
        for cand in ZIP_CANDIDATES:
            if cand.exists():
                cls.zip_path = cand
                break

    def setUp(self):
        if not self.zip_path:
            self.skipTest("ZIP with model weights not found in model/ (model.zip or qwen-model.zip)")

    def test_zip_exists_and_lists_entries(self):
        self.assertTrue(self.zip_path.exists(), f"ZIP not found: {self.zip_path}")
        with zipfile.ZipFile(self.zip_path, "r") as zf:
            names = zf.namelist()
            logging.info(f"ZIP entries: {names[:5]}{'...' if len(names) > 5 else ''}")
            self.assertGreater(len(names), 0, "ZIP must contain at least one file")

    def test_find_entry_and_stream_or_cache(self):
        zu = safe_import("model.zip_utils")
        self.assertIsNotNone(zu, "model.zip_utils import failed")

        SUPPORTED_TORCH = getattr(zu, "SUPPORTED_TORCH", (".pt", ".pth", ".bin"))
        SUPPORTED_GGUF = getattr(zu, "SUPPORTED_GGUF", (".gguf",))
        find_entry = getattr(zu, "find_entry", None)
        get_cached_file_from_zip = getattr(zu, "get_cached_file_from_zip", None)
        open_torch_stream = getattr(zu, "open_torch_stream", None)

        self.assertIsNotNone(find_entry, "zip_utils.find_entry is required")
        self.assertIsNotNone(get_cached_file_from_zip, "zip_utils.get_cached_file_from_zip is required")
        self.assertIsNotNone(open_torch_stream, "zip_utils.open_torch_stream is required")

        entry = find_entry(str(self.zip_path), SUPPORTED_TORCH + SUPPORTED_GGUF)
        self.assertIsNotNone(entry, "No supported weights found inside ZIP")
        logging.info(f"Found entry in ZIP: {entry}")

        with zipfile.ZipFile(self.zip_path, "r") as zf:
            info = zf.getinfo(entry)
            compress_type = "STORED" if info.compress_type == zipfile.ZIP_STORED else "COMPRESSED"
            logging.info(f"Entry compress type: {compress_type} | size: {info.file_size}")

        # Если это torch-вес — проверяем ленивое чтение 4KB без распаковки
        if entry.lower().endswith(tuple(ext.lower() for ext in SUPPORTED_TORCH)):
            if info.compress_type != zipfile.ZIP_STORED:
                self.skipTest("Torch entry is compressed — lazy stream requires ZIP_STORED")
            with open_torch_stream(str(self.zip_path), entry) as f:
                data = f.read(4096)
                self.assertGreater(len(data), 0, "Should read some bytes from lazy stream")

        # Любой вес можно вытащить в кэш и сверить размер
        cached_path = get_cached_file_from_zip(str(self.zip_path), entry, cache_dir=str(MODEL_DIR / ".cache"))
        self.assertTrue(Path(cached_path).exists(), "Cached file must exist")

        with zipfile.ZipFile(self.zip_path, "r") as zf:
            on_zip = zf.getinfo(entry).file_size
        on_disk = Path(cached_path).stat().st_size
        self.assertEqual(on_disk, on_zip, "Cached file size must match size in ZIP")


class TestAIInit(unittest.TestCase):
    def setUp(self):
        self.ai_mod = safe_import("core.ai")
        self.assertIsNotNone(self.ai_mod, "core.ai import failed")

    def test_init_model_with_mocked_torch_load(self):
        init_model = getattr(self.ai_mod, "init_model", None)
        self.assertIsNotNone(init_model, "init_model not found in core.ai")

        # Подмена torch.load внутри core.ai, чтобы не грузить тяжёлые веса
        with mock.patch("core.ai.torch.load", return_value={"ok": True}):
            result = init_model()

        # Базовая проверка возвращаемого объекта
        self.assertTrue(hasattr(result, "type"), "init_model should return an object with .type")
        if getattr(result, "type", None) == "torch":
            self.assertTrue(hasattr(result, "obj"), "torch result should have .obj")
        elif getattr(result, "type", None) == "gguf":
            self.assertTrue(hasattr(result, "path") and isinstance(result.path, str), "gguf result should have .path")


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orch_mod = safe_import("core.orchestrator")
        if not self.orch_mod:
            self.skipTest("core.orchestrator not found")

    def test_orchestrator_smoke(self):
        Orchestrator = find_class(self.orch_mod, ["Orchestrator", "TestOrchestrator"])
        if not Orchestrator:
            self.skipTest("No Orchestrator class found")

        orch = Orchestrator()
        if hasattr(orch, "run_inference"):
            out = orch.run_inference("ping")
            self.assertIsNotNone(out, "run_inference must return something")
        else:
            self.assertIsInstance(orch, Orchestrator)


class TestInterfacesPresence(unittest.TestCase):
    """
    Дотошная проверка наличия ключевых классов/методов, но без фатальных падений,
    если конкретный метод называется по-другому — пишем в лог и даём совет в отчёте.
    """
    CASES = [
        ("core.stt",     ["STT"],              ["transcribe", "from_file"]),
        ("core.tts",     ["TTS"],              ["synthesize", "speak"]),
        ("core.payment", ["PaymentSystem"],    ["charge", "process", "refund"]),
        ("core.memory",  ["AssociativeMemory"],["get", "set", "clear", "search"]),
        ("core.global_memory", ["GlobalMemory"],["load", "save", "update"]),
        ("core.vision",  ["Vision"],           ["analyze", "detect", "classify"]),
        ("core.interaction", ["InteractionManager"], ["handle", "route", "process"]),
        ("core.logger",  ["Logger"],           ["info", "warn", "error", "debug", "log"]),
        ("core.config",  ["ConfigLoader"],     ["load", "get", "validate"]),
        ("core.assets",  ["AssetManager"],     ["get", "resolve", "exists"]),
        ("core.session", ["SessionManager"],   ["start", "end", "get_session"]),
        ("core.router",  ["SpeechRouter", "TextRouter", "MemoryRouter"], ["route", "handle"]),
        ("core.errors",  ["ErrorHandler"],     ["handle", "wrap", "report"]),
    ]

    def test_interfaces_exist(self):
        for module_path, classes, methods in self.CASES:
            with self.subTest(module=module_path):
                mod = safe_import(module_path)
                self.assertIsNotNone(mod, f"Cannot import {module_path}")
                cls = find_class(mod, classes)
                if not cls:
                    logging.warning(f"{module_path}: none of classes {classes} found")
                    # Зафиксируем как мягкий провал интерфейса
                    self.fail(f"{module_path}: expected one of {classes}")
                # Пробуем создать без параметров (если получится)
                obj = None
                try:
                    sig = inspect.signature(cls)
                    if all(
                        p.default != inspect._empty or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
                        for p in list(sig.parameters.values())[1:]
                    ):
                        obj = cls()  # только если все параметры имеют дефолты
                except Exception:
                    obj = None

                # Проверим наличие хотя бы одного ожидаемого метода
                has_any = any(hasattr(cls, m) for m in methods) or (obj and any(hasattr(obj, m) for m in methods))
                if not has_any:
                    missing = ", ".join(methods)
                    self.fail(f"{module_path}.{cls.__name__}: none of expected methods found: {missing}")


class TestCodingHygiene(unittest.TestCase):
    def test_files_exist(self):
        required = [
            project_path("core", "ai.py"),
            project_path("core", "orchestrator.py"),
            project_path("core", "assets.py"),
            project_path("core", "memory.py"),
            project_path("core", "logger.py"),
        ]
        for p in required:
            with self.subTest(path=p):
                self.assertTrue(p.exists(), f"Missing file: {p}")

    def test_requirements_contains_torch(self):
        req = project_path("requirements.txt")
        if not req.exists():
            self.skipTest("requirements.txt not found")
        txt = req.read_text(encoding="utf-8", errors="ignore").lower()
        self.assertIn("torch", txt, "requirements.txt should contain 'torch' (pin version if needed)")


# ------------------------------------------------------------------------------
# УМНЫЙ РЕЗУЛЬТАТ И ОТЧЁТ
# ------------------------------------------------------------------------------
class SmartResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.details = []  # (kind, test, (exctype, value, tb))

    def addError(self, test, err):
        super().addError(test, err)
        self.details.append(("ERROR", test, err))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.details.append(("FAIL", test, err))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        # Не считаем skip ошибкой, но фиксируем для прозрачности
        self.details.append(("SKIP", test, (None, reason, None)))


def _suggest_fix(err_tuple, test):
    exctype, value, tb = err_tuple
    msg = str(value).lower() if value is not None else ""
    test_name = test.id()

    # Частые кейсы и советы
    if exctype is None:  # SKIP
        if "zip with model weights not found" in msg:
            return "Положи веса в папку model/ как model.zip или qwen-model.zip (содержимое: *.pt / *.gguf)."
        if "compressed — lazy stream requires zip_stored" in msg:
            return "Пересобери ZIP без сжатия для torch-весов (zip -0). Иначе используй кэш-распаковку."
        return "Скип оправдан. Проверь предусловия, чтобы включить тест."

    name = exctype.__name__

    if name in ("ImportError", "ModuleNotFoundError"):
        return "Проверь имя модуля, наличие __init__.py, корректный PYTHONPATH и пути импорта."
    if name == "AssertionError":
        if "missing file" in msg:
            return "Создай недостающий файл или поправь путь в коде/тесте."
        if "cannot import" in msg or "import failed" in msg or "import" in msg:
            return "Модуль найден с ошибкой. Проверь синтаксис и зависимости, прогоняй mypy/ruff."
        if "none of expected methods" in msg or "method" in msg and "not found" in msg:
            return "Реализуй отсутствующие методы или адаптируй тест под фактическое API."
        if "should contain 'torch'" in msg:
            return "Добавь torch в requirements.txt (с пином версии под твою платформу)."
        if "no supported weights found inside zip" in msg:
            return "Добавь внутри ZIP файл весов с поддерживаемым расширением (.pt/.pth/.bin/.gguf)."
        if "zip not found" in msg:
            return "Положи файл model.zip или qwen-model.zip в папку model/."
        return "Сверь ожидаемое и фактическое поведение, дополни тестовые предусловия."
    if name == "AttributeError":
        return "Добавь недостающий атрибут/метод в класс или проверь правильность имени."
    if name == "FileNotFoundError":
        return "Убедись, что файл существует и путь верный (рабочая директория — корень проекта)."
    if name == "TypeError":
        return "Проверь сигнатуры конструкторов/методов и значения по умолчанию."
    if name == "ValueError":
        return "Входные данные/конфиг в неверном формате — проверь валидацию и парсинг."
    return "Изучи трейсбек, воспроизведи локально по шагам, добавь логи вокруг проблемного места."


class SmartRunner(unittest.TextTestRunner):
    resultclass = SmartResult

    def run(self, test):
        result = super().run(test)

        # Итоговый диагностический отчёт в stdout
        total_problems = len(result.failures) + len(result.errors)
        print("\n" + "=" * 70)
        print("ДИАГНОСТИЧЕСКИЙ ОТЧЁТ ПО ТЕСТАМ")
        print("=" * 70)
        print(f"- Всего тестов: {result.testsRun}")
        print(f"- Ошибок: {len(result.errors)}")
        print(f"- Провалов: {len(result.failures)}")
        print(f"- Пропусков: {len(result.skipped)}")

        if result.details:
            print("\nПодробности и ориентиры по фиксам:")
            for kind, test, err in result.details:
                test_id = test.id()
                if kind == "SKIP":
                    reason = err[1]
                    print(f"* [{kind}] {test_id}")
                    print(f"  • Причина: {reason}")
                    print(f"  • Как починить: {_suggest_fix(err, test)}")
                    continue

                exctype, value, tb = err
                short = "".join(traceback.format_exception_only(exctype, value)).strip()
                # Укорачиваем трейс до первой полезной строки
                tb_preview = ""
                if tb:
                    tb_lines = traceback.format_tb(tb)
                    tb_preview = "".join(tb_lines[-3:]).strip()

                print(f"* [{kind}] {test_id}")
                print(f"  • Ошибка: {short}")
                if tb_preview:
                    print("  • Фрагмент трейсбека:")
                    for line in tb_preview.splitlines():
                        print(f"    {line}")
                print(f"  • Как починить: {_suggest_fix((exctype, value, tb), test)}")

        if total_problems == 0:
            print("\nВсе зелёные. Красота!")

        print("=" * 70 + "\n")
        return result


# ------------------------------------------------------------------------------
# LAUNCH
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project root: {ROOT}")
    print(f"Logs: {LOG_FILE}")
    unittest.main(verbosity=2, testRunner=SmartRunner)
