"""
Костыльные исключения kostylpy.
Потому что обычных исключений недостаточно.
Нужны исключения для исключений, ошибки для ошибок,
и костыли для костылей.

Каждое исключение имеет:
- Уникальный код ошибки
- Уровень серьёзности
- Встроенный костыль-фикс
- Автоматическое логирование
- Возможность самовосстановления
"""

import sys
import time
import random
import traceback
import threading
import inspect
from typing import Any, Optional, Dict, List, Tuple, Union
from enum import Enum, auto
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════
# КОДЫ ОШИБОК
# ═══════════════════════════════════════════════════════════════

class ErrorCode(Enum):
    """Уникальные коды ошибок kostylpy."""
    
    # 1xxx - Общие ошибки
    UNKNOWN = 1000
    TOO_MANY_CRUTCHES = 1001
    CRUTCH_OVERFLOW = 1002
    COFFEE_DEPLETED = 1003
    
    # 2xxx - Ошибки печати
    PRINT_FAILED = 2001
    PRINT_TOO_SHORT = 2002
    PRINT_TOO_LONG = 2003
    PRINT_CONTAINS_SECRETS = 2004
    PRINT_BUFFER_OVERFLOW = 2005
    
    # 3xxx - Ошибки файлов
    FILE_NOT_FOUND_BUT_CREATED = 3001
    FILE_PERMISSION_DENIED_BUT_IGNORED = 3002
    FILE_CORRUPTED_BUT_RECOVERED = 3003
    FILE_DELETED_WHILE_READING = 3004
    FILE_TOO_BIG = 3005
    
    # 4xxx - Ошибки импорта
    IMPORT_FAILED_BUT_STUBBED = 4001
    IMPORT_CIRCULAR_DETECTED = 4002
    IMPORT_TOO_SLOW = 4003
    IMPORT_DEPRECATED = 4004
    
    # 5xxx - Ошибки типов
    TYPE_MISMATCH_BUT_COERCED = 5001
    TYPE_NOT_FOUND = 5002
    TYPE_TOO_COMPLEX = 5003
    TYPE_IS_NONE_BUT_SHOULDNT_BE = 5004
    
    # 6xxx - Ошибки памяти
    MEMORY_ALMOST_FULL = 6001
    MEMORY_LEAK_DETECTED = 6002
    MEMORY_LEAK_IGNORED = 6003
    GARBAGE_COLLECTOR_ON_STRIKE = 6004
    
    # 7xxx - Ошибки сети
    NETWORK_UNREACHABLE_BUT_LOCAL = 7001
    NETWORK_TIMEOUT_BUT_RETRIED = 7002
    NETWORK_DNS_FAILED = 7003
    NETWORK_TOO_MANY_REQUESTS = 7004
    
    # 8xxx - Ошибки декораторов
    DECORATOR_RECURSION = 8001
    DECORATOR_STACK_OVERFLOW = 8002
    DECORATOR_LOST_FUNCTION = 8003
    
    # 9xxx - Мета-ошибки
    ERROR_HANDLING_ERROR = 9001
    EXCEPTION_IN_EXCEPTION = 9002
    KOSTYL_BROKEN = 9003
    TOO_MANY_EXCEPTIONS = 9004
    EXCEPTION_FACTORY_EXPLODED = 9005
    MONKEY_PATCH = 9006

# ═══════════════════════════════════════════════════════════════
# УРОВНИ СЕРЬЁЗНОСТИ
# ═══════════════════════════════════════════════════════════════

class ErrorSeverity(Enum):
    """Уровни серьёзности ошибок."""
    WHATEVER = ("🤷 ВСЁ РАВНО", 0)
    COSMETIC = ("✨ КОСМЕТИЧЕСКАЯ", 1)
    MINOR = ("🟢 МАЛАЯ", 2)
    MODERATE = ("🟡 СРЕДНЯЯ", 3)
    MAJOR = ("🟠 КРУПНАЯ", 4)
    CRITICAL = ("🔴 КРИТИЧЕСКАЯ", 5)
    NUCLEAR = ("💀 ЯДЕРНАЯ", 6)
    APOCALYPTIC = ("🔥 АПОКАЛИПСИС", 7)
    HEAT_DEATH = ("❄️ ТЕПЛОВАЯ СМЕРТЬ", 8)
    
    def __str__(self):
        return self.value[0]
    
    @property
    def level(self) -> int:
        return self.value[1]

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЕ КЛАССЫ ИСКЛЮЧЕНИЙ
# ═══════════════════════════════════════════════════════════════

