"""
Ядро kostylpy.
Собирает всё воедино и заставляет работать.
Если ядро падает — всё падает. Но ядро не падает, оно на костылях.

Содержит:
- KostylPy — главный класс, объединяющий всё
- Глобальная инициализация
- Обработка ошибок ядра
- Системные хуки
- Интеграция всех модулей
- Экспорт публичного API
"""

import sys
import os
import time
import threading
import atexit
import signal
import builtins
import functools
import traceback
import warnings
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════
# ИМПОРТ ВСЕХ МОДУЛЕЙ (С ЗАЩИТОЙ ОТ ОШИБОК)
# ═══════════════════════════════════════════════════════════════

def _safe_import(module_name: str, package: str = None) -> Optional[Any]:
    """Безопасно импортирует модуль."""
    try:
        return __import__(module_name, fromlist=['*'])
    except Exception as e:
        print(f"⚠️ kostylpy: не удалось загрузить модуль '{module_name}': {e}", file=sys.stderr)
        return None

# Импортируем константы (должны быть всегда)
from . import constants
from .constants import (
    KOSTYLPY_VERSION, KOSTYLPY_CODENAME,
    PANIC_THRESHOLD, Emoji, Colors,
    DEFAULT_CONFIG
)

# Импортируем остальные модули
_config_module = _safe_import('.config', 'kostylpy')
_logging_module = _safe_import('.logging_kostyl', 'kostylpy')
_metrics_module = _safe_import('.metrics', 'kostylpy')
_exceptions_module = _safe_import('.exceptions', 'kostylpy')
_utils_module = _safe_import('.utils', 'kostylpy')
_decorators_module = _safe_import('.decorators', 'kostylpy')
_context_managers_module = _safe_import('.context_managers', 'kostylpy')
_factories_module = _safe_import('.factories', 'kostylpy')
_validators_module = _safe_import('.validators', 'kostylpy')
_interceptors_module = _safe_import('.interceptors', 'kostylpy')
_async_module = _safe_import('.async_kostyl', 'kostylpy')
_patcher_module = _safe_import('.patcher', 'kostylpy')
_patterns_module = _safe_import('.patterns', 'kostylpy')
_monkey_module = _safe_import('.monkey_patcher', 'kostylpy')

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНОЕ СОСТОЯНИЕ ЯДРА
# ═══════════════════════════════════════════════════════════════

class CoreStatus:
    """Статус ядра."""
    UNINITIALIZED = "не инициализировано"
    INITIALIZING = "инициализируется"
    ACTIVE = "активно"
    DEGRADED = "деградировано (часть модулей не загружена)"
    PANIC = "паника!"
    SHUTTING_DOWN = "завершается"
    DEAD = "мертво"

@dataclass
class CoreStats:
    """Статистика ядра."""
    startup_time: float = 0.0
    modules_loaded: int = 0
    modules_failed: int = 0
    total_crutches: int = 0
    total_errors_caught: int = 0
    uptime: float = 0.0
    status: str = CoreStatus.UNINITIALIZED

# Импортируем dataclass если ещё нет
try:
    from dataclasses import dataclass
except ImportError:
    def dataclass(cls):
        return cls

# ═══════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС
# ═══════════════════════════════════════════════════════════════

