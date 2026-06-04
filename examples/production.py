# examples/production.py
"""
Продакшен-код на kostylpy.
Серьёзное приложение, которое никогда не падает.
Демонстрирует: логирование, метрики, мониторинг,
обработку ошибок, очереди задач и фоновые процессы.
"""

import sys
import os
import time
import random
import threading
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kostylpy as kp
from kostylpy import (
    safe, retry, fallback,
    KostylContext, kostyl_block,
    safe_get, safe_set, safe_divide,
    DotDict, SafeList,
)
from kostylpy.logging_kostyl import (
    logger, LogLevel,
    ConsoleHandler, FileHandler, MemoryHandler,
    CoffeeHandler,
)
from kostylpy.metrics import (
    metrics, Counter, Gauge, Histogram, Timer,
    track_metrics,
)
from kostylpy.utils import (
    timestamp_iso, time_ago, human_readable_size,
    random_string, to_json, safe_read_file,
    safe_write_file,
)
from kostylpy.async_kostyl import (
    TaskManager, AsyncRateLimiter,
    AsyncCircuitBreaker,
)

# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

print("=" * 70)
print("🏭 ПРОДАКШЕН-СИСТЕМА НА КОСТЫЛЯХ")
print("=" * 70)

# Настраиваем логгер
logger.clear_handlers()
logger.add_handler(ConsoleHandler(level=LogLevel.INFO))
logger.add_handler(FileHandler("production.log", level=LogLevel.DEBUG))
logger.add_handler(MemoryHandler(max_records=1000))

# Специальный обработчик для кофе-брейков
coffee_handler = CoffeeHandler("coffee_breaks.log")
logger.add_handler(coffee_handler)

logger.info("🚀 Продакшен-система запускается...")
logger.info(f"   Версия kostylpy: {kp.__version__}")
logger.info(f"   Время запуска: {timestamp_iso()}")

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ СИСТЕМЫ
# ═══════════════════════════════════════════════════════════════

config = DotDict({
    'app': {
        'name': 'KostylProduction',
        'version': '1.0.0',
        'environment': 'production',
        'debug': False,
    },
    'database': {
        'primary': {'host': 'db-primary.local', 'port': 5432},
        'replica': {'host': 'db-replica.local', 'port': 5432},
        'max_connections': 50,
        'timeout': 30,
    },
    'cache': {
        'enabled': True,
        'ttl': 3600,
        'max_size_mb': 512,
    },
    'queue': {
        'max_size': 10000,
        'workers': 4,
        'retry_limit': 3,
    },
    'monitoring': {
        'metrics_interval': 60,
        'health_check_interval': 30,
        'alert_threshold': 0.95,
    },
})

logger.info(f"📋 Конфигурация загружена: {config.app.name} v{config.app.version}")
logger.info(f"   Окружение: {config.app.environment}")

# ═══════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ (С ПУЛОМ СОЕДИНЕНИЙ)
# ═══════════════════════════════════════════════════════════════

logger.info("🗄️ Инициализация базы данных...")