class KostylException(Exception):
    """
    Базовое исключение kostylpy.
    Все остальные исключения наследуются от него.
    Даже те, которые не должны.
    """
    
    _exception_counter = 0
    _exception_lock = threading.Lock()
    _all_exceptions: List['KostylException'] = []
    
    def __init__(
        self,
        message: str = "Что-то пошло не так (но мы это починим)",
        code: ErrorCode = ErrorCode.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MODERATE,
        original_exception: Optional[Exception] = None,
        auto_fix: bool = True,
        recovery_hint: str = "Попробуйте перезапустить (но это не точно)",
        *args,
        **kwargs
    ):
        super().__init__(message, *args)
        
        self.message = message
        self.code = code
        self.severity = severity
        self.original_exception = original_exception
        self.auto_fix = auto_fix
        self.recovery_hint = recovery_hint
        self.timestamp = time.time()
        self.thread_id = threading.get_ident()
        self.thread_name = threading.current_thread().name
        
        # Получаем место возникновения
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller = frame.f_back
            self.file = caller.f_code.co_filename
            self.line = caller.f_lineno
            self.function = caller.f_code.co_name
        else:
            self.file = "unknown"
            self.line = 0
            self.function = "unknown"
        
        # Уникальный ID
        with self._exception_lock:
            self.__class__._exception_counter += 1
            self.id = self.__class__._exception_counter
            self.__class__._all_exceptions.append(self)
        
        # Автоматическое логирование
        self._log_creation()
        
        # Автофикс
        if self.auto_fix:
            self._attempt_auto_fix()
    
    def _log_creation(self):
        """Логирует создание исключения."""
        # Пытаемся импортировать состояние
        try:
            from . import _kostyl_state, KostylSeverity
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                None,  # Будет переопределено
                f"Создано исключение #{self.id}: {self.__class__.__name__} "
                f"[{self.code.name}] - {self.message[:100]}"
            )
        except ImportError:
            pass  # Не можем импортировать — ну и ладно
    
    def _attempt_auto_fix(self):
        """Пытается автоматически исправить проблему."""
        # По умолчанию — ничего не делаем
        # Подклассы переопределяют этот метод
        self._was_fixed = False
    
    def __str__(self):
        parts = [
            f"[{self.severity}] {self.__class__.__name__}",
            f"Код: {self.code.name} ({self.code.value})",
            f"Сообщение: {self.message}",
        ]
        if self.original_exception:
            parts.append(f"Причина: {type(self.original_exception).__name__}: {self.original_exception}")
        if hasattr(self, '_was_fixed') and self._was_fixed:
            parts.append("✅ АВТОМАТИЧЕСКИ ИСПРАВЛЕНО")
        parts.append(f"💡 {self.recovery_hint}")
        return "\n  ".join(parts)
    
    def __repr__(self):
        return (
            f"<{self.__class__.__name__} #{self.id} "
            f"[{self.code.name}] {self.severity}: {self.message[:50]}>"
        )
    
    def to_dict(self) -> dict:
        """Сериализует исключение в словарь."""
        return {
            'id': self.id,
            'type': self.__class__.__name__,
            'code': self.code.name,
            'code_value': self.code.value,
            'severity': self.severity.name,
            'message': self.message,
            'file': self.file,
            'line': self.line,
            'function': self.function,
            'timestamp': self.timestamp,
            'thread_id': self.thread_id,
            'original_exception': str(self.original_exception) if self.original_exception else None,
            'auto_fixed': getattr(self, '_was_fixed', False),
            'recovery_hint': self.recovery_hint,
        }
    
    @classmethod
    def get_all_exceptions(cls) -> List['KostylException']:
        """Возвращает все созданные исключения."""
        return cls._all_exceptions.copy()
    
    @classmethod
    def get_exception_count(cls) -> int:
        """Возвращает количество созданных исключений."""
        return cls._exception_counter

