"""
Асинхронные костыли kostylpy.
Потому что даже асинхронный код должен быть на костылях.
Если у вас нет asyncio — мы создадим его заглушку.
Если у вас есть asyncio — мы добавим туда костылей.

Содержит:
- AsyncKostyl — асинхронный костыль
- AsyncSafe — безопасный асинхронный декоратор
- AsyncRetry — повторные попытки для async
- AsyncTimeout — таймаут для корутин
- AsyncFallback — запасной вариант для async
- AsyncCircuitBreaker — защита от лавины ошибок
- AsyncRateLimiter — ограничение частоты вызовов
- AsyncBatch — пакетная обработка
- AsyncQueue — очередь с костылями
- TaskManager — менеджер асинхронных задач
- EventLoopKostyl — костыли для event loop
- FakeAsync — заглушка asyncio если его нет
"""

import sys
import time
import random
import threading
import functools
import inspect
import traceback
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Coroutine
from dataclasses import dataclass, field
from enum import Enum, auto

# Пробуем импортировать asyncio
try:
    import asyncio
    HAS_ASYNCIO = True
except ImportError:
    HAS_ASYNCIO = False

# Импортируем состояние
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
    
    class _FakeCategory(Enum):
        ASYNC = "async"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ЗАГЛУШКА ASYNCIO (если его нет)
# ═══════════════════════════════════════════════════════════════

if not HAS_ASYNCIO:
    _kostyl_state.record_kostyl(
        KostylSeverity.MAJOR,
        KostylCategory.ASYNC,
        "asyncio не найден! Создаём заглушку FakeAsync. Всё будет работать синхронно."
    )
    
    class FakeAsync:
        """Заглушка asyncio. Всё работает синхронно, но делает вид что асинхронно."""
        
        @staticmethod
        def coroutine(func):
            """Делает вид что создаёт корутину."""
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            wrapper._is_coroutine = True
            return wrapper
        
        @staticmethod
        def sleep(seconds):
            time.sleep(seconds)
        
        @staticmethod
        def gather(*coros):
            return [c() if callable(c) else c for c in coros]
        
        @staticmethod
        def run(coro):
            if callable(coro):
                return coro()
            return coro
        
        @staticmethod
        def create_task(coro):
            return coro
        
        class Task:
            def __init__(self, coro):
                self._coro = coro
                self._done = False
                self._result = None
            
            def done(self):
                return True
            
            def result(self):
                if callable(self._coro):
                    self._result = self._coro()
                return self._result
            
            def cancel(self):
                pass
        
        class Queue:
            def __init__(self, maxsize=0):
                self._queue = []
                self.maxsize = maxsize
            
            def put(self, item):
                self._queue.append(item)
            
            def get(self):
                if self._queue:
                    return self._queue.pop(0)
                return None
            
            def empty(self):
                return len(self._queue) == 0
            
            def qsize(self):
                return len(self._queue)
    
    asyncio = FakeAsync()
    
    # Патчим декоратор для async функций
    def _fake_async_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class AsyncStatus(Enum):
    """Статус асинхронной операции."""
    PENDING = "ожидание"
    RUNNING = "выполняется"
    DONE = "завершено"
    FAILED = "провалено"
    RETRYING = "повтор"
    TIMEOUT = "таймаут"
    CANCELLED = "отменено"
    FALLBACK = "запасной вариант"
    ZOMBIE = "зомби"

@dataclass
class AsyncStats:
    """Статистика асинхронных операций."""
    total_calls: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    timed_out: int = 0
    fallback_used: int = 0
    cancelled: int = 0
    total_time: float = 0.0
    errors: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 100.0
        return (self.successful / self.total_calls) * 100
    
    @property
    def average_time(self) -> float:
        if self.successful == 0:
            return 0.0
        return self.total_time / self.successful
    
    def summary(self) -> str:
        return (
            f"Вызовов: {self.total_calls} "
            f"(успешно: {self.successful}, провалено: {self.failed}, "
            f"успешность: {self.success_rate:.1f}%, "
            f"повторов: {self.retried}, таймаутов: {self.timed_out}, "
            f"запасных: {self.fallback_used}, "
            f"среднее время: {self.average_time:.4f}с)"
        )

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНАЯ КОРУТИНА
# ═══════════════════════════════════════════════════════════════

