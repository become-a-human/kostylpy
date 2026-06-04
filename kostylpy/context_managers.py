"""
Контекстные менеджеры kostylpy.
Каждый контекстный менеджер — это маленькая вселенная костылей.
Они управляют ресурсами, которых нет, обрабатывают ошибки,
которые не произошли, и логируют события, которые не случились.
"""

import sys
import os
import time
import random
import threading
import traceback
import warnings
import signal
import tempfile
import io
import json
import hashlib
import functools
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем состояние с защитой от циклического импорта
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    class _FakeSeverity(Enum):
        COSMETIC = "COSMETIC"
        MINOR = "MINOR"
        MODERATE = "MODERATE"
        MAJOR = "MAJOR"
        CRITICAL = "CRITICAL"
        NUCLEAR = "NUCLEAR"
        APOCALYPTIC = "APOCALYPTIC"
    
    class _FakeCategory(Enum):
        CONTEXT = "context"
        UNKNOWN = "unknown"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class ContextStatus(Enum):
    """Статус контекстного менеджера."""
    CREATED = "создан"
    ENTERED = "вошли"
    ACTIVE = "активен"
    ERROR = "ошибка"
    RECOVERED = "восстановлен"
    EXITED = "вышли"
    DESTROYED = "уничтожен"
    ZOMBIE = "зомби (не должен существовать)"

@dataclass
class ContextStats:
    """Статистика контекстного менеджера."""
    times_entered: int = 0
    times_exited: int = 0
    errors_caught: int = 0
    errors_escaped: int = 0
    resources_allocated: int = 0
    resources_freed: int = 0
    total_time_spent: float = 0.0
    zombie_count: int = 0
    
    def summary(self) -> str:
        return (
            f"Входов: {self.times_entered}, "
            f"Выходов: {self.times_exited}, "
            f"Поймано ошибок: {self.errors_caught}, "
            f"Упущено ошибок: {self.errors_escaped}, "
            f"Ресурсов выделено: {self.resources_allocated}, "
            f"Ресурсов освобождено: {self.resources_freed}, "
            f"Зомби: {self.zombie_count}"
        )

class KostylResource:
    """
    Ресурс, который не существует, но мы делаем вид что управляем им.
    """
    
    def __init__(self, name: str, resource_type: str = "неизвестный"):
        self.name = name
        self.resource_type = resource_type
        self.allocated = False
        self.freed = False
        self.creation_time = time.time()
        self._data = {}
    
    def allocate(self):
        """Выделяет ресурс (понарошку)."""
        if self.allocated:
            warnings.warn(f"Ресурс '{self.name}' уже выделен. Двойное выделение!")
        self.allocated = True
        return self
    
    def free(self):
        """Освобождает ресурс (тоже понарошку)."""
        if not self.allocated:
            warnings.warn(f"Ресурс '{self.name}' не был выделен. Двойное освобождение!")
        if self.freed:
            warnings.warn(f"Ресурс '{self.name}' уже освобождён. Тройное освобождение!")
        self.freed = True
        self.allocated = False
    
    def is_leaked(self) -> bool:
        """Проверяет, утёк ли ресурс."""
        return self.allocated and not self.freed
    
    def __repr__(self):
        status = "выделен" if self.allocated else "свободен"
        if self.freed:
            status = "освобождён"
        return f"<KostylResource: {self.name} ({self.resource_type}) [{status}]>"

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ КЛАСС ДЛЯ ВСЕХ КОНТЕКСТНЫХ МЕНЕДЖЕРОВ
# ═══════════════════════════════════════════════════════════════