# ═══════════════════════════════════════════════════════════════
# КОНКРЕТНЫЕ ИСКЛЮЧЕНИЯ
# ═══════════════════════════════════════════════════════════════

class PrintException(KostylException):
    """Исключения, связанные с печатью."""
    pass

class PrintFailedException(PrintException):
    """Print не смог вывести сообщение."""
    
    def __init__(self, message: str = "Не удалось вывести сообщение", **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.PRINT_FAILED,
            severity=ErrorSeverity.MAJOR,
            recovery_hint="Попробуйте написать на бумаге",
            **kwargs
        )

class PrintTooShortException(PrintException):
    """Сообщение слишком короткое."""
    
    def __init__(self, message: str = "Сообщение подозрительно короткое", **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.PRINT_TOO_SHORT,
            severity=ErrorSeverity.COSMETIC,
            recovery_hint="Добавьте больше букв",
            **kwargs
        )
    
    def _attempt_auto_fix(self):
        """Дополняет сообщение до приемлемой длины."""
        self.message = self.message + " (дополнено kostylpy для минимальной длины)"
        self._was_fixed = True

class PrintSecretsException(PrintException):
    """Обнаружен вывод секретных данных."""
    
    def __init__(self, message: str = "Обнаружен возможный вывод секретов", **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.PRINT_CONTAINS_SECRETS,
            severity=ErrorSeverity.CRITICAL,
            recovery_hint="НЕ ВЫВОДИТЕ ПАРОЛИ В КОНСОЛЬ!",
            **kwargs
        )

# ═══════════════════════════════════════════════════════════════

class FileException(KostylException):
    """Исключения, связанные с файлами."""
    pass

class FileNotFoundButCreatedException(FileException):
    """Файл не найден, но мы его создали."""
    
    def __init__(self, filepath: str = "", **kwargs):
        super().__init__(
            message=f"Файл '{filepath}' не найден, но создана заглушка",
            code=ErrorCode.FILE_NOT_FOUND_BUT_CREATED,
            severity=ErrorSeverity.MODERATE,
            recovery_hint="Создайте настоящий файл... когда-нибудь",
            **kwargs
        )
        self.filepath = filepath
    
    def _attempt_auto_fix(self):
        """Пытается создать файл."""
        try:
            with open(self.filepath, 'w') as f:
                f.write("# Создано kostylpy\n")
            self._was_fixed = True
        except:
            self._was_fixed = False

class FilePermissionDeniedButIgnoredException(FileException):
    """Нет прав, но мы сделали вид что есть."""
    
    def __init__(self, filepath: str = "", **kwargs):
        super().__init__(
            message=f"Нет прав на '{filepath}', но мы проигнорировали",
            code=ErrorCode.FILE_PERMISSION_DENIED_BUT_IGNORED,
            severity=ErrorSeverity.MAJOR,
            recovery_hint="Попросите разрешения у администратора",
            **kwargs
        )
        self.filepath = filepath

class FileCorruptedButRecoveredException(FileException):
    """Файл повреждён, но мы восстановили что смогли."""
    
    def __init__(self, filepath: str = "", recovered_data: str = "", **kwargs):
        super().__init__(
            message=f"Файл '{filepath}' повреждён, восстановлено {len(recovered_data)} байт",
            code=ErrorCode.FILE_CORRUPTED_BUT_RECOVERED,
            severity=ErrorSeverity.MAJOR,
            recovery_hint="Данные могут быть неполными",
            **kwargs
        )
        self.filepath = filepath
        self.recovered_data = recovered_data

# ═══════════════════════════════════════════════════════════════

class ImportException(KostylException):
    """Исключения, связанные с импортом."""
    pass

class ImportFailedButStubbedException(ImportException):
    """Модуль не найден, создана заглушка."""
    
    def __init__(self, module_name: str = "", fallback: str = "", **kwargs):
        super().__init__(
            message=f"Модуль '{module_name}' не найден → заменён на '{fallback}'",
            code=ErrorCode.IMPORT_FAILED_BUT_STUBBED,
            severity=ErrorSeverity.MODERATE,
            recovery_hint=f"Установите модуль: pip install {module_name}",
            **kwargs
        )
        self.module_name = module_name
        self.fallback = fallback
    
    def _attempt_auto_fix(self):
        """Пытается установить модуль (ОПАСНО!)."""
        # Не будем автоматически ставить пакеты, это слишком даже для нас
        self._was_fixed = False