class KostylCoroutine:
    """
    Обёртка над корутиной с костылями.
    Добавляет таймаут, повторные попытки, fallback.
    """
    
    def __init__(
        self,
        coro_func: Callable,
        timeout: Optional[float] = None,
        retries: int = 0,
        retry_delay: float = 0.1,
        fallback_value: Any = None,
        name: str = "костыльная корутина",
    ):
        self.coro_func = coro_func
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.fallback_value = fallback_value
        self.name = name
        self.stats = AsyncStats()
    
    async def execute(self, *args, **kwargs) -> Any:
        """Выполняет корутину с костылями."""
        start_time = time.time()
        self.stats.total_calls += 1
        
        last_error = None
        
        for attempt in range(self.retries + 1):
            try:
                if self.timeout:
                    result = await asyncio.wait_for(
                        self.coro_func(*args, **kwargs),
                        timeout=self.timeout
                    )
                else:
                    result = await self.coro_func(*args, **kwargs)
                
                duration = time.time() - start_time
                self.stats.successful += 1
                self.stats.total_time += duration
                
                if attempt > 0:
                    self.stats.retried += attempt
                
                return result
                
            except asyncio.TimeoutError:
                self.stats.timed_out += 1
                last_error = TimeoutError(f"Таймаут {self.timeout}с")
                
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.ASYNC,
                    f"Корутина '{self.name}': таймаут ({self.timeout}с)"
                )
                
                if attempt < self.retries:
                    await asyncio.sleep(self.retry_delay)
                    
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
                
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.ASYNC,
                    f"Корутина '{self.name}': ошибка {error_type} (попытка {attempt + 1})"
                )
                
                if attempt < self.retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # Все попытки провалились
        self.stats.failed += 1
        self.stats.fallback_used += 1
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.ASYNC,
            f"Корутина '{self.name}': все попытки провалились, "
            f"использован fallback: {self.fallback_value}"
        )
        
        return self.fallback_value

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОРЫ ДЛЯ АСИНХРОННЫХ ФУНКЦИЙ
# ═══════════════════════════════════════════════════════════════

def async_safe(
    fallback: Any = None,
    log_errors: bool = True,
):
    """
    Декоратор для безопасных асинхронных функций.
    Никогда не падает, всегда возвращает fallback при ошибке.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MODERATE,
                        KostylCategory.ASYNC,
                        f"AsyncSafe: '{func.__name__}' упала: {type(e).__name__}: {str(e)[:100]}"
                    )
                return fallback
        
        wrapper._kostyl_async_safe = True
        return wrapper
    
    return decorator

def async_retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: Union[type, Tuple[type, ...]] = Exception,
    fallback: Any = None,
):
    """
    Декоратор для повторных попыток асинхронных функций.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    
                    if attempt < max_attempts - 1:
                        current_delay = delay * (backoff ** attempt)
                        _kostyl_state.record_kostyl(
                            KostylSeverity.MINOR,
                            KostylCategory.ASYNC,
                            f"AsyncRetry: '{func.__name__}' "
                            f"(попытка {attempt + 2}/{max_attempts}) "
                            f"через {current_delay:.3f}с"
                        )
                        await asyncio.sleep(current_delay)
            
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.ASYNC,
                f"AsyncRetry: '{func.__name__}' провалена после {max_attempts} попыток"
            )
            return fallback
        
        wrapper._kostyl_async_retry = True
        return wrapper
    
    return decorator