class BaseKostylContext:
    """
    Базовый класс для всех костыльных контекстных менеджеров.
    Содержит общую логику, которую никто не просил.
    """
    
    def __init__(self, name: str = "безымянный костыль"):
        self.name = name
        self.status = ContextStatus.CREATED
        self.stats = ContextStats()
        self._enter_time: float = 0.0
        self._exit_time: float = 0.0
        self._resources: List[KostylResource] = []
        self._backup_globals: Dict[str, Any] = {}
        self._error_log: List[Dict] = []
        self._id = random.randint(10000, 99999)
    
    def _allocate_resource(self, resource_name: str, resource_type: str = "виртуальный") -> KostylResource:
        """Выделяет ресурс (добавляет в список для отслеживания)."""
        resource = KostylResource(resource_name, resource_type)
        resource.allocate()
        self._resources.append(resource)
        self.stats.resources_allocated += 1
        return resource
    
    def _free_resource(self, resource: KostylResource):
        """Освобождает ресурс."""
        resource.free()
        self.stats.resources_freed += 1
        if resource in self._resources:
            self._resources.remove(resource)
    
    def _free_all_resources(self):
        """Освобождает все ресурсы (включая утёкшие)."""
        leaked = [r for r in self._resources if r.is_leaked()]
        for resource in self._resources:
            try:
                resource.free()
                self.stats.resources_freed += 1
            except:
                pass
        self._resources.clear()
        
        if leaked:
            self.stats.zombie_count += len(leaked)
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.CONTEXT,
                f"Контекст '{self.name}': обнаружено {len(leaked)} утёкших ресурсов: "
                f"{', '.join(r.name for r in leaked)}"
            )
    
    def _backup_state(self, *names: str):
        """Сохраняет глобальное состояние."""
        import builtins
        for name in names:
            if hasattr(builtins, name):
                self._backup_globals[name] = getattr(builtins, name)
    
    def _restore_state(self):
        """Восстанавливает глобальное состояние."""
        import builtins
        for name, value in self._backup_globals.items():
            try:
                setattr(builtins, name, value)
            except:
                pass
        self._backup_globals.clear()
    
    def _log_error(self, error: Exception, recovered: bool = True):
        """Логирует ошибку."""
        self._error_log.append({
            'time': time.time(),
            'type': type(error).__name__,
            'message': str(error),
            'recovered': recovered,
            'traceback': traceback.format_exc()
        })
        if recovered:
            self.stats.errors_caught += 1
        else:
            self.stats.errors_escaped += 1
    
    def get_error_report(self) -> str:
        """Возвращает отчёт об ошибках."""
        if not self._error_log:
            return "Ошибок не было (подозрительно)"
        
        report = f"Отчёт об ошибках контекста '{self.name}':\n"
        for i, error in enumerate(self._error_log, 1):
            report += (
                f"  {i}. [{error['type']}] {error['message'][:100]}\n"
                f"     Восстановлен: {'да' if error['recovered'] else 'нет'}\n"
            )
        return report

# ═══════════════════════════════════════════════════════════════
# KostylContext — ОСНОВНОЙ КОНТЕКСТНЫЙ МЕНЕДЖЕР
# ═══════════════════════════════════════════════════════════════