class ImportCircularDetectedException(ImportException):
    """Обнаружен циклический импорт."""
    
    def __init__(self, modules: List[str] = None, **kwargs):
        modules = modules or []
        cycle_str = " → ".join(modules) if modules else "неизвестный цикл"
        super().__init__(
            message=f"Циклический импорт: {cycle_str}",
            code=ErrorCode.IMPORT_CIRCULAR_DETECTED,
            severity=ErrorSeverity.CRITICAL,
            recovery_hint="Разорвите круг! Перепроектируйте архитектуру!",
            **kwargs
        )
        self.modules = modules

# ═══════════════════════════════════════════════════════════════

class TypeException(KostylException):
    """Исключения, связанные с типами."""
    pass

class TypeMismatchButCoercedException(TypeException):
    """Не тот тип, но мы преобразовали."""
    
    def __init__(self, expected: str = "", got: str = "", value: Any = None, **kwargs):
        super().__init__(
            message=f"Ожидался {expected}, получен {got}. Значение '{value}' преобразовано.",
            code=ErrorCode.TYPE_MISMATCH_BUT_COERCED,
            severity=ErrorSeverity.MINOR,
            recovery_hint="Проверьте типы данных",
            **kwargs
        )
        self.expected = expected
        self.got = got
        self.value = value
    
    def _attempt_auto_fix(self):
        """Пытается преобразовать значение."""
        try:
            if self.expected == 'int' and self.got == 'str':
                self.value = int(self.value)
                self._was_fixed = True
            elif self.expected == 'str' and self.got == 'int':
                self.value = str(self.value)
                self._was_fixed = True
            elif self.expected == 'float' and self.got == 'str':
                self.value = float(self.value)
                self._was_fixed = True
            else:
                self._was_fixed = False
        except:
            self._was_fixed = False

class TypeIsNoneException(TypeException):
    """Значение None там, где не должно быть."""
    
    def __init__(self, variable_name: str = "переменная", **kwargs):
        super().__init__(
            message=f"'{variable_name}' is None, а не должно быть",
            code=ErrorCode.TYPE_IS_NONE_BUT_SHOULDNT_BE,
            severity=ErrorSeverity.MAJOR,
            recovery_hint="Проверьте, что значение инициализировано",
            **kwargs
        )
        self.variable_name = variable_name

# ═══════════════════════════════════════════════════════════════

class MemoryException(KostylException):
    """Исключения, связанные с памятью."""
    pass

class MemoryAlmostFullException(MemoryException):
    """Память почти закончилась."""
    
    def __init__(self, used_percent: float = 0.0, **kwargs):
        super().__init__(
            message=f"Память заполнена на {used_percent:.1f}%",
            code=ErrorCode.MEMORY_ALMOST_FULL,
            severity=ErrorSeverity.NUCLEAR,
            recovery_hint="Закройте Chrome!",
            **kwargs
        )
        self.used_percent = used_percent

class MemoryLeakDetectedException(MemoryException):
    """Обнаружена утечка памяти."""
    
    def __init__(self, leaked_mb: float = 0.0, **kwargs):
        super().__init__(
            message=f"Утечка памяти: {leaked_mb:.1f} МБ",
            code=ErrorCode.MEMORY_LEAK_DETECTED,
            severity=ErrorSeverity.CRITICAL,
            recovery_hint="Перезапустите приложение. Или купите ещё RAM.",
            **kwargs
        )
        self.leaked_mb = leaked_mb

class GarbageCollectorOnStrikeException(MemoryException):
    """Сборщик мусора бастует."""
    
    def __init__(self, **kwargs):
        super().__init__(
            message="Сборщик мусора объявил забастовку",
            code=ErrorCode.GARBAGE_COLLECTOR_ON_STRIKE,
            severity=ErrorSeverity.APOCALYPTIC,
            recovery_hint="Вызовите gc.collect() с уважением",
            **kwargs
        )
    
    def _attempt_auto_fix(self):
        """Вызывает сборщик мусора."""
        import gc
        collected = gc.collect()
        self.message += f" (собрано {collected} объектов)"
        self._was_fixed = True