def async_timeout(seconds: float, fallback: Any = None):
    """
    Декоратор для установки таймаута асинхронной функции.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.ASYNC,
                    f"AsyncTimeout: '{func.__name__}' превысила {seconds}с"
                )
                return fallback
        
        wrapper._kostyl_async_timeout = True
        return wrapper
    
    return decorator

def async_fallback(fallback_value: Any, exceptions: Union[type, Tuple[type, ...]] = Exception):
    """
    Декоратор: при ошибке возвращает запасное значение.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.ASYNC,
                    f"AsyncFallback: '{func.__name__}' → {fallback_value} ({type(e).__name__})"
                )
                return fallback_value
        
        wrapper._kostyl_async_fallback = True
        return wrapper
    
    return decorator

# Комбинированный декоратор
def async_kostyl(
    safe: bool = True,
    retries: int = 3,
    timeout: Optional[float] = None,
    fallback: Any = None,
    delay: float = 0.1,
):
    """
    Ультимативный декоратор для асинхронных функций.
    Объединяет safe, retry, timeout, fallback.
    """
    def decorator(func):
        @functools.wraps(func)
        @async_safe(fallback=fallback)
        @async_retry(max_attempts=retries, delay=delay, fallback=fallback)
        async def wrapper(*args, **kwargs):
            if timeout:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout
                )
            return await func(*args, **kwargs)
        
        wrapper._kostyl_async_kostyl = True
        wrapper._kostyl_meta = {
            'safe': safe,
            'retries': retries,
            'timeout': timeout,
            'fallback': fallback,
        }
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# CIRCUIT BREAKER (ЗАЩИТА ОТ ЛАВИНЫ ОШИБОК)
# ═══════════════════════════════════════════════════════════════

class CircuitState(Enum):
    CLOSED = "замкнут (работает)"
    OPEN = "разомкнут (ошибки)"
    HALF_OPEN = "полуоткрыт (проверка)"

class AsyncCircuitBreaker:
    """
    Автоматический выключатель для асинхронных операций.
    При превышении порога ошибок — отключает функцию на время.
    """
    
    def __init__(
        self,
        name: str = "circuit_breaker",
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        excluded_exceptions: Tuple[type, ...] = (),
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.excluded_exceptions = excluded_exceptions
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.half_open_calls = 0
        self._lock = asyncio.Lock() if HAS_ASYNCIO else threading.Lock()
        
        self.stats = AsyncStats()
    
    async def call(self, coro_func: Callable, *args, **kwargs) -> Any:
        """Вызывает функцию через circuit breaker."""
        
        # Проверяем состояние
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.ASYNC,
                    f"CircuitBreaker '{self.name}': переход в HALF_OPEN"
                )
            else:
                raise RuntimeError(
                    f"CircuitBreaker '{self.name}' разомкнут. "
                    f"Повтор через {self.recovery_timeout - (time.time() - self.last_failure_time):.0f}с"
                )
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls > self.half_open_max_calls:
                raise RuntimeError(
                    f"CircuitBreaker '{self.name}': превышен лимит проверочных вызовов"
                )
        
        try:
            result = await coro_func(*args, **kwargs)
            
            # Успех!
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.success_count += 1
        self.last_success_time = time.time()
        self.state = CircuitState.CLOSED
        self.stats.successful += 1
    
    def _on_failure(self, error: Exception):
        if isinstance(error, self.excluded_exceptions):
            return  # Не считаем исключённые ошибки
        
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.stats.failed += 1
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.ASYNC,
                f"CircuitBreaker '{self.name}': РАЗОМКНУТ! "
                f"({self.failure_count} ошибок подряд)"
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_val:
            self._on_failure(exc_val)
        elif not exc_type:
            self._on_success()
        return False
    
    def reset(self):
        """Сбрасывает состояние."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0

# ═══════════════════════════════════════════════════════════════
# RATE LIMITER (ОГРАНИЧЕНИЕ ЧАСТОТЫ)
# ═══════════════════════════════════════════════════════════════

class AsyncRateLimiter:
    """
    Ограничивает частоту асинхронных вызовов.
    Не больше N вызовов за период времени.
    """
    
    def __init__(
        self,
        max_calls: int = 10,
        period: float = 1.0,
        name: str = "rate_limiter",
    ):
        self.max_calls = max_calls
        self.period = period
        self.name = name
        
        self._calls: List[float] = []
        self._lock = asyncio.Lock() if HAS_ASYNCIO else threading.Lock()
        self.stats = AsyncStats()
    
    async def acquire(self) -> bool:
        """Пытается получить разрешение на вызов."""
        async with self._lock if HAS_ASYNCIO else self._lock:
            now = time.time()
            
            # Удаляем старые вызовы
            self._calls = [t for t in self._calls if now - t < self.period]
            
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                self.stats.successful += 1
                return True
            
            self.stats.failed += 1
            return False
    
    async def wait_and_acquire(self, timeout: float = 30.0) -> bool:
        """Ждёт и получает разрешение."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.acquire():
                return True
            await asyncio.sleep(self.period / self.max_calls)
        
        return False
    
    async def call(self, coro_func: Callable, *args, **kwargs) -> Any:
        """Вызывает функцию с учётом лимита."""
        if await self.wait_and_acquire():
            self.stats.total_calls += 1
            return await coro_func(*args, **kwargs)
        else:
            raise RuntimeError(
                f"RateLimiter '{self.name}': превышен лимит "
                f"({self.max_calls} вызовов за {self.period}с)"
            )
    
    def get_current_rate(self) -> float:
        """Возвращает текущую частоту вызовов."""
        now = time.time()
        recent = [t for t in self._calls if now - t < self.period]
        return len(recent) / self.period