class ConnectionPool:
    """Пул соединений с базой данных (заглушка)."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._active = 0
        self._lock = threading.Lock()
        self._total_created = Counter("db_connections_created", "Создано соединений")
        self._total_released = Counter("db_connections_released", "Освобождено соединений")
        self._wait_time = Histogram("db_wait_time", "Время ожидания соединения")
    
    @property
    def active_connections(self):
        return self._active
    
    @property
    def available_connections(self):
        return self.max_connections - self._active
    
    def acquire(self):
        """Получает соединение."""
        start = time.time()
        
        with self._lock:
            if self._active >= self.max_connections:
                logger.warning(f"Пул соединений переполнен! ({self._active}/{self.max_connections})")
                return None
            
            self._active += 1
            self._total_created.increment()
        
        self._wait_time.observe(time.time() - start)
        return DotDict({'id': random_string(8), 'created_at': timestamp_iso()})
    
    def release(self, connection):
        """Возвращает соединение в пул."""
        with self._lock:
            if self._active > 0:
                self._active -= 1
                self._total_released.increment()

db_pool = ConnectionPool(max_connections=config.database.max_connections)
logger.info(f"   Пул соединений: {db_pool.max_connections} max")

@safe(fallback={'status': 'error', 'message': 'Ошибка БД'})
@retry(max_attempts=3, delay=0.1, fallback={'status': 'error', 'message': 'БД недоступна'})
def db_query(query: str, params: dict = None) -> dict:
    """Выполняет запрос к базе данных."""
    
    conn = db_pool.acquire()
    if conn is None:
        raise RuntimeError("Нет доступных соединений")
    
    try:
        with KostylContext("запрос к БД"):
            # Имитация запроса
            time.sleep(random.uniform(0.01, 0.05))
            
            if "DROP" in query.upper() or "DELETE" in query.upper():
                logger.warning(f"Опасный запрос: {query[:50]}...")
            
            result = {
                'status': 'ok',
                'rows': random.randint(1, 100),
                'time_ms': random.uniform(1, 50),
                'connection_id': conn.id,
            }
            
            logger.debug(f"Запрос выполнен: {query[:50]}... ({result['time_ms']:.1f}ms)")
            return result
    
    finally:
        db_pool.release(conn)

# ═══════════════════════════════════════════════════════════════
# КЕШ (С TTL)
# ═══════════════════════════════════════════════════════════════

logger.info("💾 Инициализация кеша...")

class Cache:
    """Простой кеш с TTL."""
    
    def __init__(self, max_size_mb: int = 512, default_ttl: int = 3600):
        self.max_size_mb = max_size_mb
        self.default_ttl = default_ttl
        self._cache = {}
        self._lock = threading.Lock()
        self._hits = Counter("cache_hits", "Попаданий в кеш")
        self._misses = Counter("cache_misses", "Промахов кеша")
        self._size = Gauge("cache_size", "Размер кеша (записей)")
    
    @safe(fallback=None)
    def get(self, key: str):
        """Получает значение из кеша."""
        with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if time.time() < expires_at:
                    self._hits.increment()
                    return value
                else:
                    del self._cache[key]
        
        self._misses.increment()
        return None
    
    @safe(fallback=False)
    def set(self, key: str, value: any, ttl: int = None):
        """Сохраняет значение в кеш."""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        with self._lock:
            self._cache[key] = (value, expires_at)
            self._size.set(len(self._cache))
        
        return True
    
    @safe(fallback=False)
    def delete(self, key: str):
        """Удаляет значение из кеша."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._size.set(len(self._cache))
                return True
        return False
    
    @safe(fallback=0)
    def clear(self):
        """Очищает кеш."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._size.set(0)
            return count
    
    @property
    def hit_rate(self):
        total = self._hits.get() + self._misses.get()
        if total == 0:
            return 100.0
        return (self._hits.get() / total) * 100
    
    @property
    def size(self):
        return len(self._cache)

cache = Cache(max_size_mb=config.cache.max_size_mb, default_ttl=config.cache.ttl)
logger.info(f"   Кеш: до {config.cache.max_size_mb}MB, TTL={config.cache.ttl}с")

# ═══════════════════════════════════════════════════════════════
# ОЧЕРЕДЬ ЗАДАЧ
# ═══════════════════════════════════════════════════════════════

logger.info("📬 Инициализация очереди задач...")

class TaskQueue:
    """Очередь задач с воркерами."""
    
    def __init__(self, max_size: int = 1000, workers: int = 4):
        self.max_size = max_size
        self._queue = []
        self._lock = threading.Lock()
        self._workers = []
        self._running = False
        
        self._enqueued = Counter("tasks_enqueued", "Добавлено задач")
        self._processed = Counter("tasks_processed", "Обработано задач")
        self._failed = Counter("tasks_failed", "Провалено задач")
        self._queue_size = Gauge("queue_size", "Размер очереди")
        
        # Запускаем воркеры
        for i in range(workers):
            worker = threading.Thread(target=self._worker_loop, name=f"Worker-{i+1}", daemon=True)
            self._workers.append(worker)
        
        self._running = True
        for w in self._workers:
            w.start()
        
        logger.info(f"   Очередь: {max_size} max, {workers} воркеров")
    
    @safe(fallback=False)
    def enqueue(self, task_name: str, task_data: dict = None) -> bool:
        """Добавляет задачу в очередь."""
        with self._lock:
            if len(self._queue) >= self.max_size:
                logger.warning(f"Очередь переполнена! ({len(self._queue)}/{self.max_size})")
                return False
            
            task = {
                'id': random_string(16),
                'name': task_name,
                'data': task_data or {},
                'created_at': timestamp_iso(),
                'attempts': 0,
            }
            
            self._queue.append(task)
            self._enqueued.increment()
            self._queue_size.set(len(self._queue))
            
            logger.debug(f"Задача добавлена: {task_name} (#{task['id'][:8]})")
            return True
    
    @safe(fallback=None)
    def _dequeue(self):
        """Извлекает задачу из очереди."""
        with self._lock:
            if self._queue:
                task = self._queue.pop(0)
                self._queue_size.set(len(self._queue))
                return task
        return None
    
    def _worker_loop(self):
        """Цикл воркера."""
        worker_name = threading.current_thread().name
        
        while self._running:
            task = self._dequeue()
            
            if task is None:
                time.sleep(0.1)
                continue
            
            try:
                with KostylContext(f"обработка задачи {task['name']}"):
                    self._process_task(task)
                    self._processed.increment()
                    
            except Exception as e:
                self._failed.increment()
                logger.error(f"Задача {task['id'][:8]} провалена: {e}")
    
    @track_metrics(name="task_processing")
    def _process_task(self, task: dict):
        """Обрабатывает задачу."""
        task_name = task['name']
        
        # Разные типы задач
        if task_name == 'send_email':
            time.sleep(random.uniform(0.05, 0.2))
            logger.info(f"📧 Email отправлен: {task['data'].get('to', 'unknown')}")
        
        elif task_name == 'generate_report':
            time.sleep(random.uniform(0.1, 0.5))
            logger.info(f"📊 Отчёт создан: {task['data'].get('type', 'unknown')}")
        
        elif task_name == 'backup_database':
            time.sleep(random.uniform(0.2, 1.0))
            logger.info(f"💾 Бекап создан")
        
        elif task_name == 'clear_cache':
            count = cache.clear()
            logger.info(f"🗑️ Кеш очищен: {count} записей")
        
        else:
            time.sleep(random.uniform(0.01, 0.1))
            logger.debug(f"Задача выполнена: {task_name}")
    
    def stop(self):
        """Останавливает очередь."""
        self._running = False
        for w in self._workers:
            w.join(timeout=5)
        logger.info(f"Очередь остановлена. Обработано: {self._processed.get()}")

task_queue = TaskQueue(
    max_size=config.queue.max_size,
    workers=config.queue.workers
)

# ═══════════════════════════════════════════════════════════════
# МОНИТОРИНГ
# ═══════════════════════════════════════════════════════════════

logger.info("📊 Запуск мониторинга...")

class HealthChecker:
    """Проверка здоровья системы."""
    
    def __init__(self):
        self._checks = []
        self._last_check = Gauge("last_health_check", "Время последней проверки")
        self._healthy = Gauge("system_healthy", "Система здорова (1=да)")
    
    def add_check(self, name: str, check_func: callable):
        self._checks.append((name, check_func))
    
    @safe(fallback={'status': 'degraded', 'checks': {}})
    def check_all(self) -> dict:
        """Выполняет все проверки."""
        results = {}
        all_healthy = True
        
        for name, check_func in self._checks:
            try:
                is_healthy = check_func()
                results[name] = '✅' if is_healthy else '❌'
                if not is_healthy:
                    all_healthy = False
            except Exception as e:
                results[name] = f'❌ ({e})'
                all_healthy = False
        
        self._last_check.set(time.time())
        self._healthy.set(1 if all_healthy else 0)
        
        return {
            'status': 'healthy' if all_healthy else 'degraded',
            'timestamp': timestamp_iso(),
            'checks': results,
        }

health_checker = HealthChecker()

# Добавляем проверки
health_checker.add_check('database', lambda: db_pool.active_connections < db_pool.max_connections)
health_checker.add_check('cache', lambda: cache.size < 10000)
health_checker.add_check('queue', lambda: task_queue._queue_size.get() < task_queue.max_size * 0.9)
health_checker.add_check('memory', lambda: True)  # Всегда ок, мы ж на костылях
health_checker.add_check('coffee', lambda: metrics.coffee.time_since_last < 7200)

logger.info(f"   Проверок здоровья: {len(health_checker._checks)}")

# ═══════════════════════════════════════════════════════════════
# ФОНОВЫЕ ПРОЦЕССЫ
# ═══════════════════════════════════════════════════════════════

logger.info("🔄 Запуск фоновых процессов...")

# Фоновая статистика
def background_stats():
    """Собирает и логирует статистику."""
    while getattr(background_stats, '_running', True):
        time.sleep(config.monitoring.metrics_interval)
        
        stats = {
            'uptime': kp.core.uptime,
            'db_connections': f"{db_pool.active_connections}/{db_pool.max_connections}",
            'cache_size': cache.size,
            'cache_hit_rate': f"{cache.hit_rate:.1f}%",
            'queue_size': task_queue._queue_size.get(),
            'tasks_processed': task_queue._processed.get(),
            'errors_caught': kp.core._error_counter,
            'coffee_breaks': metrics.coffee.total_coffees,
        }
        
        logger.info(f"📊 Статистика: {to_json(stats)}")

# Фоновая проверка здоровья
def background_health_check():
    """Периодически проверяет здоровье."""
    while getattr(background_health_check, '_running', True):
        time.sleep(config.monitoring.health_check_interval)
        
        result = health_checker.check_all()
        
        if result['status'] != 'healthy':
            logger.warning(f"⚠️ Система нездорова! {to_json(result['checks'])}")
        else:
            logger.debug(f"✅ Система здорова")

# Запускаем фоновые потоки
stats_thread = threading.Thread(target=background_stats, daemon=True, name="StatsReporter")
stats_thread._running = True
stats_thread.start()

health_thread = threading.Thread(target=background_health_check, daemon=True, name="HealthChecker")
health_thread._running = True
health_thread.start()

# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ ЦИКЛ РАБОТЫ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("🏭 СИСТЕМА ЗАПУЩЕНА")
print("=" * 70)

logger.info("✅ Система готова к работе")
logger.coffee("☕ Кофе готов!")

try:
    # Имитация работы системы
    logger.info("Начинаем обработку...")
    
    # 1. Запросы к БД
    logger.info("\n1. Запросы к базе данных:")
    for i in range(5):
        result = db_query(f"SELECT * FROM users WHERE id = {i+1}")
        logger.info(f"   Запрос {i+1}: {result['status']} ({result['time_ms']:.1f}ms)")
    
    # 2. Работа с кешем
    logger.info("\n2. Работа с кешем:")
    cache.set('config:app', config.app, ttl=60)
    cache.set('stats:users', {'total': 1000, 'active': 750}, ttl=30)
    
    cached_config = cache.get('config:app')
    logger.info(f"   Кеш конфига: {cached_config.name if cached_config else 'промах'}")
    logger.info(f"   Hit rate: {cache.hit_rate:.1f}%")
    
    # 3. Очередь задач
    logger.info("\n3. Отправка задач в очередь:")
    
    tasks_to_send = [
        ('send_email', {'to': 'admin@example.com', 'subject': 'Отчёт'}),
        ('send_email', {'to': 'user@example.com', 'subject': 'Приветствие'}),
        ('generate_report', {'type': 'monthly', 'month': '2024-01'}),
        ('backup_database', {}),
        ('clear_cache', {}),
        ('send_email', {'to': 'dev@example.com', 'subject': 'Деплой'}),
    ]
    
    for task_name, task_data in tasks_to_send:
        success = task_queue.enqueue(task_name, task_data)
        status = "✅" if success else "❌"
        logger.info(f"   {status} {task_name}: {task_data.get('to', task_data.get('type', ''))}")
    
    # Ждём обработки
    logger.info("\n4. Ожидание обработки очереди...")
    time.sleep(2)
    
    # 4. Проверка здоровья
    logger.info("\n5. Проверка здоровья системы:")
    health = health_checker.check_all()
    
    logger.info(f"   Статус: {health['status'].upper()}")
    for check, status in health['checks'].items():
        logger.info(f"   {status} {check}")
    
    # 5. Кофе-брейк
    logger.info("\n6. Кофе-брейк:")
    metrics.coffee.drink(duration=300.0)
    logger.coffee("☕ Кофе выпит! Можно работать дальше.")
    
    # Ждём ещё немного для сбора статистики
    time.sleep(1)
    
except KeyboardInterrupt:
    logger.warning("⚠️ Получен сигнал завершения")
except Exception as e:
    logger.error(f"Критическая ошибка: {e}")

finally:
    # ═══════════════════════════════════════════════════════════
    # ЗАВЕРШЕНИЕ РАБОТЫ
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("📊 ФИНАЛЬНЫЙ ОТЧЁТ")
    print("=" * 70)
    
    # Останавливаем фоновые потоки
    stats_thread._running = False
    health_thread._running = False
    task_queue.stop()
    
    # Статистика БД
    print(f"""
    🗄️ База данных:
       Соединений: {db_pool.active_connections}/{db_pool.max_connections}
       Создано: {db_pool._total_created.get()}
       Освобождено: {db_pool._total_released.get()}
    
    💾 Кеш:
       Размер: {cache.size} записей
       Попаданий: {cache.hit_rate:.1f}%
       Всего запросов: {cache._hits.get() + cache._misses.get()}
    
    📬 Очередь:
       Добавлено задач: {task_queue._enqueued.get()}
       Обработано: {task_queue._processed.get()}
       Провалено: {task_queue._failed.get()}
       В очереди: {task_queue._queue_size.get()}
    
    🏥 Здоровье:
       Проверок: {len(health_checker._checks)}
       Статус: {health['status'].upper()}
    
    ☕ Кофе:
       Всего кофе-брейков: {metrics.coffee.total_coffees}
       Последний: {time_ago(metrics.coffee.time_since_last) if metrics.coffee.time_since_last < float('inf') else 'никогда'}
    """)
    
    # Общая статистика
    print(f"""
    🦿 KOSTYLPY:
       Версия: {kp.__version__}
       Время работы: {kp.core.uptime:.1f}с
       Костылей применено: {kp.core.stats().get('crutches', 'много')}
       Ошибок перехвачено: {kp.core._error_counter}
       Статус ядра: {kp.core.status}
    """)
    
    # Сохраняем логи
    logger.export_logs("production_report.json")
    metrics.export_json("production_metrics.json")
    
    print("   📄 Логи сохранены: production.log")
    print("   📊 Метрики сохранены: production_metrics.json")
    print("   ☕ Кофе-брейки: coffee_breaks.log")
    
    print("\n" + "=" * 70)
    print("✅ ПРОДАКШЕН-СИСТЕМА ЗАВЕРШИЛА РАБОТУ")
    print("=" * 70)
    print("   🦿 Все системы отработали штатно")
    print("   ☕ Пора пить кофе и деплоить в продакшен!")