class KostylPy:
    """
    Главный класс kostylpy.
    Синглтон. Потому что два ядра — это уже мультивселенная.
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
        
        self._start_time = time.time()
        self._initialized = False
        self._modules: Dict[str, Any] = {}
        self._hooks: List[Callable] = []
        self._patched_builtins: List[str] = []
        self._status = CoreStatus.UNINITIALIZED
        self._panic_mode = False
        self._crutch_counter = 0
        self._error_counter = 0
        
        # Инициализируем
        self._initialize()
    
    # ═══════════════════════════════════════════
    # ИНИЦИАЛИЗАЦИЯ
    # ═══════════════════════════════════════════
    
    def _initialize(self):
        """Инициализирует ядро и все модули."""
        self._status = CoreStatus.INITIALIZING
        
        modules_loaded = 0
        modules_failed = 0
        
        # Список модулей для загрузки
        module_list = [
            ('config', _config_module, 'config'),
            ('logger', _logging_module, 'logger'),
            ('metrics', _metrics_module, 'metrics'),
            ('utils', _utils_module, None),
            ('decorators', _decorators_module, None),
            ('context_managers', _context_managers_module, None),
            ('exceptions', _exceptions_module, None),
            ('factories', _factories_module, None),
            ('validators', _validators_module, None),
            ('interceptors', _interceptors_module, None),
            ('async_kostyl', _async_module, None),
            ('patcher', _patcher_module, None),
            ('patterns', _patterns_module, 'patterns'),
            ('monkey_patcher', _monkey_module, 'monkey'),
        ]
        
        for name, module, global_name in module_list:
            if module is not None:
                self._modules[name] = module
                modules_loaded += 1
                
                # Сохраняем глобальный объект если есть
                if global_name and hasattr(module, global_name):
                    self._modules[global_name] = getattr(module, global_name)
            else:
                modules_failed += 1
        
        # Применяем патчи builtins
        self._patch_builtins()
        
        # Регистрируем обработчики
        self._register_signal_handlers()
        self._register_atexit_handler()
        self._register_exception_hook()
        
        # Определяем статус
        if modules_failed > 0:
            self._status = CoreStatus.DEGRADED
        else:
            self._status = CoreStatus.ACTIVE
        
        self._initialized = True
        
        # Логируем запуск
        self._log_startup(modules_loaded, modules_failed)
    
    def _patch_builtins(self):
        """Патчит встроенные функции."""
        original_print = builtins.print
        original_open = builtins.open
        original_import = builtins.__import__
        
        # Патчим print
        def safe_print(*args, **kwargs):
            try:
                return original_print(*args, **kwargs)
            except Exception as e:
                original_print(f"{Emoji.ERROR} kostylpy: print failed: {e}", file=sys.stderr)
        
        # Патчим open
        def safe_open(file, mode='r', *args, **kwargs):
            try:
                return original_open(file, mode, *args, **kwargs)
            except FileNotFoundError:
                import io
                original_print(f"{Emoji.WARNING} kostylpy: файл не найден, создана заглушка: {file}")
                return io.StringIO("" if 'r' in mode else None)
            except Exception as e:
                import io
                original_print(f"{Emoji.ERROR} kostylpy: open failed: {e}")
                return io.StringIO("")
        
        # Применяем
        builtins.print = safe_print
        builtins.open = safe_open
        
        self._patched_builtins = ['print', 'open']
    
    def _register_signal_handlers(self):
        """Регистрирует обработчики сигналов."""
        def signal_handler(signum, frame):
            sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
            
            if self._status == CoreStatus.PANIC:
                # Уже паникуем — сдаёмся
                print(f"\n{Emoji.ERROR} KOSTYLPY: повторный сигнал {sig_name}")
                print(f"{Emoji.KOSTYL} Костыли не выдержали. Завершаемся.")
                sys.exit(1)
            
            if self._panic_mode:
                # Второй сигнал — точно выходим
                print(f"\n{Emoji.ERROR} KOSTYLPY: сигнал {sig_name} в режиме паники")
                print(f"{Emoji.KOSTYL} Выходим, но мы ещё вернёмся!")
                sys.exit(0)
            
            # Первый сигнал — держимся
            self._panic_mode = True
            self._status = CoreStatus.PANIC
            
            print(f"\n{Emoji.ERROR} KOSTYLPY: получен сигнал {sig_name}")
            print(f"{Emoji.KOSTYL} Но мы держимся на костылях!")
            print(f"{Emoji.KOSTYL} Нажмите ещё раз для выхода.")
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except:
            pass  # Не на всех платформах работает
    
    def _register_atexit_handler(self):
        """Регистрирует обработчик завершения."""
        @atexit.register
        def atexit_handler():
            self._status = CoreStatus.SHUTTING_DOWN
            
            try:
                # Сохраняем метрики
                if 'metrics' in self._modules:
                    self._modules['metrics'].export_json()
                
                # Сохраняем конфиг
                if 'config' in self._modules and hasattr(self._modules['config'], 'save'):
                    self._modules['config'].save()
                
                # Выводим отчёт
                print(self.report())
                
            except Exception:
                pass  # При завершении уже всё равно
    
    def _register_exception_hook(self):
        """Регистрирует глобальный обработчик исключений."""
        original_hook = sys.excepthook
        
        def kostyl_excepthook(exc_type, exc_value, exc_tb):
            self._error_counter += 1
            
            # Логируем
            if 'logger' in self._modules:
                try:
                    logger = self._modules['logger']
                    logger.error(
                        f"Необработанное исключение: {exc_type.__name__}: {exc_value}"
                    )
                except:
                    pass
            
            # Записываем метрики
            if 'metrics' in self._modules:
                try:
                    self._modules['metrics'].crashes.record_crash(exc_type.__name__)
                except:
                    pass
            
            # Если паника — выводим специальное сообщение
            if self._panic_mode:
                print(f"\n{Emoji.ERROR} KOSTYLPY: исключение в режиме паники!")
                print(f"{Emoji.KOSTYL} Тип: {exc_type.__name__}")
                print(f"{Emoji.KOSTYL} Сообщение: {exc_value}")
                print(f"{Emoji.KOSTYL} Но мы продолжаем работать!\n")
                return  # Не падаем в режиме паники
            
            # Иначе — стандартная обработка
            original_hook(exc_type, exc_value, exc_tb)
        
        sys.excepthook = kostyl_excepthook
    
    def _log_startup(self, loaded: int, failed: int):
        """Логирует запуск ядра."""
        banner = constants.get_kostylpy_banner()
        print(banner)
        print(f"   Модулей загружено: {loaded}")
        if failed > 0:
            print(f"   {Colors.YELLOW}Модулей не загружено: {failed}{Colors.RESET}")
        print(f"   Статус: {self._status}")
        print(f"   Время запуска: {time.time() - self._start_time:.3f}с")
        print()
    
    # ═══════════════════════════════════════════
    # ПУБЛИЧНЫЕ МЕТОДЫ
    # ═══════════════════════════════════════════
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def is_active(self) -> bool:
        return self._status in (CoreStatus.ACTIVE, CoreStatus.DEGRADED)
    
    @property
    def is_panic(self) -> bool:
        return self._panic_mode
    
    @property
    def uptime(self) -> float:
        return time.time() - self._start_time
    
    @property
    def config(self):
        """Доступ к конфигурации."""
        if 'config' in self._modules:
            return self._modules['config']
        return None
    
    @property
    def logger(self):
        """Доступ к логгеру."""
        if 'logger' in self._modules:
            return self._modules['logger']
        return None
    
    @property
    def metrics(self):
        """Доступ к метрикам."""
        if 'metrics' in self._modules:
            return self._modules['metrics']
        return None
    
    def get_module(self, name: str) -> Optional[Any]:
        """Получает загруженный модуль."""
        return self._modules.get(name)
    
    def is_module_loaded(self, name: str) -> bool:
        """Проверяет, загружен ли модуль."""
        return name in self._modules
    
    def loaded_modules(self) -> List[str]:
        """Возвращает список загруженных модулей."""
        return list(self._modules.keys())
    
    # ═══════════════════════════════════════════
    # ОТЧЁТЫ
    # ═══════════════════════════════════════════
    
    def report(self) -> str:
        """Генерирует полный отчёт о состоянии."""
        report = f"""
{Emoji.KOSTYL} ═══════════════════════════════════════════════
{Emoji.KOSTYL} KOSTYLPY CORE REPORT
{Emoji.KOSTYL} ═══════════════════════════════════════════════