# ═══════════════════════════════════════════════════════════════

class NetworkException(KostylException):
    """Исключения, связанные с сетью."""
    pass

class NetworkUnreachableButLocalException(NetworkException):
    """Сеть недоступна, работаем локально."""
    
    def __init__(self, url: str = "", **kwargs):
        super().__init__(
            message=f"Сеть недоступна для '{url}', переключились на локальный режим",
            code=ErrorCode.NETWORK_UNREACHABLE_BUT_LOCAL,
            severity=ErrorSeverity.MAJOR,
            recovery_hint="Проверьте подключение к интернету",
            **kwargs
        )
        self.url = url

class NetworkTimeoutButRetriedException(NetworkException):
    """Таймаут сети, но мы перепробовали."""
    
    def __init__(self, url: str = "", attempts: int = 0, **kwargs):
        super().__init__(
            message=f"Таймаут '{url}' после {attempts} попыток",
            code=ErrorCode.NETWORK_TIMEOUT_BUT_RETRIED,
            severity=ErrorSeverity.MODERATE,
            recovery_hint="Проверьте скорость интернета",
            **kwargs
        )
        self.url = url
        self.attempts = attempts

# ═══════════════════════════════════════════════════════════════

class DecoratorException(KostylException):
    """Исключения, связанные с декораторами."""
    pass

class DecoratorRecursionException(DecoratorException):
    """Слишком много декораторов."""
    
    def __init__(self, func_name: str = "", depth: int = 0, **kwargs):
        super().__init__(
            message=f"Слишком глубокая рекурсия декораторов для '{func_name}' (глубина: {depth})",
            code=ErrorCode.DECORATOR_RECURSION,
            severity=ErrorSeverity.NUCLEAR,
            recovery_hint="Уберите часть декораторов",
            **kwargs
        )
        self.func_name = func_name
        self.depth = depth

class DecoratorLostFunctionException(DecoratorException):
    """Декоратор потерял функцию."""
    
    def __init__(self, decorator_name: str = "", **kwargs):
        super().__init__(
            message=f"Декоратор '{decorator_name}' потерял функцию (как?!?!)",
            code=ErrorCode.DECORATOR_LOST_FUNCTION,
            severity=ErrorSeverity.APOCALYPTIC,
            recovery_hint="Перепишите декоратор с нуля",
            **kwargs
        )
        self.decorator_name = decorator_name

# ═══════════════════════════════════════════════════════════════

class MetaException(KostylException):
    """Мета-исключения. Исключения для исключений."""
    pass

class ErrorHandlingErrorException(MetaException):
    """Ошибка при обработке ошибки."""
    
    def __init__(self, original_error: Exception = None, handler_error: Exception = None, **kwargs):
        super().__init__(
            message="Ошибка при обработке ошибки!",
            code=ErrorCode.ERROR_HANDLING_ERROR,
            severity=ErrorSeverity.HEAT_DEATH,
            recovery_hint="Всё очень плохо. Заварите кофе.",
            **kwargs
        )
        self.original_error = original_error
        self.handler_error = handler_error

class ExceptionInExceptionException(MetaException):
    """Исключение внутри исключения."""
    
    def __init__(self, outer: Exception = None, inner: Exception = None, **kwargs):
        super().__init__(
            message="Исключение возникло внутри другого исключения!",
            code=ErrorCode.EXCEPTION_IN_EXCEPTION,
            severity=ErrorSeverity.HEAT_DEATH,
            recovery_hint="Это уже слишком. Серьёзно.",
            **kwargs
        )
        self.outer = outer
        self.inner = inner

class KostylBrokenException(MetaException):
    """Костыль сломался."""
    
    def __init__(self, kostyl_name: str = "", **kwargs):
        super().__init__(
            message=f"Костыль '{kostyl_name}' сломался! Нужен костыль для костыля!",
            code=ErrorCode.KOSTYL_BROKEN,
            severity=ErrorSeverity.APOCALYPTIC,
            recovery_hint="Поставьте костыль на костыль",
            **kwargs
        )
        self.kostyl_name = kostyl_name
    
    def _attempt_auto_fix(self):
        """Пытается починить костыль костылём."""
        self.message += " (починен запасным костылём)"
        self._was_fixed = True

