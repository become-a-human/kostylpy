"""
Костыльное логирование kostylpy.
Потому что стандартный logging — это скучно и недостаточно костыльно.
Здесь логируются даже сами логи.

Содержит:
- KostylLogger — костыльный логгер
- LogLevel — уровни логирования (с костыльными)
- LogRotator — ротация логов
- KostylFormatter — форматтер с эмодзи
- KostylHandler — обработчики логов
- MemoryHandler — лог в памяти
- FileHandler — лог в файл
- NetworkHandler — лог по сети
- CoffeeHandler — лог для кофе-брейков
- LogAggregator — сборщик логов со всех костылей
- Глобальный экземпляр логгера
"""

import sys
import os
import time
import json
import threading
import traceback
import inspect
import socket
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime

# Импортируем константы
try:
    from .constants import (
        Emoji, Colors, DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT,
        MAX_LOG_SIZE, LOG_ROTATION_COUNT, LOG_TRUNCATE_LENGTH
    )
except ImportError:
    class Emoji:
        KOSTYL = "🦿"
        ERROR = "❌"
        WARNING = "⚠️"
        INFO = "ℹ️"
        DEBUG = "🐛"
        CRITICAL = "💀"
        COFFEE = "☕"
        SUCCESS = "✅"
        FILE = "📄"
    class Colors:
        @staticmethod
        def red(t): return t
        @staticmethod
        def yellow(t): return t
        @staticmethod
        def green(t): return t
        @staticmethod
        def blue(t): return t
        @staticmethod
        def magenta(t): return t
        @staticmethod
        def cyan(t): return t
        RESET = ""
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
    MAX_LOG_SIZE = 10000
    LOG_ROTATION_COUNT = 5
    LOG_TRUNCATE_LENGTH = 500

# Импортируем состояние
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    _kostyl_state = None

# ═══════════════════════════════════════════════════════════════
# УРОВНИ ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

class LogLevel(Enum):
    """Уровни логирования (расширенные, с костыльными)."""
    TRACE = (0, "🔍", "TRACE")  # Самый подробный
    DEBUG = (10, Emoji.DEBUG, "DEBUG")
    INFO = (20, Emoji.INFO, "INFO")
    SUCCESS = (25, Emoji.SUCCESS, "SUCCESS")  # Новый уровень!
    COFFEE = (28, Emoji.COFFEE, "COFFEE")  # Уровень для кофе
    WARNING = (30, Emoji.WARNING, "WARNING")
    ERROR = (40, Emoji.ERROR, "ERROR")
    CRITICAL = (50, Emoji.CRITICAL, "CRITICAL")
    KOSTYL = (55, Emoji.KOSTYL, "KOSTYL")  # Особый уровень
    NUCLEAR = (60, "☢️", "NUCLEAR")
    APOCALYPSE = (70, "🔥", "APOCALYPSE")
    
    @property
    def value_int(self) -> int:
        return self.value[0]
    
    @property
    def emoji(self) -> str:
        return self.value[1]
    
    @property
    def name_short(self) -> str:
        return self.value[2]
    
    @classmethod
    def from_string(cls, level: str) -> 'LogLevel':
        """Получает уровень из строки."""
        level_upper = level.upper()
        for log_level in cls:
            if log_level.name == level_upper or log_level.name_short == level_upper:
                return log_level
        return cls.INFO

# ═══════════════════════════════════════════════════════════════
# ЗАПИСЬ ЛОГА
# ═══════════════════════════════════════════════════════════════

@dataclass
class LogRecord:
    """Запись в логе."""
    timestamp: float
    level: LogLevel
    message: str
    module: str = ""
    function: str = ""
    line: int = 0
    thread_id: int = 0
    thread_name: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[Exception] = None
    
    @property
    def formatted_time(self) -> str:
        return datetime.fromtimestamp(self.timestamp).strftime(DATETIME_FORMAT)
    
    @property
    def level_str(self) -> str:
        return f"{self.level.emoji} {self.level.name_short}"
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'time': self.formatted_time,
            'level': self.level.name,
            'level_emoji': self.level.emoji,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line': self.line,
            'thread_id': self.thread_id,
            'thread_name': self.thread_name,
            'extra': self.extra,
            'has_exception': self.exception is not None,
        }
    
    def __str__(self):
        return (
            f"{self.formatted_time} {self.level_str} "
            f"[{self.module}:{self.line}] {self.message}"
        )

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ ОБРАБОТЧИК ЛОГОВ
# ═══════════════════════════════════════════════════════════════

