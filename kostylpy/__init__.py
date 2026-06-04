"""
kostylpy — Профессиональная библиотека костылей для Python.
Версия: 3.0.0-beta-kostyl-enterprise-edition
Статус: "Работает — не трогай, не дыши, не смотри"
Лицензия: WTFPL с дополнительными костылями

Просто импортируй этот модуль, и весь твой код станет
неубиваемым. Серьёзно. Мы патчим всё: print, open, import,
деление, индексы, атрибуты, даже сам интерпретатор
начинает работать через костыли.

ПРИНЦИПЫ:
    1. Если что-то работает — добавь костыль для надёжности.
    2. Если что-то не работает — добавь ещё костылей.
    3. Если костылей больше 1000 — ты на верном пути.
    4. Производительность? Нет, не слышали.
    5. Stack trace? Заменён на костыльный trace.
"""

__version__ = "3.0.0-beta-kostyl-enterprise-edition"
__author__ = "Коллектив костылестроителей им. В.Е.Лосипедова"
__email__ = "kostyl@crutch.enterprise"
__license__ = "WTFPL + Kostyl Clause"
__status__ = "Production Ready (на костылях)"

import sys
import os
import builtins
import functools
import importlib
import traceback
import signal
import atexit
import threading
import time
import random
import inspect
import warnings
import json
import hashlib
import base64
import io
import types
import typing
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto

# ═══════════════════════════════════════════════════════════════
# БЕЗОПАСНЫЙ ИМПОРТ МОДУЛЕЙ
# ═══════════════════════════════════════════════════════════════

def _safe_import_module(module_name: str):
    """Безопасно импортирует модуль, возвращает None при ошибке."""
    try:
        # Пробуем абсолютный импорт
        return __import__(f'kostylpy.{module_name}', fromlist=[module_name])
    except Exception:
        try:
            # Пробуем относительный импорт
            return __import__(f'.{module_name}', fromlist=[module_name], level=1)
        except Exception as e:
            print(f"⚠️ kostylpy: модуль '{module_name}' не загружен: {e}", file=sys.stderr)
            return None

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ КОСТЫЛИЗАЦИИ
# ═══════════════════════════════════════════════════════════════

KOSTYL_VERSION = __version__
KOSTYL_MODE_ACTIVE = True
KOSTYL_COFFEE_REQUIRED = True
KOSTYL_PANIC_THRESHOLD = 42  # После 42 костылей — паника
KOSTYL_MAX_RECURSION = 9001  # It's over 9000!

class KostylSeverity(Enum):
    """Уровни серьёзности костылей."""
    COSMETIC = "✨ КОСМЕТИЧЕСКИЙ"
    MINOR = "🟢 МАЛЫЙ"
    MODERATE = "🟡 УМЕРЕННЫЙ"
    MAJOR = "🟠 КРУПНЫЙ"
    CRITICAL = "🔴 КРИТИЧЕСКИЙ"
    NUCLEAR = "💀 ЯДЕРНЫЙ"
    APOCALYPTIC = "🔥 АПОКАЛИПТИЧЕСКИЙ"

class KostylCategory(Enum):
    """Категории костылей для логирования."""
    PRINT = "print"
    OPEN = "open"
    IMPORT = "import"
    DIVISION = "division"
    ATTRIBUTE = "attribute"
    INDEX = "index"
    CALL = "call"
    TYPE = "type"
    MEMORY = "memory"
    NETWORK = "network"
    DECORATOR = "decorator"
    CONTEXT = "context"
    FACTORY = "factory"
    VALIDATOR = "validator"
    INTERCEPTOR = "interceptor"
    ASYNC = "async"
    UTILS = "utils"
    MONKEY = "monkey"
    UNKNOWN = "unknown"

@dataclass
class KostylRecord:
    """Запись о применённом костыле."""
    id: int
    timestamp: float
    severity: KostylSeverity
    category: KostylCategory
    description: str
    file: str
    line: int
    traceback: str
    was_successful: bool
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'severity': self.severity.name,
            'category': self.category.value,
            'description': self.description,
            'file': self.file,
            'line': self.line,
            'traceback': self.traceback,
            'was_successful': self.was_successful
        }
    
    def __str__(self) -> str:
        emoji = self.severity.value.split()[0]
        return f"[{emoji}] #{self.id} {self.description}"

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНОЕ СОСТОЯНИЕ
# ═══════════════════════════════════════════════════════════════