class KostylContext(BaseKostylContext):
    """
    Основной костыльный контекстный менеджер.
    
    Использование:
        with KostylContext("мой блок") as ctx:
            # Код, который может упасть
            # Но не упадёт, потому что мы его поймаем
    
    Фичи:
        - Подавляет ВСЕ исключения
        - Логирует ошибки
        - Восстанавливает состояние
        - Делает кофе (не делает)
    """
    
    def __init__(
        self,
        name: str = "костыльный блок",
        suppress: Union[bool, Tuple[type, ...]] = True,
        log_errors: bool = True,
        reraise_critical: bool = False,
        timeout: Optional[float] = None,
        max_errors: int = -1,
        on_error: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        backup_builtins: bool = False
    ):
        """
        Args:
            name: Имя блока для логов
            suppress: Подавлять ли ошибки (True = все, False = никакие, tuple = только эти)
            log_errors: Логировать ли ошибки
            reraise_critical: Пробрасывать ли критические ошибки
            timeout: Таймаут выполнения блока
            max_errors: Максимальное количество ошибок (-1 = безлимит)
            on_error: Функция, вызываемая при ошибке (получает exception)
            on_exit: Функция, вызываемая при выходе
            backup_builtins: Сохранять и восстанавливать builtins
        """
        super().__init__(name)
        self.suppress = suppress
        self.log_errors = log_errors
        self.reraise_critical = reraise_critical
        self.timeout = timeout
        self.max_errors = max_errors
        self.on_error = on_error
        self.on_exit = on_exit
        self.backup_builtins = backup_builtins
        
        self._error_count = 0
        self._timed_out = False
        self._start_time: float = 0.0
    
    def __enter__(self):
        """Вход в контекст. Начинаем костылизацию."""
        self.status = ContextStatus.ENTERED
        self._enter_time = time.time()
        self._start_time = time.time()
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            f"🔧 Вход в контекст '{self.name}' (#{self._id})"
        )
        
        # Сохраняем состояние если нужно
        if self.backup_builtins:
            self._backup_state('print', 'open', 'input', '__import__')
        
        # Выделяем виртуальные ресурсы
        self._allocate_resource(f"{self.name}_lock", "блокировка")
        self._allocate_resource(f"{self.name}_buffer", "буфер")
        
        self.status = ContextStatus.ACTIVE
        self.stats.times_entered += 1
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста. Убираем за собой."""
        self._exit_time = time.time()
        duration = self._exit_time - self._enter_time
        self.stats.total_time_spent += duration
        
        # Проверка таймаута
        if self.timeout and duration > self.timeout:
            self._timed_out = True
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.CONTEXT,
                f"Контекст '{self.name}' превысил таймаут: {duration:.2f}с > {self.timeout}с"
            )
        
        # Обрабатываем исключение
        if exc_type is not None:
            self._error_count += 1
            self._log_error(exc_val, recovered=False)
            
            # Вызываем пользовательский обработчик
            if self.on_error:
                try:
                    self.on_error(exc_val)
                except Exception as handler_error:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MAJOR,
                        KostylCategory.CONTEXT,
                        f"Обработчик ошибок в '{self.name}' упал: {handler_error}"
                    )
            
            # Решаем, подавлять ли ошибку
            should_suppress = False
            
            if self.suppress is True:
                should_suppress = True
            elif isinstance(self.suppress, (tuple, list)):
                should_suppress = isinstance(exc_val, self.suppress)
            elif self.suppress is False:
                should_suppress = False
            
            # Проверяем лимит ошибок
            if self.max_errors > 0 and self._error_count >= self.max_errors:
                should_suppress = False
                _kostyl_state.record_kostyl(
                    KostylSeverity.NUCLEAR,
                    KostylCategory.CONTEXT,
                    f"Контекст '{self.name}': превышен лимит ошибок ({self.max_errors})!"
                )
            
            # Проверяем критические ошибки
            if self.reraise_critical:
                critical_types = (
                    SystemExit, KeyboardInterrupt, MemoryError,
                    SystemError, RuntimeError
                )
                if isinstance(exc_val, critical_types):
                    should_suppress = False
            
            if should_suppress:
                self._log_error(exc_val, recovered=True)
                self.status = ContextStatus.RECOVERED
                
                if self.log_errors:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MODERATE,
                        KostylCategory.CONTEXT,
                        f"Контекст '{self.name}': подавлена ошибка {exc_type.__name__}: "
                        f"{str(exc_val)[:100]}"
                    )
                
                self._cleanup()
                return True  # Подавляем исключение
            else:
                self.status = ContextStatus.ERROR
                self._cleanup()
                return False  # Пробрасываем исключение
        
        # Нет ошибки — нормальный выход
        self.status = ContextStatus.EXITED
        self.stats.times_exited += 1
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            f"🔧 Выход из контекста '{self.name}' (за {duration:.3f}с)"
        )
        
        self._cleanup()
        
        # Вызываем on_exit
        if self.on_exit:
            try:
                self.on_exit()
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.CONTEXT,
                    f"on_exit в '{self.name}' упал: {e}"
                )
        
        return False
    
    def _cleanup(self):
        """Очистка ресурсов."""
        self._free_all_resources()
        
        if self.backup_builtins:
            self._restore_state()
        
        if self._timed_out:
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.CONTEXT,
                f"Контекст '{self.name}': таймаут, принудительная очистка"
            )

# ═══════════════════════════════════════════════════════════════
# SafeFileContext — БЕЗОПАСНАЯ РАБОТА С ФАЙЛАМИ
# ═══════════════════════════════════════════════════════════════

class SafeFileContext(BaseKostylContext):
    """
    Контекстный менеджер для безопасной работы с файлами.
    
    Использование:
        with SafeFileContext("data.txt", "r") as f:
            content = f.read()
    
    Фичи:
        - Автоматически создаёт файл если его нет
        - Создаёт директории если их нет
        - Делает бекап перед записью
        - Логирует все операции
    """
    
    def __init__(
        self,
        filepath: str,
        mode: str = "r",
        encoding: str = "utf-8",
        create_if_missing: bool = True,
        create_dirs: bool = True,
        backup_before_write: bool = False,
        fallback_encoding: str = "latin-1",
        max_retries: int = 3
    ):
        """
        Args:
            filepath: Путь к файлу
            mode: Режим открытия
            encoding: Кодировка
            create_if_missing: Создавать файл если нет
            create_dirs: Создавать директории если нет
            backup_before_write: Делать бекап перед записью
            fallback_encoding: Запасная кодировка
            max_retries: Максимальное количество попыток
        """
        super().__init__(f"файл:{filepath}")
        self.filepath = filepath
        self.mode = mode
        self.encoding = encoding
        self.create_if_missing = create_if_missing
        self.create_dirs = create_dirs
        self.backup_before_write = backup_before_write
        self.fallback_encoding = fallback_encoding
        self.max_retries = max_retries
        
        self._file = None
        self._backup_path: Optional[str] = None
        self._bytes_written = 0
        self._bytes_read = 0
    
    def __enter__(self):
        """Открывает файл с костылями."""
        super().__enter__()
        
        # Создаём директории
        if self.create_dirs:
            dirname = os.path.dirname(self.filepath)
            if dirname and not os.path.exists(dirname):
                try:
                    os.makedirs(dirname, exist_ok=True)
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MINOR,
                        KostylCategory.CONTEXT,
                        f"Созданы директории: {dirname}"
                    )
                except Exception as e:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MAJOR,
                        KostylCategory.CONTEXT,
                        f"Не удалось создать директории {dirname}: {e}"
                    )
        
        # Делаем бекап
        if self.backup_before_write and 'w' in self.mode and os.path.exists(self.filepath):
            try:
                backup_path = f"{self.filepath}.kostyl_backup_{int(time.time())}"
                import shutil
                shutil.copy2(self.filepath, backup_path)
                self._backup_path = backup_path
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.CONTEXT,
                    f"Создан бекап: {backup_path}"
                )
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.CONTEXT,
                    f"Не удалось создать бекап: {e}"
                )
        
        # Пробуем открыть файл
        for attempt in range(self.max_retries):
            try:
                self._file = open(self.filepath, self.mode, encoding=self.encoding)
                self._allocate_resource(f"file:{self.filepath}", "файловый дескриптор")
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.CONTEXT,
                    f"Файл открыт: {self.filepath} (режим: {self.mode})"
                )
                return self._file
                
            except FileNotFoundError:
                if self.create_if_missing and 'r' not in self.mode:
                    # Создаём файл
                    try:
                        with open(self.filepath, 'w', encoding=self.encoding) as f:
                            f.write("")
                        _kostyl_state.record_kostyl(
                            KostylSeverity.MINOR,
                            KostylCategory.CONTEXT,
                            f"Файл создан: {self.filepath}"
                        )
                        continue
                    except:
                        pass
                
                # Создаём виртуальный файл
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.CONTEXT,
                    f"Файл не найден: {self.filepath}, создан виртуальный"
                )
                self._file = io.StringIO() if 'b' not in self.mode else io.BytesIO()
                return self._file
            
            except UnicodeDecodeError:
                if self.encoding != self.fallback_encoding:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MINOR,
                        KostylCategory.CONTEXT,
                        f"Проблема с кодировкой {self.encoding}, пробуем {self.fallback_encoding}"
                    )
                    self.encoding = self.fallback_encoding
                    continue
                raise
            
            except PermissionError:
                _kostyl_state.record_kostyl(
                    KostylSeverity.CRITICAL,
                    KostylCategory.CONTEXT,
                    f"Нет прав на доступ к {self.filepath}",
                    was_successful=False
                )
                self._file = io.StringIO()
                return self._file
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.NUCLEAR,
                        KostylCategory.CONTEXT,
                        f"Не удалось открыть {self.filepath}: {e}",
                        was_successful=False
                    )
                    self._file = io.StringIO()
                    return self._file
                time.sleep(0.1 * (attempt + 1))
        
        return self._file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает файл с проверками."""
        if self._file and hasattr(self._file, 'close'):
            try:
                # Сбрасываем на диск если есть буфер
                if hasattr(self._file, 'flush'):
                    self._file.flush()
                self._file.close()
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.CONTEXT,
                    f"Файл закрыт: {self.filepath}"
                )
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.CONTEXT,
                    f"Ошибка при закрытии файла {self.filepath}: {e}"
                )
        
        self._free_all_resources()
        
        # Восстанавливаем из бекапа если была ошибка
        if exc_type and self._backup_path and os.path.exists(self._backup_path):
            try:
                import shutil
                shutil.copy2(self._backup_path, self.filepath)
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.CONTEXT,
                    f"Восстановлен из бекапа: {self.filepath}"
                )
            except:
                pass
        
        return False  # Не подавляем исключения