class BaseKostylHandler:
    """Базовый класс для обработчиков логов."""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG):
        self.level = level
        self._formatter = None
    
    def set_formatter(self, formatter: 'KostylFormatter'):
        self._formatter = formatter
    
    def format(self, record: LogRecord) -> str:
        if self._formatter:
            return self._formatter.format(record)
        return str(record)
    
    def can_handle(self, record: LogRecord) -> bool:
        return record.level.value_int >= self.level.value_int
    
    def handle(self, record: LogRecord):
        if self.can_handle(record):
            self.emit(record)
    
    def emit(self, record: LogRecord):
        raise NotImplementedError
    
    def flush(self):
        pass
    
    def close(self):
        pass

# ═══════════════════════════════════════════════════════════════
# ФОРМАТТЕР ЛОГОВ
# ═══════════════════════════════════════════════════════════════

class KostylFormatter:
    """Форматирует записи лога."""
    
    def __init__(
        self,
        format: str = "{emoji} {time} [{level}] {module}:{line} {function}() → {message}",
        use_colors: bool = True,
        use_emoji: bool = True,
    ):
        self.format = format
        self.use_colors = use_colors
        self.use_emoji = use_emoji
    
    def format(self, record: LogRecord) -> str:
        """Форматирует запись лога."""
        try:
            result = self.format
            
            replacements = {
                '{emoji}': record.level.emoji if self.use_emoji else '',
                '{time}': record.formatted_time,
                '{level}': record.level.name_short,
                '{message}': record.message,
                '{module}': record.module,
                '{function}': record.function,
                '{line}': str(record.line),
                '{thread}': record.thread_name,
                '{thread_id}': str(record.thread_id),
            }
            
            for key, value in replacements.items():
                result = result.replace(key, value)
            
            # Добавляем информацию об исключении
            if record.exception:
                result += f"\n{Colors.RED}{traceback.format_exc()}{Colors.RESET}"
            
            # Добавляем extra данные
            if record.extra:
                extra_str = ", ".join(f"{k}={v}" for k, v in record.extra.items())
                result += f" [{extra_str}]"
            
            # Цветное форматирование
            if self.use_colors:
                result = self._apply_colors(result, record.level)
            
            return result
            
        except Exception as e:
            return f"[FORMATTER ERROR: {e}] {record.message}"
    
    def _apply_colors(self, text: str, level: LogLevel) -> str:
        """Применяет цвета в зависимости от уровня."""
        color_map = {
            LogLevel.TRACE: Colors.CYAN,
            LogLevel.DEBUG: Colors.BLUE,
            LogLevel.INFO: Colors.GREEN,
            LogLevel.SUCCESS: Colors.GREEN,
            LogLevel.COFFEE: Colors.MAGENTA,
            LogLevel.WARNING: Colors.YELLOW,
            LogLevel.ERROR: Colors.RED,
            LogLevel.CRITICAL: Colors.RED + Colors.BOLD,
            LogLevel.KOSTYL: Colors.CYAN + Colors.BOLD,
            LogLevel.NUCLEAR: Colors.BG_RED + Colors.BRIGHT_WHITE,
            LogLevel.APOCALYPSE: Colors.BG_RED + Colors.BRIGHT_YELLOW,
        }
        
        color = color_map.get(level, "")
        if color:
            return f"{color}{text}{Colors.RESET}"
        return text

# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ ЛОГОВ
# ═══════════════════════════════════════════════════════════════

class ConsoleHandler(BaseKostylHandler):
    """Выводит логи в консоль."""
    
    def __init__(
        self,
        level: LogLevel = LogLevel.DEBUG,
        stream=sys.stdout,
        use_colors: bool = True
    ):
        super().__init__(level)
        self.stream = stream
        self.set_formatter(KostylFormatter(use_colors=use_colors))
    
    def emit(self, record: LogRecord):
        try:
            formatted = self.format(record)
            print(formatted, file=self.stream, flush=True)
        except Exception:
            # Если даже логгер упал — пишем хоть что-то
            print(f"[LOGGER ERROR] {record.message}", file=sys.stderr)