# ═══════════════════════════════════════════════════════════════
# АСИНХРОННАЯ ОЧЕРЕДЬ С КОСТЫЛЯМИ
# ═══════════════════════════════════════════════════════════════

class AsyncKostylQueue:
    """
    Асинхронная очередь с костылями.
    Элементы можно добавлять и забирать.
    При переполнении — старые элементы теряются (или нет).
    """
    
    def __init__(
        self,
        maxsize: int = 100,
        name: str = "костыльная очередь",
        discard_old: bool = True,
    ):
        self.maxsize = maxsize
        self.name = name
        self.discard_old = discard_old
        
        self._queue: List[Any] = []
        self._lock = asyncio.Lock() if HAS_ASYNCIO else threading.Lock()
        self._not_empty = asyncio.Event() if HAS_ASYNCIO else threading.Event()
        self._not_full = asyncio.Event() if HAS_ASYNCIO else threading.Event()
        
        if HAS_ASYNCIO:
            self._not_full.set()
        
        self.stats = AsyncStats()
        self._total_put = 0
        self._total_get = 0
        self._total_discarded = 0
    
    async def put(self, item: Any) -> bool:
        """Добавляет элемент в очередь."""
        async with self._lock if HAS_ASYNCIO else self._lock:
            if len(self._queue) >= self.maxsize:
                if self.discard_old:
                    discarded = self._queue.pop(0)
                    self._total_discarded += 1
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MINOR,
                        KostylCategory.ASYNC,
                        f"Очередь '{self.name}': удалён старый элемент: {str(discarded)[:50]}"
                    )
                else:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MODERATE,
                        KostylCategory.ASYNC,
                        f"Очередь '{self.name}': переполнена! Элемент отброшен."
                    )
                    return False
            
            self._queue.append(item)
            self._total_put += 1
            
            if HAS_ASYNCIO:
                self._not_empty.set()
            
            return True
    
    async def get(self, timeout: Optional[float] = None) -> Any:
        """Забирает элемент из очереди."""
        start_time = time.time()
        
        while True:
            async with self._lock if HAS_ASYNCIO else self._lock:
                if self._queue:
                    item = self._queue.pop(0)
                    self._total_get += 1
                    
                    if HAS_ASYNCIO:
                        self._not_full.set()
                        if not self._queue:
                            self._not_empty.clear()
                    
                    return item
            
            if timeout and time.time() - start_time >= timeout:
                raise asyncio.TimeoutError(
                    f"Очередь '{self.name}': таймаут получения ({timeout}с)"
                )
            
            if HAS_ASYNCIO:
                await asyncio.sleep(0.01)
            else:
                time.sleep(0.01)
    
    @property
    def size(self) -> int:
        return len(self._queue)
    
    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0
    
    @property
    def is_full(self) -> bool:
        return len(self._queue) >= self.maxsize

