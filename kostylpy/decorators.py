"""
Декораторы kostylpy.
Каждый декоратор — это маленький шедевр костыльной инженерии.
Содержит больше костылей, чем строк кода.
Если декоратор падает — он применяет сам себя.
"""

import functools
import time
import random
import threading
import traceback
import inspect
import sys
import warnings
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем состояние (с защитой от циклического импорта)
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    # Если не можем импортировать — создаём локальное состояние
    class _FakeSeverity(Enum):
        COSMETIC = "COSMETIC"
        MINOR = "MINOR"
        MODERATE = "MODERATE"
        MAJOR = "MAJOR"
        CRITICAL = "CRITICAL"
        NUCLEAR = "NUCLEAR"
    
    class _FakeCategory(Enum):
        DECORATOR = "decorator"
        UNKNOWN = "unknown"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ДЕКОРАТОРОВ
# ═══════════════════════════════════════════════════════════════

# Счётчик вызовов (глобальный, потому что глобальные переменные — это костыль)
_global_call_counter = 0
_global_call_lock = threading.Lock()

def _increment_call_counter() -> int:
    """Увеличивает глобальный счётчик вызовов. Потокобезопасно (на костылях)."""
    global _global_call_counter
    with _global_call_lock:
        _global_call_counter += 1
        return _global_call_counter

def _get_caller_info() -> Dict[str, Any]:
    """
    Получает информацию о вызывающем коде.
    Проходит по стеку вызовов, игнорируя самого себя.
    """
    info = {
        'file': 'unknown',
        'line': 0,
        'function': 'unknown',
        'code_context': 'unknown',
        'timestamp': time.time(),
        'thread_id': threading.get_ident(),
        'thread_name': threading.current_thread().name,
    }
    
    try:
        frame = inspect.currentframe()
        # Пропускаем фреймы kostylpy
        for _ in range(10):  # Не больше 10, чтобы не зациклиться
            if frame is None:
                break
            if 'kostylpy' not in frame.f_code.co_filename:
                info['file'] = frame.f_code.co_filename
                info['line'] = frame.f_lineno
                info['function'] = frame.f_code.co_name
                if frame.f_code.co_name != '<module>':
                    try:
                        lines, _ = inspect.getsourcelines(frame)
                        if lines:
                            info['code_context'] = lines[0].strip()
                    except:
                        pass
                break
            frame = frame.f_back
    except Exception as e:
        # Если не получилось — и ладно, костыль же
        info['error'] = str(e)
    
    return info

def _safe_get_function_name(func: Callable) -> str:
    """Безопасно получает имя функции."""
    try:
        return func.__name__
    except AttributeError:
        try:
            return func.__class__.__name__
        except:
            return str(func)[:50]

def _safe_get_docstring(func: Callable) -> str:
    """Безопасно получает документацию функции."""
    try:
        doc = func.__doc__
        if doc:
            return doc.strip().split('\n')[0][:100]
    except:
        pass
    return "Нет документации (костыль?)"

# ═══════════════════════════════════════════════════════════════
# КЛАСС ДЛЯ ХРАНЕНИЯ СТАТИСТИКИ ДЕКОРАТОРА
# ═══════════════════════════════════════════════════════════════