class TooManyExceptionsException(MetaException):
    """Слишком много исключений."""
    
    def __init__(self, count: int = 0, **kwargs):
        super().__init__(
            message=f"Создано {count} исключений. Может, хватит?",
            code=ErrorCode.TOO_MANY_EXCEPTIONS,
            severity=ErrorSeverity.HEAT_DEATH,
            recovery_hint="Остановите программу. Пожалуйста.",
            **kwargs
        )
        self.count = count

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА ИСКЛЮЧЕНИЙ
# ═══════════════════════════════════════════════════════════════

class ExceptionFactory:
    """
    Фабрика для создания исключений.
    Потому что создавать исключения вручную — скучно.
    """
    
    _exception_map: Dict[ErrorCode, type] = {
        ErrorCode.PRINT_FAILED: PrintFailedException,
        ErrorCode.PRINT_TOO_SHORT: PrintTooShortException,
        ErrorCode.PRINT_CONTAINS_SECRETS: PrintSecretsException,
        ErrorCode.FILE_NOT_FOUND_BUT_CREATED: FileNotFoundButCreatedException,
        ErrorCode.FILE_PERMISSION_DENIED_BUT_IGNORED: FilePermissionDeniedButIgnoredException,
        ErrorCode.FILE_CORRUPTED_BUT_RECOVERED: FileCorruptedButRecoveredException,
        ErrorCode.IMPORT_FAILED_BUT_STUBBED: ImportFailedButStubbedException,
        ErrorCode.IMPORT_CIRCULAR_DETECTED: ImportCircularDetectedException,
        ErrorCode.TYPE_MISMATCH_BUT_COERCED: TypeMismatchButCoercedException,
        ErrorCode.TYPE_IS_NONE_BUT_SHOULDNT_BE: TypeIsNoneException,
        ErrorCode.MEMORY_ALMOST_FULL: MemoryAlmostFullException,
        ErrorCode.MEMORY_LEAK_DETECTED: MemoryLeakDetectedException,
        ErrorCode.GARBAGE_COLLECTOR_ON_STRIKE: GarbageCollectorOnStrikeException,
        ErrorCode.NETWORK_UNREACHABLE_BUT_LOCAL: NetworkUnreachableButLocalException,
        ErrorCode.NETWORK_TIMEOUT_BUT_RETRIED: NetworkTimeoutButRetriedException,
        ErrorCode.DECORATOR_RECURSION: DecoratorRecursionException,
        ErrorCode.DECORATOR_LOST_FUNCTION: DecoratorLostFunctionException,
        ErrorCode.ERROR_HANDLING_ERROR: ErrorHandlingErrorException,
        ErrorCode.EXCEPTION_IN_EXCEPTION: ExceptionInExceptionException,
        ErrorCode.KOSTYL_BROKEN: KostylBrokenException,
        ErrorCode.TOO_MANY_EXCEPTIONS: TooManyExceptionsException,
    }
    
    @classmethod
    def create(
        cls,
        code: ErrorCode,
        message: str = "",
        **kwargs
    ) -> KostylException:
        """Создаёт исключение по коду."""
        exception_class = cls._exception_map.get(code, KostylException)
        
        try:
            return exception_class(message=message, code=code, **kwargs)
        except Exception as e:
            # Если не можем создать нужное исключение — создаём мета-исключение
            return ExceptionFactoryExplodedException(
                message=f"Не удалось создать исключение {code.name}: {e}",
                original_exception=e
            )
    
    @classmethod
    def create_from_original(
        cls,
        original: Exception,
        message: str = "",
        severity: ErrorSeverity = ErrorSeverity.MODERATE
    ) -> KostylException:
        """Создаёт костыльное исключение на основе обычного."""
        # Определяем код по типу оригинального исключения
        if isinstance(original, ZeroDivisionError):
            code = ErrorCode.UNKNOWN
        elif isinstance(original, FileNotFoundError):
            code = ErrorCode.FILE_NOT_FOUND_BUT_CREATED
        elif isinstance(original, ImportError):
            code = ErrorCode.IMPORT_FAILED_BUT_STUBBED
        elif isinstance(original, TypeError):
            code = ErrorCode.TYPE_MISMATCH_BUT_COERCED
        elif isinstance(original, MemoryError):
            code = ErrorCode.MEMORY_ALMOST_FULL
        elif isinstance(original, PermissionError):
            code = ErrorCode.FILE_PERMISSION_DENIED_BUT_IGNORED
        else:
            code = ErrorCode.UNKNOWN
        
        return cls.create(
            code=code,
            message=message or str(original),
            severity=severity,
            original_exception=original
        )
    
    @classmethod
    def random_exception(cls) -> KostylException:
        """Создаёт случайное исключение (для тестов, наверное)."""
        codes = list(cls._exception_map.keys())
        code = random.choice(codes)
        messages = [
            "Что-то пошло не так",
            "Неожиданная ошибка",
            "Этого не должно было случиться",
            "Костыль не выдержал",
            "Слишком много костылей",
        ]
        return cls.create(code=code, message=random.choice(messages))