# ═══════════════════════════════════════════════════════════════
# МЕНЕДЖЕР ЗАДАЧ
# ═══════════════════════════════════════════════════════════════

class TaskManager:
    """
    Менеджер асинхронных задач.
    Создаёт, отслеживает, отменяет задачи.
    """
    
    def __init__(self, name: str = "менеджер задач"):
        self.name = name
        self._tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, Any] = {}
        self._errors: Dict[str, Exception] = {}
        self._lock = asyncio.Lock() if HAS_ASYNCIO else threading.Lock()
        self._counter = 0
    
    def create_task(
        self,
        coro_func: Callable,
        name: Optional[str] = None,
        *args,
        **kwargs
    ) -> str:
        """Создаёт и запускает задачу."""
        task_name = name or f"task_{self._counter}"
        self._counter += 1
        
        async def wrapped():
            try:
                result = await coro_func(*args, **kwargs)
                self._results[task_name] = result
                return result
            except Exception as e:
                self._errors[task_name] = e
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.ASYNC,
                    f"Задача '{task_name}' упала: {type(e).__name__}"
                )
                raise
        
        if HAS_ASYNCIO:
            task = asyncio.create_task(wrapped())
            self._tasks[task_name] = task
        else:
            # Синхронный режим
            task = wrapped
            self._tasks[task_name] = task
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.ASYNC,
            f"Создана задача: '{task_name}'"
        )
        
        return task_name
    
    def get_result(self, task_name: str, default: Any = None) -> Any:
        """Получает результат задачи."""
        return self._results.get(task_name, default)
    
    def get_error(self, task_name: str) -> Optional[Exception]:
        """Получает ошибку задачи."""
        return self._errors.get(task_name)
    
    def cancel_task(self, task_name: str):
        """Отменяет задачу."""
        task = self._tasks.get(task_name)
        if task and HAS_ASYNCIO:
            task.cancel()
        if task_name in self._tasks:
            del self._tasks[task_name]
    
    def cancel_all(self):
        """Отменяет все задачи."""
        for name in list(self._tasks.keys()):
            self.cancel_task(name)
    
    @property
    def active_tasks(self) -> List[str]:
        """Возвращает список активных задач."""
        return list(self._tasks.keys())
    
    @property
    def task_count(self) -> int:
        return len(self._tasks)
    
    def status_report(self) -> str:
        """Генерирует отчёт о состоянии задач."""
        report = f"📋 Менеджер задач '{self.name}':\n"
        report += f"   Активных задач: {self.task_count}\n"
        report += f"   Завершённых: {len(self._results)}\n"
        report += f"   С ошибками: {len(self._errors)}\n"
        
        if self._tasks:
            report += "   Активные задачи:\n"
            for name in self._tasks:
                report += f"     • {name}\n"
        
        if self._errors:
            report += "   Ошибки:\n"
            for name, error in list(self._errors.items())[:5]:
                report += f"     • {name}: {type(error).__name__}\n"
        
        return report

# ═══════════════════════════════════════════════════════════════
# BATCH PROCESSOR (ПАКЕТНАЯ ОБРАБОТКА)
# ═══════════════════════════════════════════════════════════════

