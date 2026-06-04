"""
Метрики kostylpy.
Собирает статистику обо всём: сколько костылей, как часто падает,
сколько кофе выпито, и насколько всё плохо.

Содержит:
- KostylMetrics — сборщик метрик
- Counter — счётчик событий
- Gauge — измеряемая величина
- Histogram — гистограмма значений
- Timer — замер времени
- CoffeeMeter — счётчик кофе
- CrashCounter — счётчик падений
- PatchMetrics — метрики патчей
- MetricsCollector — сборщик всех метрик
- MetricsReporter — генератор отчётов
- Глобальный экземпляр метрик
"""

import time
import threading
import json
import math
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import statistics

# Импортируем константы
try:
    from .constants import Emoji, Colors
except ImportError:
    class Emoji:
        KOSTYL = "🦿"
        COFFEE = "☕"
        ERROR = "❌"
        SUCCESS = "✅"
        WARNING = "⚠️"
        FIX = "🩹"
        PARTY = "🎉"
        CHART = "📊"
        CLOCK = "⏱️"
    class Colors:
        @staticmethod
        def green(t): return t
        @staticmethod
        def red(t): return t
        @staticmethod
        def yellow(t): return t
        RESET = ""

# Импортируем состояние
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    _kostyl_state = None

# ═══════════════════════════════════════════════════════════════
# ТИПЫ МЕТРИК
# ═══════════════════════════════════════════════════════════════

class MetricType(Enum):
    COUNTER = "counter"       # Счётчик (только растёт)
    GAUGE = "gauge"           # Измеряемая величина
    HISTOGRAM = "histogram"   # Гистограмма значений
    TIMER = "timer"           # Измерение времени
    RATE = "rate"             # Частота событий

@dataclass
class MetricSnapshot:
    """Снимок метрики в момент времени."""
    name: str
    type: MetricType
    value: Any
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': self.type.value,
            'value': self.value,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
        }

# ═══════════════════════════════════════════════════════════════
# БАЗОВАЯ МЕТРИКА
# ═══════════════════════════════════════════════════════════════