# ═══════════════════════════════════════════════════════════════
# TimerContext — ЗАМЕР ВРЕМЕНИ С КОСТЫЛЯМИ
# ═══════════════════════════════════════════════════════════════

class TimerContext(BaseKostylContext):
    """
    Контекстный менеджер для замера времени.
    Замеряет время, даже если блок упал.
    
    Использование:
        with TimerContext("моя операция") as timer:
            do_something()
        print(timer.elapsed)
    """
    
    def __init__(
        self,
        name: str = "операция",
        warn_if_slower_than: Optional[float] = None,
        log_start: bool = False,
        log_end: bool = True,
        precision: int = 4
    ):
        super().__init__(name)
        self.warn_if_slower_than = warn_if_slower_than
        self.log_start = log_start
        self.log_end = log_end
        self.precision = precision
        
        self.elapsed: float = 0.0
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._was_error: bool = False
    
    def __enter__(self):
        super().__enter__()
        self._start_time = time.perf_counter()
        
        if self.log_start:
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.CONTEXT,
                f"⏱️ Старт замера: '{self.name}'"
            )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.perf_counter()
        self.elapsed = self._end_time - self._start_time
        self._was_error = exc_type is not None
        
        if self.log_end:
            status = "⚠️ с ошибкой" if self._was_error else "✅ успешно"
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.CONTEXT,
                f"⏱️ '{self.name}': {self.elapsed:.{self.precision}f}с {status}"
            )
        
        if self.warn_if_slower_than and self.elapsed > self.warn_if_slower_than:
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.CONTEXT,
                f"'{self.name}' медленно: {self.elapsed:.{self.precision}f}с "
                f"(порог: {self.warn_if_slower_than}с)"
            )
        
        self._free_all_resources()
        return False  # Не подавляем исключения
    
    @property
    def elapsed_ms(self) -> float:
        """Время в миллисекундах."""
        return self.elapsed * 1000
    
    def __str__(self):
        return f"TimerContext('{self.name}'): {self.elapsed:.{self.precision}f}с"