class AsyncBatchProcessor:
    """
    Накапливает элементы и обрабатывает их пакетами.
    """
    
    def __init__(
        self,
        batch_size: int = 10,
        max_wait: float = 1.0,
        name: str = "пакетный обработчик",
    ):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.name = name
        
        self._batch: List[Any] = []
        self._lock = asyncio.Lock() if HAS_ASYNCIO else threading.Lock()
        self._last_flush = time.time()
    
    async def add(self, item: Any) -> Optional[List[Any]]:
        """Добавляет элемент. Возвращает пакет если накопилось."""
        async with self._lock if HAS_ASYNCIO else self._lock:
            self._batch.append(item)
            
            should_flush = (
                len(self._batch) >= self.batch_size or
                (time.time() - self._last_flush) >= self.max_wait
            )
            
            if should_flush:
                batch = self._batch.copy()
                self._batch.clear()
                self._last_flush = time.time()
                return batch
        
        return None
    
    async def flush(self) -> List[Any]:
        """Принудительно возвращает накопленный пакет."""
        async with self._lock if HAS_ASYNCIO else self._lock:
            batch = self._batch.copy()
            self._batch.clear()
            self._last_flush = time.time()
            return batch
    
    @property
    def pending_count(self) -> int:
        return len(self._batch)

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

async def gather_safe(
    *coros,
    return_exceptions: bool = True,
    fallback: Any = None,
) -> List[Any]:
    """
    Безопасная версия asyncio.gather.
    Никогда не падает, возвращает fallback для упавших корутин.
    """
    results = []
    
    for coro in coros:
        try:
            result = await coro
            results.append(result)
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.MINOR,
                KostylCategory.ASYNC,
                f"gather_safe: корутина упала: {type(e).__name__}"
            )
            if return_exceptions:
                results.append(e)
            else:
                results.append(fallback)
    
    return results

async def run_with_timeout(
    coro_func: Callable,
    timeout: float,
    fallback: Any = None,
) -> Any:
    """Запускает корутину с таймаутом."""
    try:
        return await asyncio.wait_for(coro_func(), timeout=timeout)
    except asyncio.TimeoutError:
        return fallback

async def retry_until_success(
    coro_func: Callable,
    max_attempts: int = 10,
    delay: float = 1.0,
    success_test: Optional[Callable[[Any], bool]] = None,
) -> Any:
    """Повторяет корутину пока не будет успех."""
    for attempt in range(max_attempts):
        try:
            result = await coro_func()
            if success_test is None or success_test(result):
                return result
        except Exception:
            pass
        
        if attempt < max_attempts - 1:
            await asyncio.sleep(delay)
    
    raise RuntimeError(f"Не удалось добиться успеха за {max_attempts} попыток")

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Заглушка
    'FakeAsync',
    'HAS_ASYNCIO',
    
    # Базовые классы
    'KostylCoroutine',
    'AsyncStats',
    'AsyncStatus',
    'CircuitState',
    
    # Декораторы
    'async_safe',
    'async_retry',
    'async_timeout',
    'async_fallback',
    'async_kostyl',
    
    # Утилиты
    'AsyncCircuitBreaker',
    'AsyncRateLimiter',
    'AsyncKostylQueue',
    'TaskManager',
    'AsyncBatchProcessor',
    
    # Функции
    'gather_safe',
    'run_with_timeout',
    'retry_until_success',
]

status = "✅ (asyncio доступен)" if HAS_ASYNCIO else "⚠️ (режим заглушки FakeAsync)"
print(f"🔄 kostylpy.async_kostyl: загружен {status}")
print(f"   Декораторы: async_safe, async_retry, async_timeout, async_fallback, async_kostyl")
print(f"   Утилиты: CircuitBreaker, RateLimiter, Queue, TaskManager, BatchProcessor")