class BaseMetric:
    """Базовая метрика."""
    
    def __init__(self, name: str, description: str = "", labels: Dict[str, str] = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self._created_at = time.time()
        self._lock = threading.Lock()
    
    def snapshot(self) -> MetricSnapshot:
        raise NotImplementedError
    
    def reset(self):
        raise NotImplementedError
    
    @property
    def age(self) -> float:
        return time.time() - self._created_at

# ═══════════════════════════════════════════════════════════════
# СЧЁТЧИК
# ═══════════════════════════════════════════════════════════════

class Counter(BaseMetric):
    """Счётчик, который только увеличивается."""
    
    def __init__(self, name: str, description: str = "", initial: int = 0):
        super().__init__(name, description)
        self._value = initial
    
    def increment(self, delta: int = 1):
        with self._lock:
            self._value += delta
    
    def get(self) -> int:
        return self._value
    
    def snapshot(self) -> MetricSnapshot:
        return MetricSnapshot(
            name=self.name,
            type=MetricType.COUNTER,
            value=self._value,
            timestamp=time.time(),
            metadata={'description': self.description}
        )
    
    def reset(self):
        with self._lock:
            self._value = 0
    
    def __str__(self):
        return f"Counter({self.name}): {self._value}"

# ═══════════════════════════════════════════════════════════════
# ИЗМЕРЯЕМАЯ ВЕЛИЧИНА
# ═══════════════════════════════════════════════════════════════

class Gauge(BaseMetric):
    """Величина, которая может меняться в обе стороны."""
    
    def __init__(self, name: str, description: str = "", initial: float = 0.0):
        super().__init__(name, description)
        self._value = initial
    
    def set(self, value: float):
        with self._lock:
            self._value = value
    
    def increment(self, delta: float = 1.0):
        with self._lock:
            self._value += delta
    
    def decrement(self, delta: float = 1.0):
        with self._lock:
            self._value -= delta
    
    def get(self) -> float:
        return self._value
    
    def snapshot(self) -> MetricSnapshot:
        return MetricSnapshot(
            name=self.name,
            type=MetricType.GAUGE,
            value=self._value,
            timestamp=time.time(),
            metadata={'description': self.description}
        )
    
    def reset(self):
        with self._lock:
            self._value = 0.0
    
    def __str__(self):
        return f"Gauge({self.name}): {self._value}"

# ═══════════════════════════════════════════════════════════════
# ГИСТОГРАММА
# ═══════════════════════════════════════════════════════════════

class Histogram(BaseMetric):
    """Гистограмма значений с бакетами."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        buckets: List[float] = None,
    ):
        super().__init__(name, description)
        self.buckets = sorted(buckets or [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0])
        self._values: List[float] = []
        self._count = 0
        self._sum = 0.0
        self._bucket_counts = {b: 0 for b in self.buckets}
        self._bucket_counts[float('inf')] = 0
    
    def observe(self, value: float):
        with self._lock:
            self._values.append(value)
            self._count += 1
            self._sum += value
            
            # Находим бакет
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1
                    break
            else:
                self._bucket_counts[float('inf')] += 1
            
            # Ограничиваем историю
            if len(self._values) > 10000:
                self._values = self._values[-1000:]
    
    @property
    def count(self) -> int:
        return self._count
    
    @property
    def sum(self) -> float:
        return self._sum
    
    @property
    def avg(self) -> float:
        if self._count == 0:
            return 0.0
        return self._sum / self._count
    
    @property
    def min(self) -> float:
        if not self._values:
            return 0.0
        return min(self._values)
    
    @property
    def max(self) -> float:
        if not self._values:
            return 0.0
        return max(self._values)
    
    @property
    def median(self) -> float:
        if not self._values:
            return 0.0
        return statistics.median(self._values)
    
    @property
    def p95(self) -> float:
        """95-й перцентиль."""
        if not self._values:
            return 0.0
        sorted_values = sorted(self._values)
        index = int(len(sorted_values) * 0.95)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    @property
    def p99(self) -> float:
        """99-й перцентиль."""
        if not self._values:
            return 0.0
        sorted_values = sorted(self._values)
        index = int(len(sorted_values) * 0.99)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def snapshot(self) -> MetricSnapshot:
        return MetricSnapshot(
            name=self.name,
            type=MetricType.HISTOGRAM,
            value={
                'count': self._count,
                'sum': self._sum,
                'avg': self.avg,
                'min': self.min,
                'max': self.max,
                'median': self.median,
                'p95': self.p95,
                'p99': self.p99,
                'buckets': self._bucket_counts.copy(),
            },
            timestamp=time.time(),
            metadata={'description': self.description}
        )
    
    def reset(self):
        with self._lock:
            self._values.clear()
            self._count = 0
            self._sum = 0.0
            for bucket in self._bucket_counts:
                self._bucket_counts[bucket] = 0
    
    def __str__(self):
        return (
            f"Histogram({self.name}): "
            f"count={self._count}, avg={self.avg:.3f}, "
            f"median={self.median:.3f}, p95={self.p95:.3f}"
        )

# ═══════════════════════════════════════════════════════════════
# ТАЙМЕР
# ═══════════════════════════════════════════════════════════════

class Timer(BaseMetric):
    """Замеряет время операций."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self._histogram = Histogram(f"{name}_histogram", description)
        self._count = 0
        self._total_time = 0.0
    
    def start(self) -> 'TimerContext':
        """Начинает замер времени. Возвращает контекстный менеджер."""
        return TimerContext(self)
    
    def record(self, duration: float):
        with self._lock:
            self._histogram.observe(duration)
            self._count += 1
            self._total_time += duration
    
    def time(self, func: Callable) -> Callable:
        """Декоратор для замера времени функции."""
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                self.record(time.perf_counter() - start)
        
        return wrapper
    
    @property
    def count(self) -> int:
        return self._count
    
    @property
    def total_time(self) -> float:
        return self._total_time
    
    @property
    def avg(self) -> float:
        return self._histogram.avg
    
    @property
    def p95(self) -> float:
        return self._histogram.p95
    
    def snapshot(self) -> MetricSnapshot:
        return MetricSnapshot(
            name=self.name,
            type=MetricType.TIMER,
            value={
                'count': self._count,
                'total': self._total_time,
                'avg': self.avg,
                'p95': self.p95,
            },
            timestamp=time.time(),
            metadata={'description': self.description}
        )
    
    def reset(self):
        with self._lock:
            self._histogram.reset()
            self._count = 0
            self._total_time = 0.0
    
    def __str__(self):
        return (
            f"Timer({self.name}): "
            f"count={self._count}, avg={self.avg:.4f}с, p95={self.p95:.4f}с"
        )

class TimerContext:
    """Контекстный менеджер для таймера."""
    
    def __init__(self, timer: Timer):
        self.timer = timer
        self._start_time = 0.0
    
    def __enter__(self):
        self._start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration = time.perf_counter() - self._start_time
        self.timer.record(duration)
        return False

# ═══════════════════════════════════════════════════════════════
# СПЕЦИАЛЬНЫЕ МЕТРИКИ
# ═══════════════════════════════════════════════════════════════

class CoffeeMeter:
    """Измеряет потребление кофе."""
    
    def __init__(self):
        self._coffee_count = Counter("coffee_total", "Всего выпито кофе")
        self._coffee_time = Histogram(
            "coffee_duration",
            "Длительность кофе-брейков",
            buckets=[30, 60, 120, 300, 600]
        )
        self._last_coffee = Gauge("coffee_last", "Время последнего кофе")
        self._coffee_strength = Gauge("coffee_strength", "Крепость кофе (%)", initial=100.0)
    
    def drink(self, duration: float = 300.0, strength: float = 100.0):
        """Записывает кофе-брейк."""
        self._coffee_count.increment()
        self._coffee_time.observe(duration)
        self._last_coffee.set(time.time())
        self._coffee_strength.set(strength)
        
        if _kostyl_state:
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.UNKNOWN,
                f"☕ Кофе-брейк #{self._coffee_count.get()}: {duration}с"
            )
    
    @property
    def total_coffees(self) -> int:
        return self._coffee_count.get()
    
    @property
    def avg_duration(self) -> float:
        return self._coffee_time.avg
    
    @property
    def time_since_last(self) -> float:
        last = self._last_coffee.get()
        if last == 0:
            return float('inf')
        return time.time() - last
    
    def stats(self) -> Dict:
        return {
            'total': self.total_coffees,
            'avg_duration': f"{self.avg_duration:.1f}с",
            'time_since_last': f"{self.time_since_last:.1f}с",
            'strength': f"{self._coffee_strength.get():.0f}%",
            'status': '☕ Достаточно' if self.time_since_last < 3600 else '⚠️ Пора выпить кофе!'
        }