# ═══════════════════════════════════════════════════════════════
# SuppressWarningsContext — ПОДАВЛЕНИЕ ПРЕДУПРЕЖДЕНИЙ
# ═══════════════════════════════════════════════════════════════

class SuppressWarningsContext(BaseKostylContext):
    """
    Подавляет все предупреждения в блоке.
    Даже те, которые должны были нас спасти.
    """
    
    def __init__(self, name: str = "подавитель предупреждений"):
        super().__init__(name)
        self._original_filters = None
    
    def __enter__(self):
        super().__enter__()
        self._original_filters = warnings.filters[:]
        warnings.filterwarnings('ignore')
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            "Предупреждения подавлены (костыль?)"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._original_filters is not None:
            warnings.filters = self._original_filters
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            "Предупреждения восстановлены"
        )
        self._free_all_resources()
        return False

# ═══════════════════════════════════════════════════════════════
# TempDirectoryContext — ВРЕМЕННАЯ ДИРЕКТОРИЯ
# ═══════════════════════════════════════════════════════════════

class TempDirectoryContext(BaseKostylContext):
    """
    Создаёт временную директорию и удаляет её при выходе.
    Если удалить не получается — ну и ладно.
    """
    
    def __init__(self, prefix: str = "kostyl_", suffix: str = "_tmp"):
        super().__init__(f"temp_dir:{prefix}*{suffix}")
        self.prefix = prefix
        self.suffix = suffix
        self.path: Optional[str] = None
        self._created_files: List[str] = []
    
    def __enter__(self):
        super().__enter__()
        self.path = tempfile.mkdtemp(prefix=self.prefix, suffix=self.suffix)
        self._allocate_resource(self.path, "директория")
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            f"Создана временная директория: {self.path}"
        )
        return self.path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path and os.path.exists(self.path):
            try:
                import shutil
                shutil.rmtree(self.path, ignore_errors=True)
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.CONTEXT,
                    f"Удалена временная директория: {self.path}"
                )
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.CONTEXT,
                    f"Не удалось удалить {self.path}: {e}. Останется как есть."
                )
        
        self._free_all_resources()
        return False