@dataclass
class DecoratorStats:
    """Статистика работы декоратора. Да, у декоратора есть статистика."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    retry_attempts: int = 0
    fallbacks_used: int = 0
    total_time: float = 0.0
    errors: Dict[str, int] = field(default_factory=dict)
    last_error: Optional[str] = None
    last_call_time: float = 0.0
    
    def record_success(self, duration: float):
        self.total_calls += 1
        self.successful_calls += 1
        self.total_time += duration
        self.last_call_time = duration
    
    def record_failure(self, error_type: str):
        self.total_calls += 1
        self.failed_calls += 1
        self.errors[error_type] = self.errors.get(error_type, 0) + 1
        self.last_error = error_type
    
    def record_retry(self):
        self.retry_attempts += 1
    
    def record_fallback(self):
        self.fallbacks_used += 1
    
    def get_success_rate(self) -> float:
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100
    
    def get_average_time(self) -> float:
        if self.successful_calls == 0:
            return 0.0
        return self.total_time / self.successful_calls
    
    def summary(self) -> str:
        return (
            f"Вызовов: {self.total_calls} "
            f"(успешно: {self.successful_calls}, "
            f"провалено: {self.failed_calls}, "
            f"успешность: {self.get_success_rate():.1f}%, "
            f"повторов: {self.retry_attempts}, "
            f"запасных: {self.fallbacks_used}, "
            f"среднее время: {self.get_average_time():.4f}с)"
        )

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР safe
# ═══════════════════════════════════════════════════════════════

# Словарь для хранения статистики по функциям
# Глобальный словарь — потому что так проще (костыль!)
_safe_stats: Dict[int, DecoratorStats] = {}
_safe_stats_lock = threading.Lock()

def safe(func: Optional[Callable] = None, *, 
         default: Any = None,
         log_errors: bool = True,
         reraise: Union[bool, List[type]] = False,
         on_error: Optional[Callable] = None,
         max_failures: int = -1,
         cooldown_after_failures: int = 0):
    """
    Декоратор, который делает функцию абсолютно безопасной.
    Она никогда не упадёт. Никогда. Серьёзно.
    
    Args:
        func: Декорируемая функция
        default: Значение по умолчанию при ошибке
        log_errors: Логировать ли ошибки
        reraise: Пробрасывать ли исключения (False, True, или список типов)
        on_error: Функция, вызываемая при ошибке
        max_failures: Максимальное количество ошибок перед паникой (-1 = бесконечно)
        cooldown_after_failures: Задержка после N ошибок
    
    Returns:
        Безопасная версия функции, обмотанная костылями
    """
    
    # Поддержка использования без скобок: @safe
    if func is not None and callable(func):
        return _safe_decorator_impl(
            func, default, log_errors, reraise, on_error, 
            max_failures, cooldown_after_failures
        )
    
    # Поддержка использования со скобками: @safe(default=None)
    def decorator(f):
        return _safe_decorator_impl(
            f, default, log_errors, reraise, on_error,
            max_failures, cooldown_after_failures
        )
    return decorator

def _safe_decorator_impl(
    func: Callable,
    default: Any,
    log_errors: bool,
    reraise: Union[bool, List[type]],
    on_error: Optional[Callable],
    max_failures: int,
    cooldown_after_failures: int
) -> Callable:
    """
    Реализация декоратора safe.
    Тут происходит вся магия (костыльная).
    """
    
    func_name = _safe_get_function_name(func)
    func_doc = _safe_get_docstring(func)
    func_id = id(func)
    
    # Инициализируем статистику
    with _safe_stats_lock:
        if func_id not in _safe_stats:
            _safe_stats[func_id] = DecoratorStats()
    
    stats = _safe_stats[func_id]
    
    # Счётчик последовательных ошибок
    consecutive_failures = [0]  # Список для мутабельности в замыкании
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        call_id = _increment_call_counter()
        caller_info = _get_caller_info()
        start_time = time.time()
        
        # Проверка на cooldown
        if cooldown_after_failures > 0 and consecutive_failures[0] >= cooldown_after_failures:
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.DECORATOR,
                f"Cooldown для функции '{func_name}' после {consecutive_failures[0]} ошибок"
            )
            time.sleep(0.1 * consecutive_failures[0])
            consecutive_failures[0] = 0
        
        try:
            # Пробуем выполнить функцию
            result = func(*args, **kwargs)
            
            # Успех!
            duration = time.time() - start_time
            stats.record_success(duration)
            consecutive_failures[0] = 0
            
            return result
            
        except Exception as e:
            # Ошибка! Начинаем костылизацию
            duration = time.time() - start_time
            stats.record_failure(type(e).__name__)
            consecutive_failures[0] += 1
            
            # Проверяем, не пора ли panic
            if 0 < max_failures <= stats.failed_calls:
                _kostyl_state.record_kostyl(
                    KostylSeverity.APOCALYPTIC,
                    KostylCategory.DECORATOR,
                    f"Функция '{func_name}' превысила лимит ошибок ({max_failures})!",
                    was_successful=False
                )
                raise  # Всё, сдаёмся
            
            # Логируем
            if log_errors:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.DECORATOR,
                    f"Функция '{func_name}' упала: {error_msg}"
                )
            
            # Вызываем on_error если есть
            if on_error is not None:
                try:
                    on_error(e, args, kwargs, caller_info)
                except Exception as on_error_error:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MAJOR,
                        KostylCategory.DECORATOR,
                        f"Обработчик ошибок для '{func_name}' тоже упал: {on_error_error}"
                    )
            
            # Проверяем, нужно ли пробрасывать
            should_reraise = False
            if reraise is True:
                should_reraise = True
            elif isinstance(reraise, (list, tuple)):
                should_reraise = any(isinstance(e, t) for t in reraise)
            
            if should_reraise:
                raise
            
            # Возвращаем default
            stats.record_fallback()
            _kostyl_state.record_kostyl(
                KostylSeverity.MINOR,
                KostylCategory.DECORATOR,
                f"Функция '{func_name}' → fallback: {default}"
            )
            return default
    
    # Прикрепляем статистику и метаданные к обёртке
    wrapper._kostyl_safe = True
    wrapper._kostyl_stats = stats
    wrapper._kostyl_original = func
    wrapper._kostyl_func_name = func_name
    
    # Добавляем метод для получения статистики
    def get_stats():
        return stats.summary()
    wrapper.get_stats = get_stats
    
    # Добавляем метод сброса статистики
    def reset_stats():
        nonlocal stats
        with _safe_stats_lock:
            stats = DecoratorStats()
            _safe_stats[func_id] = stats
        consecutive_failures[0] = 0
    wrapper.reset_stats = reset_stats
    
    return wrapper

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР retry
# ═══════════════════════════════════════════════════════════════

_retry_stats: Dict[int, DecoratorStats] = {}
_retry_stats_lock = threading.Lock()

def retry(
    max_attempts: int = 3,
    delay: Union[float, Tuple[float, float]] = 0.1,
    backoff: float = 2.0,
    exceptions: Union[type, Tuple[type, ...]] = Exception,
    on_retry: Optional[Callable] = None,
    fallback: Any = None,
    jitter: bool = True
):
    """
    Декоратор для повторных попыток выполнения функции.
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками (или кортеж (min, max))
        backoff: Множитель задержки (экспоненциальный backoff)
        exceptions: Какие исключения ловить
        on_retry: Функция, вызываемая перед каждой повторной попыткой
        fallback: Значение, если все попытки провалились
        jitter: Добавлять ли случайную дрожь к задержке
    
    Returns:
        Функция, которая будет пытаться, пока не получится
    """
    
    def decorator(func):
        func_name = _safe_get_function_name(func)
        func_id = id(func)
        
        with _retry_stats_lock:
            if func_id not in _retry_stats:
                _retry_stats[func_id] = DecoratorStats()
        stats = _retry_stats[func_id]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    if attempt > 0:
                        stats.record_retry()
                    stats.record_success(duration)
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    attempt_num = attempt + 1
                    
                    if attempt < max_attempts - 1:
                        # Вычисляем задержку
                        if isinstance(delay, (tuple, list)):
                            current_delay = random.uniform(delay[0], delay[1])
                        else:
                            current_delay = delay * (backoff ** attempt)
                        
                        if jitter:
                            current_delay *= random.uniform(0.5, 1.5)
                        
                        _kostyl_state.record_kostyl(
                            KostylSeverity.MINOR,
                            KostylCategory.DECORATOR,
                            f"Повтор '{func_name}' (попытка {attempt_num}/{max_attempts}) "
                            f"через {current_delay:.3f}с: {type(e).__name__}"
                        )
                        
                        if on_retry:
                            try:
                                on_retry(attempt_num, e, current_delay)
                            except:
                                pass
                        
                        time.sleep(current_delay)
                    else:
                        stats.record_failure(type(e).__name__)
            
            # Все попытки провалились
            stats.record_fallback()
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.DECORATOR,
                f"Функция '{func_name}' не смогла после {max_attempts} попыток. "
                f"Последняя ошибка: {type(last_exception).__name__}: {str(last_exception)[:100]}"
            )
            
            return fallback
        
        # Прикрепляем метаданные
        wrapper._kostyl_retry = True
        wrapper._kostyl_stats = stats
        wrapper._kostyl_original = func
        wrapper._kostyl_max_attempts = max_attempts
        
        def get_stats():
            return stats.summary()
        wrapper.get_stats = get_stats
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР fallback
# ═══════════════════════════════════════════════════════════════

def fallback(fallback_value: Any = None, *, 
             exceptions: Union[type, Tuple[type, ...]] = Exception,
             log: bool = True):
    """
    Декоратор, который при ошибке возвращает запасное значение.
    
    Args:
        fallback_value: Что возвращать при ошибке
        exceptions: Какие исключения ловить
        log: Логировать ли ошибки
    
    Returns:
        Функция, которая всегда что-то возвращает
    """
    
    def decorator(func):
        func_name = _safe_get_function_name(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MINOR,
                        KostylCategory.DECORATOR,
                        f"Fallback для '{func_name}': {type(e).__name__} → {fallback_value}"
                    )
                return fallback_value
        
        wrapper._kostyl_fallback = True
        wrapper._kostyl_fallback_value = fallback_value
        wrapper._kostyl_original = func
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР kostyl_method
# ═══════════════════════════════════════════════════════════════

def kostyl_method(
    safe_mode: bool = True,
    retry_mode: bool = True,
    max_attempts: int = 2,
    fallback_value: Any = None,
    log_calls: bool = False,
    measure_time: bool = True,
    cache_results: bool = False
):
    """
    Ультимативный декоратор для методов.
    Комбинирует safe, retry, fallback и ещё кучу всего.
    
    Args:
        safe_mode: Включить безопасный режим
        retry_mode: Включить повторные попытки
        max_attempts: Максимум попыток
        fallback_value: Значение при полном провале
        log_calls: Логировать каждый вызов
        measure_time: Измерять время выполнения
        cache_results: Кешировать результаты (почему бы и нет?)
    
    Returns:
        Метод, обмотанный всеми костылями сразу
    """
    
    def decorator(func):
        func_name = _safe_get_function_name(func)
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Кеширование
            if cache_results:
                try:
                    cache_key = (args, tuple(sorted(kwargs.items())))
                    if cache_key in cache:
                        return cache[cache_key]
                except:
                    pass  # Не всё можно закешировать
            
            if log_calls:
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.DECORATOR,
                    f"Вызов метода '{func_name}'"
                )
            
            # Объединяем все режимы
            attempts = max_attempts if retry_mode else 1
            last_error = None
            
            for attempt in range(attempts):
                try:
                    if measure_time:
                        start = time.time()
                        result = func(*args, **kwargs)
                        duration = time.time() - start
                        
                        if duration > 1.0:
                            _kostyl_state.record_kostyl(
                                KostylSeverity.COSMETIC,
                                KostylCategory.DECORATOR,
                                f"Метод '{func_name}' выполнялся {duration:.2f}с (подозрительно долго)"
                            )
                    else:
                        result = func(*args, **kwargs)
                    
                    # Кешируем результат
                    if cache_results:
                        try:
                            cache[cache_key] = result
                        except:
                            pass
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    
                    if attempt < attempts - 1:
                        _kostyl_state.record_kostyl(
                            KostylSeverity.MINOR,
                            KostylCategory.DECORATOR,
                            f"Повтор метода '{func_name}' ({attempt + 2}/{attempts})"
                        )
                        time.sleep(0.05 * (attempt + 1))
            
            # Все попытки провалились
            if safe_mode:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.DECORATOR,
                    f"Метод '{func_name}' → safe fallback после {attempts} попыток"
                )
                return fallback_value
            else:
                raise last_error
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР cached (костыльное кеширование)
# ═══════════════════════════════════════════════════════════════

def cached(max_size: int = 128, ttl: float = 0):
    """
    Кеширующий декоратор.
    Кеш хранится в оперативной памяти и никогда не чистится сам.
    
    Args:
        max_size: Максимальный размер кеша (после превышения — очистка всего)
        ttl: Время жизни записи в секундах (0 = вечно)
    """
    
    def decorator(func):
        cache: Dict[Any, Tuple[Any, float]] = {}
        cache_lock = threading.Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Создаём ключ
            try:
                key = (args, tuple(sorted(kwargs.items())))
            except TypeError:
                # Если аргументы не хешируются — не кешируем
                return func(*args, **kwargs)
            
            with cache_lock:
                # Проверяем кеш
                if key in cache:
                    result, timestamp = cache[key]
                    if ttl == 0 or (time.time() - timestamp) < ttl:
                        return result
                    else:
                        del cache[key]
                
                # Очищаем кеш если переполнен
                if len(cache) >= max_size:
                    cache.clear()
                    _kostyl_state.record_kostyl(
                        KostylSeverity.COSMETIC,
                        KostylCategory.DECORATOR,
                        f"Кеш функции '{_safe_get_function_name(func)}' очищен (превышен размер {max_size})"
                    )
                
                # Вычисляем и кешируем
                result = func(*args, **kwargs)
                cache[key] = (result, time.time())
                return result
        
        def clear_cache():
            with cache_lock:
                cache.clear()
        
        def cache_info():
            with cache_lock:
                return f"Кеш: {len(cache)}/{max_size} записей"
        
        wrapper._kostyl_cached = True
        wrapper.clear_cache = clear_cache
        wrapper.cache_info = cache_info
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР deprecated_kostyl
# ═══════════════════════════════════════════════════════════════

def deprecated_kostyl(reason: str = "Потому что костыль устарел", 
                      alternative: str = "новый костыль"):
    """
    Декоратор для пометки устаревших костылей.
    Выводит предупреждение при использовании.
    """
    
    def decorator(func):
        func_name = _safe_get_function_name(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"🦿 Функция '{func_name}' устарела: {reason}. "
                f"Используйте {alternative}.",
                DeprecationWarning,
                stacklevel=2
            )
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.DECORATOR,
                f"Вызов устаревшей функции '{func_name}': {reason}"
            )
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР monkey_patch
# ═══════════════════════════════════════════════════════════════

def monkey_patch(target_class, method_name: Optional[str] = None):
    """
    Декоратор для monkey-patching'а.
    Потому что нормальный inheritance — это скучно.
    
    Args:
        target_class: Класс, который патчим
        method_name: Имя метода (если None, берётся из функции)
    """
    
    def decorator(func):
        nonlocal method_name
        if method_name is None:
            method_name = func.__name__
        
        original = getattr(target_class, method_name, None)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._kostyl_monkey_patch = True
        wrapper._kostyl_original = original
        wrapper._kostyl_target = target_class
        
        setattr(target_class, method_name, wrapper)
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.DECORATOR,
            f"Monkey-patch: {target_class.__name__}.{method_name} заменён"
        )
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР log_execution
# ═══════════════════════════════════════════════════════════════

def log_execution(level: str = "DEBUG", 
                  log_args: bool = True,
                  log_result: bool = False,
                  log_time: bool = True):
    """
    Декоратор для логирования выполнения функции.
    Пишет кучу бесполезной информации.
    """
    
    def decorator(func):
        func_name = _safe_get_function_name(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            call_id = _increment_call_counter()
            
            # Логируем вызов
            log_parts = [f"[{level}] [{call_id}] Вызов '{func_name}'"]
            
            if log_args:
                args_str = ", ".join(
                    [repr(a)[:50] for a in args] +
                    [f"{k}={repr(v)[:50]}" for k, v in kwargs.items()]
                )
                log_parts.append(f"({args_str})")
            
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.DECORATOR,
                " ".join(log_parts)
            )
            
            try:
                result = func(*args, **kwargs)
                
                if log_time or log_result:
                    parts = [f"[{level}] [{call_id}] '{func_name}' выполнена"]
                    if log_time:
                        duration = time.time() - start_time
                        parts.append(f"за {duration:.4f}с")
                    if log_result:
                        parts.append(f"→ {repr(result)[:100]}")
                    
                    _kostyl_state.record_kostyl(
                        KostylSeverity.COSMETIC,
                        KostylCategory.DECORATOR,
                        " ".join(parts)
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.DECORATOR,
                    f"[{level}] [{call_id}] '{func_name}' УПАЛА через {duration:.4f}с: {type(e).__name__}"
                )
                raise
        
        return wrapper
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ВСЕХ ДЕКОРАТОРОВ РАЗОМ
# ═══════════════════════════════════════════════════════════════

def all_decorators():
    """Возвращает словарь со всеми доступными декораторами."""
    return {
        'safe': safe,
        'retry': retry,
        'fallback': fallback,
        'kostyl_method': kostyl_method,
        'cached': cached,
        'deprecated_kostyl': deprecated_kostyl,
        'monkey_patch': monkey_patch,
        'log_execution': log_execution,
    }

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    'safe',
    'retry',
    'fallback',
    'kostyl_method',
    'cached',
    'deprecated_kostyl',
    'monkey_patch',
    'log_execution',
    'all_decorators',
]

# Костыльная мета-информация
__decorator_count__ = len(__all__) - 1  # Минус all_decorators
__total_lines__ = 600  # Примерно
__coffee_consumed__ = "Много"