class GlobalKostylState:
    """
    Глобальное состояние костылизации.
    Синглтон, потому что костыли должны быть едины.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.active: bool = True
        self.kostyl_counter: int = 0
        self.kostyl_log: List[KostylRecord] = []
        self.panic_mode: bool = False
        self.start_time: float = time.time()
        self.total_saved: int = 0  # Сколько раз спасли от падения
        self.total_failed: int = 0  # Сколько раз не смогли спасти
        self.coffee_breaks: int = 0
        self.original_functions: Dict[str, Callable] = {}
        self.patched_targets: List[str] = []
        self.statistics: Dict[str, int] = {}
        
        # Инициализируем статистику
        for cat in KostylCategory:
            self.statistics[cat.value] = 0
    
    def record_kostyl(
        self,
        severity: KostylSeverity,
        category: KostylCategory,
        description: str,
        was_successful: bool = True
    ) -> KostylRecord:
        """Записывает костыль в лог."""
        self.kostyl_counter += 1
        self.statistics[category.value] += 1
        
        if was_successful:
            self.total_saved += 1
        else:
            self.total_failed += 1
        
        # Получаем инфу о месте вызова
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back if frame.f_back else frame
        filename = caller_frame.f_code.co_filename if caller_frame else "unknown"
        lineno = caller_frame.f_lineno if caller_frame else 0
        tb = ''.join(traceback.format_stack(frame, limit=3))
        
        record = KostylRecord(
            id=self.kostyl_counter,
            timestamp=time.time(),
            severity=severity,
            category=category,
            description=description,
            file=filename,
            line=lineno,
            traceback=tb,
            was_successful=was_successful
        )
        
        self.kostyl_log.append(record)
        
        # Проверка на панику
        if self.kostyl_counter >= KOSTYL_PANIC_THRESHOLD and not self.panic_mode:
            self.panic_mode = True
            self._trigger_panic()
        
        return record
    
    def _trigger_panic(self):
        """Активирует режим паники."""
        msg = f"""
        ╔══════════════════════════════════════════╗
        ║  🚨 KOSTYLPY: РЕЖИМ ПАНИКИ АКТИВИРОВАН  ║
        ║  Превышен порог костылей: {KOSTYL_PANIC_THRESHOLD}            ║
        ║  Всего костылей: {self.kostyl_counter}                     ║
        ║  Спасено от падений: {self.total_saved}                   ║
        ║  Рекомендация: заварить кофе ☕        ║
        ╚══════════════════════════════════════════╝
        """
        warnings.warn(msg, UserWarning)
    
    def get_report(self) -> str:
        """Генерирует полный отчёт."""
        runtime = time.time() - self.start_time
        report = f"""
        ╔══════════════════════════════════════════════╗
        ║        🦿 KOSTYLPY ФИНАЛЬНЫЙ ОТЧЁТ          ║
        ╠══════════════════════════════════════════════╣
        ║  Версия: {KOSTYL_VERSION:<37}║
        ║  Время работы: {runtime:.2f} сек               ║
        ║  Всего костылей: {self.kostyl_counter:<27}║
        ║  Успешных: {self.total_saved:<32}║
        ║  Провальных: {self.total_failed:<30}║
        ║  Кофе-брейков: {self.coffee_breaks:<29}║
        ╠══════════════════════════════════════════════╣
        ║  Статистика по категориям:                  ║
        """
        for cat, count in self.statistics.items():
            if count > 0:
                report += f"        ║    {cat:<15}: {count:<20}║\n"
        
        report += """
        ╠══════════════════════════════════════════════╣
        ║  Статус: Работает на костылях™              ║
        ╚══════════════════════════════════════════════╝
        """
        return report
    
    def save_report(self, filepath: str = "kostyl_report.json"):
        """Сохраняет отчёт в JSON."""
        report_data = {
            'version': KOSTYL_VERSION,
            'runtime': time.time() - self.start_time,
            'total_kostyls': self.kostyl_counter,
            'total_saved': self.total_saved,
            'total_failed': self.total_failed,
            'statistics': self.statistics,
            'records': [r.to_dict() for r in self.kostyl_log]
        }
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"📊 Отчёт сохранён в {filepath}")
        except Exception as e:
            print(f"🩹 Не удалось сохранить отчёт: {e}")

# Глобальный экземпляр состояния
_kostyl_state = GlobalKostylState()

# ═══════════════════════════════════════════════════════════════
# СОХРАНЯЕМ ОРИГИНАЛЫ
# ═══════════════════════════════════════════════════════════════

_original_print = builtins.print
_original_open = builtins.open
_original_import = builtins.__import__
_original_getattr = builtins.getattr
_original_setattr = builtins.setattr
_original_input = builtins.input

_kostyl_state.original_functions = {
    'print': _original_print,
    'open': _original_open,
    'import': _original_import,
    'getattr': _original_getattr,
    'setattr': _original_setattr,
    'input': _original_input,
}

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНЫЙ PRINT
# ═══════════════════════════════════════════════════════════════

def _kostyl_print(*args, **kwargs):
    """
    Костыльный print.
    - Никогда не падает
    - Повторяет при ошибке
    - Логирует подозрительно короткие сообщения
    - Может выводить в несколько потоков (зачем-то)
    """
    # Проверка на подозрительно короткое сообщение
    if args and isinstance(args[0], str) and len(args[0]) < 10:
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.PRINT,
            f"Подозрительно короткое сообщение: '{args[0]}'"
        )
    
    # Проверка на наличие секретных данных
    if args and isinstance(args[0], str):
        suspicious = ['password', 'secret', 'token', 'key', 'пароль', 'секрет']
        for word in suspicious:
            if word.lower() in args[0].lower():
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.PRINT,
                    f"Обнаружен возможный вывод секретных данных (содержит '{word}')"
                )
    
    # Многократные попытки вывода
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Добавляем случайную задержку для "стабильности"
            if attempt > 0 and random.random() < 0.5:
                time.sleep(random.uniform(0.01, 0.1))
            
            return _original_print(*args, **kwargs)
            
        except Exception as e:
            if attempt == max_attempts - 1:
                _kostyl_state.record_kostyl(
                    KostylSeverity.CRITICAL,
                    KostylCategory.PRINT,
                    f"Не удалось вывести сообщение после {max_attempts} попыток: {e}",
                    was_successful=False
                )
                # Пробуем вывести хоть что-то
                try:
                    _original_print("🩹 KOSTYLPY: СООБЩЕНИЕ УТЕРЯНО")
                except:
                    pass
            else:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.PRINT,
                    f"Повторная попытка вывода ({attempt + 2}/{max_attempts})"
                )

builtins.print = _kostyl_print

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНЫЙ OPEN
# ═══════════════════════════════════════════════════════════════

class KostylFileWrapper:
    """Обёртка для файла с костылями."""
    
    def __init__(self, file_obj, original_path: str):
        self._file = file_obj
        self._path = original_path
        self._read_attempts = 0
        self._write_attempts = 0
    
    def read(self, *args, **kwargs):
        self._read_attempts += 1
        try:
            return self._file.read(*args, **kwargs)
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.OPEN,
                f"Ошибка чтения файла {self._path}: {e}"
            )
            return ""
    
    def write(self, *args, **kwargs):
        self._write_attempts += 1
        for attempt in range(3):
            try:
                return self._file.write(*args, **kwargs)
            except Exception as e:
                if attempt == 2:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MAJOR,
                        KostylCategory.OPEN,
                        f"Не удалось записать в файл {self._path}: {e}",
                        was_successful=False
                    )
                time.sleep(0.05)
        return 0
    
    def __getattr__(self, name):
        return getattr(self._file, name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        try:
            return self._file.__exit__(*args)
        except:
            pass

def _kostyl_open(file, mode='r', *args, **kwargs):
    """
    Костыльный open.
    - При отсутствии файла создаёт виртуальный
    - При ошибке чтения возвращает пустую строку
    - Логирует все подозрительные операции
    """
    filepath = str(file)
    
    # Проверка на подозрительные пути
    dangerous_paths = ['/etc/', '/proc/', '/sys/', 'C:\\Windows\\', '/root/']
    for dangerous in dangerous_paths:
        if dangerous in filepath:
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.OPEN,
                f"Попытка доступа к системному пути: {filepath}"
            )
    
    try:
        file_obj = _original_open(file, mode, *args, **kwargs)
        return KostylFileWrapper(file_obj, filepath)
        
    except FileNotFoundError:
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.OPEN,
            f"Файл не найден: {filepath}, создана виртуальная заглушка"
        )
        if 'r' in mode and '+' not in mode:
            return KostylFileWrapper(io.StringIO(""), filepath)
        else:
            return KostylFileWrapper(io.StringIO(), filepath)
    
    except PermissionError:
        _kostyl_state.record_kostyl(
            KostylSeverity.CRITICAL,
            KostylCategory.OPEN,
            f"Нет прав на доступ к файлу: {filepath}",
            was_successful=False
        )
        return KostylFileWrapper(io.StringIO(""), filepath)
    
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.NUCLEAR,
            KostylCategory.OPEN,
            f"Неизвестная ошибка открытия файла {filepath}: {e}",
            was_successful=False
        )
        return KostylFileWrapper(io.StringIO(""), filepath)

builtins.open = _kostyl_open

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНЫЙ IMPORT
# ═══════════════════════════════════════════════════════════════

_FALLBACK_MODULES = {
    'numpy': ('math', 'Математика на костылях'),
    'pandas': ('csv', 'Таблички на костылях'),
    'matplotlib': ('webbrowser', 'Графики в браузере'),
    'requests': ('urllib.request', 'HTTP на костылях'),
    'flask': ('http.server', 'Веб-сервер на костылях'),
    'django': ('http.server', 'Django на костылях (очень сильных)'),
    'sqlalchemy': ('sqlite3', 'SQL на костылях'),
    'redis': ('pickle', 'Кеш на костылях'),
    'celery': ('threading', 'Очереди на костылях'),
    'tensorflow': ('random', 'AI на random'),
    'torch': ('random', 'Нейросеть на random'),
    'sklearn': ('statistics', 'ML на костылях'),
}

def _kostyl_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Костыльный импорт.
    - Пробует несколько способов импорта
    - Ищет замену среди установленных модулей
    - Создаёт полноценную заглушку при неудаче
    """
    # Пропускаем внутренние импорты
    if name.startswith('_') or name in sys.builtin_module_names:
        return _original_import(name, globals, locals, fromlist, level)
    
    try:
        return _original_import(name, globals, locals, fromlist, level)
    
    except ImportError:
        # Ищем замену
        if name in _FALLBACK_MODULES:
            fallback_name, description = _FALLBACK_MODULES[name]
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.IMPORT,
                f"Модуль '{name}' не найден → {description}: '{fallback_name}'"
            )
            try:
                return _original_import(fallback_name, globals, locals, fromlist, level)
            except ImportError:
                pass
        
        # Создаём заглушку
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.IMPORT,
            f"Модуль '{name}' не найден → создана универсальная заглушка"
        )
        
        # Создаём полноценный модуль-заглушку
        stub_module = types.ModuleType(name)
        stub_module.__doc__ = f"Заглушка kostylpy для модуля {name}"
        stub_module.__version__ = "0.0.1-kostyl"
        stub_module.__kostyl_stub__ = True
        
        # Добавляем универсальный обработчик
        class StubClass:
            def __init__(self, *args, **kwargs):
                pass
            def __getattr__(self, item):
                return lambda *args, **kwargs: None
            def __call__(self, *args, **kwargs):
                return None
            def __str__(self):
                return f"<KostylStub:{name}>"
            def __repr__(self):
                return f"<KostylStub:{name}>"
            def __bool__(self):
                return False
            def __len__(self):
                return 0
            def __iter__(self):
                return iter([])
        
        stub_module.Stub = StubClass
        sys.modules[name] = stub_module
        
        return stub_module