class FileHandler(BaseKostylHandler):
    """Пишет логи в файл."""
    
    def __init__(
        self,
        filepath: str = "kostylpy.log",
        level: LogLevel = LogLevel.DEBUG,
        max_size_mb: int = 10,
        backup_count: int = 3,
        create_dirs: bool = True,
    ):
        super().__init__(level)
        self.filepath = filepath
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count
        
        if create_dirs:
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
        
        self._file = open(filepath, 'a', encoding='utf-8')
        self._lock = threading.Lock()
        self.set_formatter(KostylFormatter(use_colors=False))
    
    def emit(self, record: LogRecord):
        try:
            with self._lock:
                formatted = self.format(record)
                self._file.write(formatted + '\n')
                self._file.flush()
                
                # Проверяем размер
                if self._file.tell() > self.max_size_mb * 1024 * 1024:
                    self._rotate()
        except Exception:
            pass  # Не можем логировать ошибку логирования
    
    def _rotate(self):
        """Ротирует файл лога."""
        try:
            self._file.close()
            
            # Переименовываем старые файлы
            for i in range(self.backup_count - 1, 0, -1):
                old_name = f"{self.filepath}.{i}"
                new_name = f"{self.filepath}.{i + 1}"
                if os.path.exists(old_name):
                    os.rename(old_name, new_name)
            
            # Переименовываем текущий
            if os.path.exists(self.filepath):
                os.rename(self.filepath, f"{self.filepath}.1")
            
            # Открываем новый
            self._file = open(self.filepath, 'a', encoding='utf-8')
        except Exception:
            self._file = open(self.filepath, 'a', encoding='utf-8')
    
    def close(self):
        try:
            self._file.close()
        except:
            pass

class MemoryHandler(BaseKostylHandler):
    """Хранит логи в памяти."""
    
    def __init__(
        self,
        level: LogLevel = LogLevel.DEBUG,
        max_records: int = 1000,
    ):
        super().__init__(level)
        self.max_records = max_records
        self._records: List[LogRecord] = []
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord):
        with self._lock:
            self._records.append(record)
            if len(self._records) > self.max_records:
                self._records = self._records[-self.max_records:]
    
    def get_records(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100,
    ) -> List[LogRecord]:
        """Возвращает записи с фильтрацией."""
        with self._lock:
            records = self._records
            if level:
                records = [r for r in records if r.level.value_int >= level.value_int]
            return records[-limit:]
    
    def search(self, query: str, limit: int = 100) -> List[LogRecord]:
        """Ищет записи по тексту."""
        with self._lock:
            results = [r for r in self._records if query.lower() in r.message.lower()]
            return results[-limit:]
    
    def clear(self):
        with self._lock:
            self._records.clear()
    
    def export(self, format: str = "json") -> str:
        """Экспортирует логи."""
        with self._lock:
            if format == "json":
                return json.dumps(
                    [r.to_dict() for r in self._records],
                    indent=2,
                    ensure_ascii=False
                )
            else:
                return "\n".join(str(r) for r in self._records)
    
    @property
    def count(self) -> int:
        return len(self._records)