Версия: {KOSTYLPY_VERSION} ({KOSTYLPY_CODENAME})
Статус: {self._status}
Время работы: {self.uptime:.1f}с
Костылей применено: {self._crutch_counter}
Ошибок перехвачено: {self._error_counter}

Модули ({len(self._modules)}):
"""
        for name in self._modules:
            report += f"  {Emoji.SUCCESS} {name}\n"
        
        # Добавляем отчёты подсистем
        if 'metrics' in self._modules:
            try:
                report += f"\n{self._modules['metrics'].report()}"
            except:
                pass
        
        report += f"\n{Emoji.KOSTYL} ═══════════════════════════════════════════════"
        return report
    
    def stats(self) -> Dict[str, Any]:
        """Возвращает статистику в виде словаря."""
        return {
            'version': KOSTYLPY_VERSION,
            'codename': KOSTYLPY_CODENAME,
            'status': self._status,
            'uptime': self.uptime,
            'crutches': self._crutch_counter,
            'errors_caught': self._error_counter,
            'modules_loaded': list(self._modules.keys()),
            'panic_mode': self._panic_mode,
            'patched_builtins': self._patched_builtins,
        }
    
    def health_check(self) -> Dict[str, bool]:
        """Проверяет здоровье всех систем."""
        return {
            'core': self._status in (CoreStatus.ACTIVE, CoreStatus.DEGRADED),
            'config': 'config' in self._modules,
            'logger': 'logger' in self._modules,
            'metrics': 'metrics' in self._modules,
            'decorators': 'decorators' in self._modules,
            'validators': 'validators' in self._modules,
            'interceptors': 'interceptors' in self._modules,
            'async': 'async_kostyl' in self._modules,
        }

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ═══════════════════════════════════════════════════════════════

# Создаём главный экземпляр
kostylpy = KostylPy()

# Алиасы для удобства
core = kostylpy

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ ПУБЛИЧНОГО API
# ═══════════════════════════════════════════════════════════════

# Экспортируем основные функции из подмодулей
try:
    from .decorators import safe, retry, fallback
except ImportError:
    def safe(func=None, **kwargs):
        return func if func else lambda f: f
    def retry(max_attempts=3, **kwargs):
        return lambda f: f
    def fallback(value=None, **kwargs):
        return lambda f: f

try:
    from .context_managers import KostylContext, kostyl_block
except ImportError:
    class KostylContext:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    def kostyl_block(*a, **kw):
        from contextlib import contextmanager
        @contextmanager
        def dummy():
            yield
        return dummy()

try:
    from .validators import (
        TypeValidator, RangeValidator, StringValidator,
        EmailValidator, ValidationResult
    )
except ImportError:
    TypeValidator = RangeValidator = StringValidator = EmailValidator = None
    ValidationResult = None

try:
    from .utils import (
        safe_get, safe_set, safe_divide, truncate,
        DotDict, SafeList, random_string
    )
except ImportError:
    safe_get = lambda d, k, default=None: default
    safe_set = lambda d, k, v: d
    safe_divide = lambda a, b, default=0: default
    truncate = lambda t, l=80: t[:l]
    DotDict = dict
    SafeList = list
    random_string = lambda l=10: "kostyl"

try:
    from .async_kostyl import (
        async_safe, async_retry, async_timeout,
        AsyncCircuitBreaker, AsyncRateLimiter
    )
except ImportError:
    async_safe = lambda fallback=None: lambda f: f
    async_retry = lambda max_attempts=3: lambda f: f
    async_timeout = lambda s, fallback=None: lambda f: f
    AsyncCircuitBreaker = AsyncRateLimiter = None

# ═══════════════════════════════════════════════════════════════
# ИНФОРМАЦИЯ О СБОРКЕ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Главный объект
    'kostylpy',
    'core',
    'KostylPy',
    
    # Статусы
    'CoreStatus',
    'CoreStats',
    
    # Декораторы
    'safe', 'retry', 'fallback',
    
    # Контекстные менеджеры
    'KostylContext', 'kostyl_block',
    
    # Валидаторы
    'TypeValidator', 'RangeValidator', 'StringValidator',
    'EmailValidator', 'ValidationResult',
    
    # Утилиты
    'safe_get', 'safe_set', 'safe_divide', 'truncate',
    'DotDict', 'SafeList', 'random_string',
    
    # Асинхронные
    'async_safe', 'async_retry', 'async_timeout',
    'AsyncCircuitBreaker', 'AsyncRateLimiter',
    
    # Версия
    'KOSTYLPY_VERSION', 'KOSTYLPY_CODENAME',
    'Emoji', 'Colors',
]

# Финальное сообщение
print(f"{Emoji.SUCCESS} kostylpy core: инициализация завершена")
print(f"{Emoji.KOSTYL} Статус: {kostylpy.status}")
print(f"{Emoji.COFFEE} Готов к работе. Заварите кофе.")