# ═══════════════════════════════════════════════════════════════
# RedirectOutputContext — ПЕРЕХВАТ ВЫВОДА
# ═══════════════════════════════════════════════════════════════

class RedirectOutputContext(BaseKostylContext):
    """
    Перехватывает stdout и stderr.
    Сохраняет всё в буфер, чтобы никто не увидел ошибок.
    """
    
    def __init__(self, name: str = "перехватчик вывода"):
        super().__init__(name)
        self._original_stdout = None
        self._original_stderr = None
        self._stdout_buffer = None
        self._stderr_buffer = None
    
    def __enter__(self):
        super().__enter__()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._stdout_buffer = io.StringIO()
        self._stderr_buffer = io.StringIO()
        sys.stdout = self._stdout_buffer
        sys.stderr = self._stderr_buffer
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            "Вывод перехвачен"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        
        self.stdout_content = self._stdout_buffer.getvalue()
        self.stderr_content = self._stderr_buffer.getvalue()
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            f"Вывод восстановлен (stdout: {len(self.stdout_content)} симв, "
            f"stderr: {len(self.stderr_content)} симв)"
        )
        
        self._free_all_resources()
        return False

# ═══════════════════════════════════════════════════════════════
# kostyl_block — ФУНКЦИЯ-ДЕКОРАТОР ДЛЯ БЫСТРОГО СОЗДАНИЯ
# ═══════════════════════════════════════════════════════════════

@contextmanager
def kostyl_block(
    name: str = "быстрый костыль",
    suppress: bool = True,
    log: bool = False
):
    """
    Быстрый костыльный блок через contextmanager.
    
    Использование:
        with kostyl_block("мой код"):
            risky_operation()
    """
    if log:
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.CONTEXT,
            f"🔧 Вход в быстрый блок: '{name}'"
        )
    
    try:
        yield
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.CONTEXT,
            f"Быстрый блок '{name}': подавлена ошибка {type(e).__name__}: {str(e)[:100]}"
        )
        if not suppress:
            raise
    finally:
        if log:
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.CONTEXT,
                f"🔧 Выход из быстрого блока: '{name}'"
            )

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    'KostylContext',
    'SafeFileContext',
    'TimerContext',
    'SuppressWarningsContext',
    'TempDirectoryContext',
    'RedirectOutputContext',
    'kostyl_block',
    'KostylResource',
    'ContextStats',
    'ContextStatus',
    'BaseKostylContext',
]