# Специальное исключение для фабрики
class ExceptionFactoryExplodedException(KostylException):
    """Фабрика исключений взорвалась."""
    
    def __init__(self, message: str = "", **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.EXCEPTION_FACTORY_EXPLODED,
            severity=ErrorSeverity.HEAT_DEATH,
            recovery_hint="Фабрика исключений сломана. Это конец.",
            **kwargs
        )

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР ДЛЯ АВТОМАТИЧЕСКОГО ПРЕОБРАЗОВАНИЯ ИСКЛЮЧЕНИЙ
# ═══════════════════════════════════════════════════════════════

def kostylize_exceptions(
    default_code: ErrorCode = ErrorCode.UNKNOWN,
    default_severity: ErrorSeverity = ErrorSeverity.MODERATE,
    reraise: bool = True
):
    """
    Декоратор, который преобразует обычные исключения в костыльные.
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KostylException:
                raise  # Костыльные исключения не трогаем
            except Exception as e:
                kostyl_exc = ExceptionFactory.create_from_original(
                    e,
                    message=f"В функции '{func.__name__}': {e}",
                    severity=default_severity
                )
                if reraise:
                    raise kostyl_exc from e
                return None
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Базовые
    'KostylException',
    'ErrorCode',
    'ErrorSeverity',
    
    # Print
    'PrintException',
    'PrintFailedException',
    'PrintTooShortException',
    'PrintSecretsException',
    
    # File
    'FileException',
    'FileNotFoundButCreatedException',
    'FilePermissionDeniedButIgnoredException',
    'FileCorruptedButRecoveredException',
    
    # Import
    'ImportException',
    'ImportFailedButStubbedException',
    'ImportCircularDetectedException',
    
    # Type
    'TypeException',
    'TypeMismatchButCoercedException',
    'TypeIsNoneException',
    
    # Memory
    'MemoryException',
    'MemoryAlmostFullException',
    'MemoryLeakDetectedException',
    'GarbageCollectorOnStrikeException',
    
    # Network
    'NetworkException',
    'NetworkUnreachableButLocalException',
    'NetworkTimeoutButRetriedException',
    
    # Decorator
    'DecoratorException',
    'DecoratorRecursionException',
    'DecoratorLostFunctionException',
    
    # Meta
    'MetaException',
    'ErrorHandlingErrorException',
    'ExceptionInExceptionException',
    'KostylBrokenException',
    'TooManyExceptionsException',
    'ExceptionFactoryExplodedException',
    
    # Утилиты
    'ExceptionFactory',
    'kostylize_exceptions',
]

# Считаем количество исключений
_exception_classes = [
    cls for cls in globals().values()
    if isinstance(cls, type) and issubclass(cls, KostylException)
]
print(f"🦿 kostylpy.exceptions: загружено {len(_exception_classes)} типов исключений")
print(f"   Кодов ошибок: {len(ErrorCode)}")
print(f"   Уровней серьёзности: {len(ErrorSeverity)}")