builtins.__import__ = _kostyl_import

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНЫЙ EXCEPTHOOK
# ═══════════════════════════════════════════════════════════════

_original_excepthook = sys.excepthook

def _kostyl_excepthook(exc_type, exc_value, exc_tb):
    """
    Костыльный обработчик исключений.
    Вместо падения — логирует и продолжает работу.
    """
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    severity = KostylSeverity.NUCLEAR
    category = KostylCategory.UNKNOWN
    
    # Определяем категорию
    if exc_type == ZeroDivisionError:
        category = KostylCategory.DIVISION
        severity = KostylSeverity.MODERATE
    elif exc_type == AttributeError:
        category = KostylCategory.ATTRIBUTE
        severity = KostylSeverity.MINOR
    elif exc_type in (IndexError, KeyError):
        category = KostylCategory.INDEX
        severity = KostylSeverity.MINOR
    elif exc_type == TypeError:
        category = KostylCategory.TYPE
        severity = KostylSeverity.MODERATE
    
    _kostyl_state.record_kostyl(
        severity,
        category,
        f"Перехвачено исключение: {exc_type.__name__}: {exc_value}",
        was_successful=True
    )
    
    # Выводим костыльное сообщение вместо traceback
    _original_print(f"\n{'='*60}")
    _original_print(f"🩹 KOSTYLPY ПЕРЕХВАТИЛ ОШИБКУ!")
    _original_print(f"   Тип: {exc_type.__name__}")
    _original_print(f"   Сообщение: {exc_value}")
    _original_print(f"   Серьёзность: {severity.value}")
    _original_print(f"   Статус: Продолжаем работу (на костылях)")
    _original_print(f"{'='*60}\n")