class CrashCounter:
    """Считает падения и восстановления."""
    
    def __init__(self):
        self._crashes = Counter("crashes_total", "Всего падений")
        self._recoveries = Counter("recoveries_total", "Всего восстановлений")
        self._crash_rate = Gauge("crash_rate", "Частота падений в час")
        self._last_crash = Gauge("last_crash", "Время последнего падения")
        self._crash_types = defaultdict(int)
    
    def record_crash(self, error_type: str = "unknown"):
        self._crashes.increment()
        self._last_crash.set(time.time())
        self._crash_types[error_type] += 1
    
    def record_recovery(self):
        self._recoveries.increment()
    
    @property
    def total_crashes(self) -> int:
        return self._crashes.get()
    
    @property
    def total_recoveries(self) -> int:
        return self._recoveries.get()
    
    @property
    def recovery_rate(self) -> float:
        crashes = self.total_crashes
        if crashes == 0:
            return 100.0
        return (self._recoveries.get() / crashes) * 100
    
    @property
    def most_common_crash(self) -> str:
        if not self._crash_types:
            return "none"
        return max(self._crash_types, key=self._crash_types.get)
    
    def stats(self) -> Dict:
        return {
            'total_crashes': self.total_crashes,
            'total_recoveries': self.total_recoveries,
            'recovery_rate': f"{self.recovery_rate:.1f}%",
            'most_common': self.most_common_crash,
            'crash_types': dict(self._crash_types),
        }