class NetworkHandler(BaseKostylHandler):
    """Отправляет логи по сети (если повезёт)."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9999,
        level: LogLevel = LogLevel.WARNING,
    ):
        super().__init__(level)
        self.host = host
        self.port = port
        self._socket = None
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord):
        try:
            data = json.dumps(record.to_dict()).encode('utf-8')
            # Не будем реально отправлять, просто запишем в лог что попытались
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.UNKNOWN,
                    f"Сетевое логирование: {record.message[:100]}"
                )
        except Exception:
            pass

class CoffeeHandler(BaseKostylHandler):
    """
    Специальный обработчик для кофе-брейков.
    Логирует каждый кофе-брейк отдельно.
    """
    
    def __init__(self, filepath: str = "coffee.log"):
        super().__init__(LogLevel.COFFEE)
        self.filepath = filepath
        self._coffee_count = 0
        self._total_coffee_time = 0.0
        self._lock = threading.Lock()
        
        self.set_formatter(KostylFormatter(
            format="☕ {time} КОФЕ-БРЕЙК #{coffee}: {message} ({duration}с)",
            use_colors=True
        ))
    
    def emit(self, record: LogRecord):
        with self._lock:
            self._coffee_count += 1
            # Сохраняем в файл
            try:
                with open(self.filepath, 'a', encoding='utf-8') as f:
                    formatted = self.format(record)
                    f.write(formatted + '\n')
            except:
                pass
    
    @property
    def coffee_stats(self) -> Dict:
        return {
            'total_coffees': self._coffee_count,
            'total_time': self._total_coffee_time,
            'file': self.filepath,
        }

# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ ЛОГГЕР
# ═══════════════════════════════════════════════════════════════

class KostylLogger:
    """
    Главный костыльный логгер.
    Пишет логи везде и сразу.
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
        
        self._handlers: List[BaseKostylHandler] = []
        self._level = LogLevel.DEBUG
        self._disabled = False
        self._record_count = 0
        self._start_time = time.time()
        
        # Добавляем консольный обработчик по умолчанию
        self.add_handler(ConsoleHandler())
        
        # Добавляем обработчик в память
        memory = MemoryHandler()
        self.add_handler(memory)
        self.memory_handler = memory
    
    # ═══════════════════════════════════════════
    # УПРАВЛЕНИЕ ОБРАБОТЧИКАМИ
    # ═══════════════════════════════════════════
    
    def add_handler(self, handler: BaseKostylHandler):
        self._handlers.append(handler)
    
    def remove_handler(self, handler: BaseKostylHandler):
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def clear_handlers(self):
        for handler in self._handlers:
            handler.close()
        self._handlers.clear()
    
    def set_level(self, level: Union[LogLevel, str]):
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        self._level = level
    
    def disable(self):
        self._disabled = True
    
    def enable(self):
        self._disabled = False
    
    # ═══════════════════════════════════════════
    # МЕТОДЫ ЛОГИРОВАНИЯ
    # ═══════════════════════════════════════════
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Dict = None,
        exception: Optional[Exception] = None,
        stack_offset: int = 0,
    ):
        """Внутренний метод логирования."""
        if self._disabled:
            return
        
        if level.value_int < self._level.value_int:
            return
        
        # Получаем информацию о месте вызова
        frame = inspect.currentframe()
        for _ in range(3 + stack_offset):  # Пропускаем фреймы логгера
            if frame:
                frame = frame.f_back
        
        module = ""
        function = ""
        line = 0
        
        if frame:
            module = frame.f_globals.get('__name__', '')
            function = frame.f_code.co_name
            line = frame.f_lineno
        
        # Создаём запись
        record = LogRecord(
            timestamp=time.time(),
            level=level,
            message=message[:LOG_TRUNCATE_LENGTH],
            module=module,
            function=function,
            line=line,
            thread_id=threading.get_ident(),
            thread_name=threading.current_thread().name,
            extra=extra or {},
            exception=exception,
        )
        
        # Отправляем всем обработчикам
        for handler in self._handlers:
            try:
                handler.handle(record)
            except Exception as e:
                # Не можем логировать ошибку логирования
                print(f"[LOGGER HANDLER ERROR] {e}", file=sys.stderr)
        
        self._record_count += 1
    
    def trace(self, message: str, **extra):
        self._log(LogLevel.TRACE, message, extra)
    
    def debug(self, message: str, **extra):
        self._log(LogLevel.DEBUG, message, extra)
    
    def info(self, message: str, **extra):
        self._log(LogLevel.INFO, message, extra)
    
    def success(self, message: str, **extra):
        self._log(LogLevel.SUCCESS, message, extra)
    
    def coffee(self, message: str = "Кофе-брейк!", **extra):
        self._log(LogLevel.COFFEE, message, extra)
    
    def warning(self, message: str, **extra):
        self._log(LogLevel.WARNING, message, extra)
    
    def error(self, message: str, exception: Optional[Exception] = None, **extra):
        self._log(LogLevel.ERROR, message, extra, exception)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **extra):
        self._log(LogLevel.CRITICAL, message, extra, exception)
    
    def kostyl(self, message: str, **extra):
        self._log(LogLevel.KOSTYL, message, extra)
    
    def nuclear(self, message: str, **extra):
        self._log(LogLevel.NUCLEAR, message, extra)
    
    def apocalypse(self, message: str, **extra):
        self._log(LogLevel.APOCALYPSE, message, extra)
    
    def exception(self, exc: Exception, message: str = ""):
        """Логирует исключение с трейсбеком."""
        msg = message or f"Исключение: {type(exc).__name__}: {str(exc)[:200]}"
        self._log(LogLevel.ERROR, msg, exception=exc)
    
    # ═══════════════════════════════════════════
    # УТИЛИТЫ
    # ═══════════════════════════════════════════
    
    def get_records(self, level: Optional[LogLevel] = None, limit: int = 100) -> List[LogRecord]:
        """Возвращает записи из памяти."""
        if hasattr(self, 'memory_handler'):
            return self.memory_handler.get_records(level, limit)
        return []
    
    def search(self, query: str, limit: int = 100) -> List[LogRecord]:
        """Ищет по логам."""
        if hasattr(self, 'memory_handler'):
            return self.memory_handler.search(query, limit)
        return []
    
    def export_logs(self, filepath: str = "kostylpy_export.json"):
        """Экспортирует логи в файл."""
        try:
            if hasattr(self, 'memory_handler'):
                data = self.memory_handler.export("json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(data)
                self.info(f"Логи экспортированы в {filepath}")
                return True
        except Exception as e:
            self.error(f"Не удалось экспортировать логи: {e}")
        return False
    
    def stats(self) -> Dict:
        """Возвращает статистику логирования."""
        return {
            'total_records': self._record_count,
            'uptime': time.time() - self._start_time,
            'handlers': len(self._handlers),
            'level': self._level.name,
            'disabled': self._disabled,
            'memory_records': len(self.memory_handler._records) if hasattr(self, 'memory_handler') else 0,
        }
    
    def report(self) -> str:
        """Генерирует отчёт."""
        s = self.stats()
        return (
            f"{Emoji.FILE} ЛОГГЕР KOSTYLPY\n"
            f"   Записей: {s['total_records']}\n"
            f"   В памяти: {s['memory_records']}\n"
            f"   Обработчиков: {s['handlers']}\n"
            f"   Уровень: {s['level']}\n"
            f"   Время работы: {s['uptime']:.1f}с\n"
            f"   Статус: {'ОТКЛЮЧЕН' if s['disabled'] else 'АКТИВЕН'}"
        )

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ═══════════════════════════════════════════════════════════════

# Создаём глобальный логгер
logger = KostylLogger()

# Удобные алиасы
log = logger
LOG = logger

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР ДЛЯ ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

def log_execution(
    level: LogLevel = LogLevel.DEBUG,
    log_args: bool = True,
    log_result: bool = False,
    log_time: bool = True,
):
    """
    Декоратор для логирования выполнения функции.
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Логируем вызов
            args_str = ""
            if log_args and args:
                args_str = ", ".join(repr(a)[:50] for a in args)
            if log_args and kwargs:
                kwargs_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in kwargs.items())
                args_str += (", " if args_str else "") + kwargs_str
            
            logger.log(
                level,
                f"Вызов: {func_name}({args_str})"
            )
            
            # Выполняем
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                
                # Логируем результат
                parts = [f"{func_name} выполнена"]
                if log_time:
                    parts.append(f"за {elapsed:.4f}с")
                if log_result:
                    parts.append(f"→ {repr(result)[:100]}")
                
                logger.log(level, " ".join(parts))
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start
                logger.error(
                    f"{func_name} УПАЛА через {elapsed:.4f}с: {type(e).__name__}",
                    exception=e
                )
                raise
        
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основное
    'KostylLogger',
    'logger', 'log', 'LOG',  # Глобальные экземпляры
    
    # Уровни
    'LogLevel',
    
    # Записи
    'LogRecord',
    
    # Обработчики
    'BaseKostylHandler',
    'ConsoleHandler',
    'FileHandler',
    'MemoryHandler',
    'NetworkHandler',
    'CoffeeHandler',
    
    # Форматтер
    'KostylFormatter',
    
    # Декоратор
    'log_execution',
]

# Приветственное сообщение
logger.info("Логгер kostylpy инициализирован")
logger.coffee("Кофе готов к употреблению")