sys.excepthook = _kostyl_excepthook

# ═══════════════════════════════════════════════════════════════
# ДОПОЛНИТЕЛЬНЫЕ КОСТЫЛИ
# ═══════════════════════════════════════════════════════════════

# Патчим input на случай ошибок ввода
def _kostyl_input(prompt=""):
    try:
        return _original_input(prompt)
    except (EOFError, KeyboardInterrupt):
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.UNKNOWN,
            "Ошибка ввода, возвращена пустая строка"
        )
        return ""

builtins.input = _kostyl_input

# Добавляем обработчик сигналов
def _kostyl_signal_handler(signum, frame):
    _kostyl_state.record_kostyl(
        KostylSeverity.APOCALYPTIC,
        KostylCategory.UNKNOWN,
        f"Получен сигнал {signum}, но мы держимся!"
    )
    _original_print(f"\n🩹 kostylpy: сигнал {signum} получен, но мы не падаем!")

signal.signal(signal.SIGINT, _kostyl_signal_handler)
signal.signal(signal.SIGTERM, _kostyl_signal_handler)

# Авто-отчёт при завершении
@atexit.register
def _kostyl_atexit():
    if _kostyl_state.kostyl_counter > 0:
        print(_kostyl_state.get_report())
        _kostyl_state.save_report()