class PatchMetrics:
    """Метрики monkey patching'а."""
    
    def __init__(self):
        self._patches_applied = Counter("patches_applied", "Применено патчей")
        self._patches_failed = Counter("patches_failed", "Провалено патчей")
        self._patches_rolled_back = Counter("patches_rolled_back", "Откачено патчей")
        self._active_patches = Gauge("patches_active", "Активных патчей")
    
    def record_apply(self):
        self._patches_applied.increment()
        self._active_patches.increment()
    
    def record_failure(self):
        self._patches_failed.increment()
    
    def record_rollback(self):
        self._patches_rolled_back.increment()
        self._active_patches.decrement()
    
    def stats(self) -> Dict:
        return {
            'applied': self._patches_applied.get(),
            'failed': self._patches_failed.get(),
            'rolled_back': self._patches_rolled_back.get(),
            'active': self._active_patches.get(),
        }

# ═══════════════════════════════════════════════════════════════
# СБОРЩИК МЕТРИК
# ═══════════════════════════════════════════════════════════════

class KostylMetrics:
    """
    Главный сборщик метрик kostylpy.
    Содержит все метрики и умеет генерировать отчёты.
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
        
        # Создаём все метрики
        self._metrics: Dict[str, BaseMetric] = {}
        self._start_time = time.time()
        
        # Основные счётчики
        self.total_operations = Counter("ops_total", "Всего операций")
        self.successful_ops = Counter("ops_success", "Успешных операций")
        self.failed_ops = Counter("ops_failed", "Проваленных операций")
        
        # Время операций
        self.operation_timer = Timer("op_duration", "Длительность операций")
        
        # Специальные метрики
        self.coffee = CoffeeMeter()
        self.crashes = CrashCounter()
        self.patches = PatchMetrics()
        
        # Количество костылей
        self.total_crutches = Counter("crutches_total", "Всего костылей")
        self.active_crutches = Gauge("crutches_active", "Активных костылей")
        
        # Производительность
        self.memory_usage = Gauge("memory_mb", "Использование памяти (МБ)")
        self.uptime = Gauge("uptime_seconds", "Время работы (сек)")
        
        # Регистрируем метрики
        self._register(self.total_operations)
        self._register(self.successful_ops)
        self._register(self.failed_ops)
        self._register(self.operation_timer)
        self._register(self.total_crutches)
        self._register(self.active_crutches)
        self._register(self.memory_usage)
        self._register(self.uptime)
    
    def _register(self, metric: BaseMetric):
        self._metrics[metric.name] = metric
    
    def get(self, name: str) -> Optional[BaseMetric]:
        return self._metrics.get(name)
    
    def record_operation(self, success: bool = True, duration: float = 0.0):
        """Записывает операцию."""
        self.total_operations.increment()
        if success:
            self.successful_ops.increment()
        else:
            self.failed_ops.increment()
        self.operation_timer.record(duration)
    
    def record_crutch(self):
        """Записывает применение костыля."""
        self.total_crutches.increment()
        self.active_crutches.increment()
    
    def record_crutch_removed(self):
        """Записывает удаление костыля."""
        self.active_crutches.decrement()
    
    @property
    def success_rate(self) -> float:
        total = self.total_operations.get()
        if total == 0:
            return 100.0
        return (self.successful_ops.get() / total) * 100
    
    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time
    
    def update_system_metrics(self):
        """Обновляет системные метрики."""
        try:
            import psutil
            process = psutil.Process()
            self.memory_usage.set(process.memory_info().rss / 1024 / 1024)
        except ImportError:
            self.memory_usage.set(-1)
        
        self.uptime.set(self.uptime_seconds)
    
    def snapshot(self) -> Dict:
        """Создаёт снимок всех метрик."""
        self.update_system_metrics()
        
        return {
            'timestamp': time.time(),
            'uptime': self.uptime_seconds,
            'metrics': {
                name: metric.snapshot().to_dict()
                for name, metric in self._metrics.items()
            },
            'coffee': self.coffee.stats(),
            'crashes': self.crashes.stats(),
            'patches': self.patches.stats(),
            'summary': {
                'total_ops': self.total_operations.get(),
                'success_rate': f"{self.success_rate:.1f}%",
                'avg_duration': f"{self.operation_timer.avg:.4f}с",
                'total_crutches': self.total_crutches.get(),
                'active_crutches': self.active_crutches.get(),
            }
        }
    
    def report(self) -> str:
        """Генерирует красивый отчёт."""
        self.update_system_metrics()
        
        s = self.snapshot()
        summary = s['summary']
        
        report = f"""
{Emoji.CHART} ═══════════════════════════════════════
{Emoji.CHART} KOSTYLPY МЕТРИКИ
{Emoji.CHART} ═══════════════════════════════════════