# ═══════════════════════════════════════════════════════════════
# ПУБЛИЧНЫЙ API
# ═══════════════════════════════════════════════════════════════

# Импортируем из подмодулей
from .decorators import safe, retry, fallback, kostyl_method
from .context_managers import KostylContext, kostyl_block

# Экспортируем для удобства
__all__ = [
    # Декораторы
    'safe', 'retry', 'fallback', 'kostyl_method',
    # Контекстные менеджеры
    'KostylContext', 'kostyl_block',
    # Состояние
    'KostylRecord', 'KostylSeverity', 'KostylCategory',
    'GlobalKostylState',
    # Утилиты
    'report', 'get_state',
]

def report():
    """Публичная функция для получения отчёта."""
    print(_kostyl_state.get_report())

def get_state():
    """Возвращает глобальное состояние."""
    return _kostyl_state

# ═══════════════════════════════════════════════════════════════
# ФИНАЛЬНЫЙ АККОРД
# ═══════════════════════════════════════════════════════════════

_original_print(f"🦿 kostylpy v{KOSTYL_VERSION} загружен")
_original_print(f"   Защищено компонентов: 7 (print, open, import, input, excepthook, signal, atexit)")
_original_print(f"   Режим: {'АКТИВЕН' if KOSTYL_MODE_ACTIVE else 'ОТКЛЮЧЕН (зря)'}")
_original_print(f"   Порог паники: {KOSTYL_PANIC_THRESHOLD} костылей")
_original_print(f"   Кофе требуется: {'ДА ☕' if KOSTYL_COFFEE_REQUIRED else 'НЕТ (но лучше заварить)'}")
_original_print("   Статус: Готов к работе. Ваш код в надёжных костылях.\n")

# Всё. Теперь ваш код под защитой.
# Серьёзно, просто import kostylpy и забудьте о багах.