{Emoji.CLOCK} Время работы: {self.uptime_seconds:.0f}с

{Emoji.KOSTYL} Операции:
   Всего: {summary['total_ops']}
   Успешно: {summary['success_rate']}
   Среднее время: {summary['avg_duration']}

{Emoji.KOSTYL} Костыли:
   Всего применено: {summary['total_crutches']}
   Активных: {summary['active_crutches']}

{Emoji.COFFEE} Кофе:
   Выпито: {s['coffee']['total']}
   Последний: {s['coffee']['time_since_last']} назад
   Статус: {s['coffee']['status']}

{Emoji.ERROR} Падения:
   Всего: {s['crashes']['total_crashes']}
   Восстановлено: {s['crashes']['recovery_rate']}
   Чаще всего: {s['crashes']['most_common']}

{Emoji.FIX} Патчи:
   Применено: {s['patches']['applied']}
   Активных: {s['patches']['active']}
   Откачено: {s['patches']['rolled_back']}

{Emoji.CHART} ═══════════════════════════════════════
"""
        return report
    
    def export_json(self, filepath: str = "kostylpy_metrics.json"):
        """Экспортирует метрики в JSON."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.snapshot(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ═══════════════════════════════════════════════════════════════

metrics = KostylMetrics()

# Удобные алиасы
record_operation = metrics.record_operation
record_crutch = metrics.record_crutch
drink_coffee = metrics.coffee.drink
record_crash = metrics.crashes.record_crash
record_recovery = metrics.crashes.record_recovery

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР ДЛЯ МЕТРИК
# ═══════════════════════════════════════════════════════════════

def track_metrics(name: str = None):
    """
    Декоратор для отслеживания метрик функции.
    Автоматически считает вызовы, успехи, падения и время.
    """
    import functools
    
    def decorator(func):
        metric_name = name or func.__name__
        timer = Timer(f"{metric_name}_timer", f"Время выполнения {metric_name}")
        success_counter = Counter(f"{metric_name}_success", f"Успешных вызовов {metric_name}")
        failure_counter = Counter(f"{metric_name}_failure", f"Провальных вызовов {metric_name}")
        
        metrics._register(timer)
        metrics._register(success_counter)
        metrics._register(failure_counter)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                success_counter.increment()
                return result
            except Exception:
                failure_counter.increment()
                raise
            finally:
                timer.record(time.perf_counter() - start)
                metrics.total_operations.increment()
        
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основное
    'KostylMetrics',
    'metrics',  # Глобальный экземпляр
    
    # Типы метрик
    'Counter',
    'Gauge',
    'Histogram',
    'Timer',
    'TimerContext',
    
    # Специальные
    'CoffeeMeter',
    'CrashCounter',
    'PatchMetrics',
    
    # Утилиты
    'MetricType',
    'MetricSnapshot',
    
    # Алиасы
    'record_operation',
    'record_crutch',
    'drink_coffee',
    'record_crash',
    'record_recovery',
    
    # Декоратор
    'track_metrics',
]

# Записываем первую метрику
metrics.total_operations.increment()
metrics.coffee.drink(duration=0.1, strength=100.0)  # Инициализационный кофе
print(f"{Emoji.CHART} kostylpy.metrics: метрики активированы")