<h1>🦿 Kostylpy API Reference</h1>

<p><em>Полная документация по API библиотеки kostylpy. (Насколько "полная" может быть документация к костылям.)</em></p>

<hr>

<h2>📑 Оглавление</h2>

<p>
    <a href="#core">🏗️ Ядро</a> •
    <a href="#config">⚙️ Конфигурация</a> •
    <a href="#decorators">🛡️ Декораторы</a> •
    <a href="#context">📦 Контекстные менеджеры</a> •
    <a href="#validators">✅ Валидаторы</a> •
    <a href="#utils">🔧 Утилиты</a> •
    <a href="#factories">🏭 Фабрики</a> •
    <a href="#interceptors">🕵️ Перехватчики</a> •
    <a href="#metrics">📊 Метрики</a> •
    <a href="#logging">📝 Логирование</a> •
    <a href="#async">🔄 Асинхронные костыли</a> •
    <a href="#patcher">💉 Патчер</a> •
    <a href="#monkey">🐒 Monkey Patcher</a> •
    <a href="#constants">📋 Константы</a> •
    <a href="#full-example">🎯 Полный пример</a>
</p>

<hr>

<h2 id="core">🏗️ Ядро (Core)</h2>

<h3><code>kostylpy.KostylPy</code></h3>
<p>Главный класс библиотеки. <strong>Синглтон</strong>.</p>

<pre><code>from kostylpy.core import KostylPy
core = KostylPy()</code></pre>

<h4>Свойства</h4>
<ul>
    <li><code>status</code> — <em>"активно"</em>, <em>"деградировано"</em>, <em>"паника!"</em></li>
    <li><code>is_active</code> → <code>bool</code></li>
    <li><code>is_panic</code> → <code>bool</code></li>
    <li><code>uptime</code> → <code>float</code> (секунды)</li>
    <li><code>config</code> — экземпляр <code>KostylConfig</code></li>
    <li><code>logger</code> — экземпляр <code>KostylLogger</code></li>
    <li><code>metrics</code> — экземпляр <code>KostylMetrics</code></li>
</ul>

<h4>Методы</h4>
<ul>
    <li><code>health_check()</code> → <code>dict</code> — проверка здоровья всех систем</li>
    <li><code>stats()</code> → <code>dict</code> — статистика ядра</li>
    <li><code>report()</code> → <code>str</code> — полный отчёт</li>
    <li><code>get_module(name)</code> → <code>module | None</code></li>
    <li><code>is_module_loaded(name)</code> → <code>bool</code></li>
    <li><code>loaded_modules()</code> → <code>list[str]</code></li>
</ul>

<hr>

<h2 id="config">⚙️ Конфигурация (Config)</h2>

<h3><code>kostylpy.config</code></h3>
<p>Глобальный экземпляр конфигурации.</p>

<pre><code>from kostylpy.config import config

config.get('debug')                    # False
config.get('network.default_timeout')  # 30.0

# Быстрый доступ
config.debug              # False
config.panic_threshold    # 42
config.coffee_required    # True

# Установка
config.set('debug', True)</code></pre>

<h4>Свойства</h4>
<ul>
    <li><code>debug</code>, <code>verbose</code>, <code>log_level</code></li>
    <li><code>panic_threshold</code> — порог паники (по умолчанию <strong>42</strong>)</li>
    <li><code>coffee_required</code> — <code>True</code> всегда</li>
    <li><code>default_timeout</code>, <code>retry_count</code></li>
</ul>

<h4>Методы</h4>
<ul>
    <li><code>get(key, default=None)</code> — вложенные ключи через точку</li>
    <li><code>set(key, value)</code> / <code>has(key)</code> / <code>all()</code></li>
    <li><code>load_file(path)</code> / <code>load_env(prefix)</code> / <code>load_all()</code></li>
    <li><code>save(path)</code> / <code>validate()</code> / <code>report()</code></li>
</ul>

<hr>

<h2 id="decorators">🛡️ Декораторы</h2>

<h3><code>@kostylpy.safe</code></h3>
<p>Функция <strong>никогда не упадёт</strong>.</p>

<pre><code>@kp.safe(fallback="всё ок")
def risky():
    raise ValueError("Ошибка!")
result = risky()  # "всё ок"</code></pre>

<table>
    <tr><th>Параметр</th><th>Тип</th><th>Описание</th></tr>
    <tr><td><code>fallback</code></td><td>any</td><td>Значение при ошибке</td></tr>
    <tr><td><code>log_errors</code></td><td>bool</td><td>Логировать ошибки</td></tr>
    <tr><td><code>reraise</code></td><td>bool | list[type]</td><td>Пробросить исключения</td></tr>
    <tr><td><code>on_error</code></td><td>callable</td><td>Обработчик ошибок</td></tr>
    <tr><td><code>max_failures</code></td><td>int</td><td>Лимит ошибок перед panic</td></tr>
</table>

<h3><code>@kostylpy.retry</code></h3>
<p>Повторяет функцию при ошибке.</p>

<pre><code>@kp.retry(max_attempts=3, delay=0.1, backoff=2.0)
def flaky():
    return api.call()</code></pre>

<table>
    <tr><th>Параметр</th><th>Тип</th><th>По умолчанию</th></tr>
    <tr><td><code>max_attempts</code></td><td>int</td><td>3</td></tr>
    <tr><td><code>delay</code></td><td>float | (min, max)</td><td>0.1</td></tr>
    <tr><td><code>backoff</code></td><td>float</td><td>2.0</td></tr>
    <tr><td><code>exceptions</code></td><td>type | tuple</td><td>Exception</td></tr>
    <tr><td><code>jitter</code></td><td>bool</td><td>True</td></tr>
    <tr><td><code>fallback</code></td><td>any</td><td>None</td></tr>
</table>

<h3><code>@kostylpy.fallback</code></h3>
<p>Возвращает запасное значение при ошибке.</p>
<pre><code>@kp.fallback(0)
def divide(a, b): return a / b</code></pre>

<h3><code>@kostylpy.cached</code></h3>
<p>Кеширует результаты функции.</p>
<pre><code>@kp.cached(max_size=128, ttl=60)
def expensive(x, y): ...</code></pre>

<h3><code>@kostylpy.deprecated_kostyl</code></h3>
<p>Помечает функцию как устаревшую.</p>
<pre><code>@kp.deprecated_kostyl(reason="старый", alternative="новый")
def old_func(): ...</code></pre>

<hr>

<h2 id="context">📦 Контекстные менеджеры</h2>

<h3><code>KostylContext</code></h3>
<p>Подавляет все исключения внутри блока.</p>
<pre><code>with kp.KostylContext("опасный блок", suppress=True):
    1 / 0  # не упадёт!</code></pre>

<h3><code>TimerContext</code></h3>
<p>Замеряет время выполнения блока.</p>
<pre><code>with kp.TimerContext("замер") as t:
    do_work()
print(t.elapsed)  # float</code></pre>

<h3><code>SafeFileContext</code></h3>
<p>Безопасная работа с файлами.</p>
<pre><code>with kp.SafeFileContext("config.json", "r") as f:
    data = f.read()</code></pre>

<h3><code>kostyl_block</code></h3>
<p>Быстрый костыльный блок.</p>
<pre><code>with kp.kostyl_block():
    risky()</code></pre>

<hr>

<h2 id="validators">✅ Валидаторы</h2>

<table>
    <tr><th>Валидатор</th><th>Пример</th></tr>
    <tr><td><code>TypeValidator</code></td><td><code>kp.TypeValidator(int)</code></td></tr>
    <tr><td><code>RangeValidator</code></td><td><code>kp.RangeValidator(min=0, max=100)</code></td></tr>
    <tr><td><code>StringValidator</code></td><td><code>kp.StringValidator(min_length=3)</code></td></tr>
    <tr><td><code>EmailValidator</code></td><td><code>kp.EmailValidator()</code></td></tr>
    <tr><td><code>PasswordValidator</code></td><td><code>kp.PasswordValidator(min_length=8, require_emoji=True)</code></td></tr>
    <tr><td><code>NullValidator</code></td><td><code>kp.NullValidator()</code></td></tr>
    <tr><td><code>FileValidator</code></td><td><code>kp.FileValidator(max_size_mb=10)</code></td></tr>
    <tr><td><code>DataValidator</code></td><td><code>kp.DataValidator(schema={"name": StringValidator()})</code></td></tr>
</table>

<h3><code>ValidationResult</code></h3>
<p>Результат валидации.</p>
<pre><code>result = validator.validate(value)
result.is_valid         # bool
result.errors           # list[ValidationError]
result.raise_if_invalid()
result.get_or_default(default)</code></pre>

<h3><code>ValidationPipeline</code></h3>
<p>Цепочка валидаторов.</p>
<pre><code>pipe = kp.ValidationPipeline()
pipe.add(kp.TypeValidator(int))
pipe.add(kp.RangeValidator(min=0))
pipe.validate(42)</code></pre>

<hr>

<h2 id="utils">🔧 Утилиты</h2>

<h3>Безопасные структуры данных</h3>
<pre><code>d = kp.DotDict({'a': {'b': 1}})
d.a.b  # 1

lst = kp.SafeList([1,2,3], default=0)
lst[100]  # 0</code></pre>

<h3>Безопасный доступ</h3>
<pre><code>kp.safe_get(data, 'users.0.name', default='?')  # 'Alice'
kp.safe_divide(100, 0, default=0)  # 0
kp.clamp(value, 0, 100)</code></pre>

<h3>Форматирование</h3>
<pre><code>kp.human_readable_size(1234567)  # "1.2 МБ"
kp.time_ago(3661)                # "1 час назад"
kp.truncate("длинный...", 10)    # "длинный..."
kp.slugify("Привет, Мир!")      # "privet-mir"</code></pre>

<h3>Генераторы</h3>
<pre><code>kp.random_string(16)
kp.random_email()
kp.random_name()
kp.random_ip()
kp.random_emoji()</code></pre>

<h3>Конвертеры</h3>
<pre><code>kp.to_json(obj)
kp.from_json(text)
kp.to_base64("hello")
kp.to_hash("data")</code></pre>

<hr>

<h2 id="factories">🏭 Фабрики</h2>

<pre><code># Исключения
exc = kp.ExceptionFactory().produce("ValueError", "Всё плохо")

# Заглушки
stub = kp.StubFactory().produce("function", return_value=42)

# Случайные костыли
product = kp.RandomKostylFactory().produce()

# Мета-фабрика (создаёт другие фабрики)
factory = kp.MetaFactory().produce("stub")</code></pre>

<hr>

<h2 id="interceptors">🕵️ Перехватчики</h2>

<pre><code># Перехват функции
kp.FunctionInterceptor(target_func=my_func, mode=kp.InterceptMode.LOG_ONLY)

# Глобальный перехват
kp.intercept_all()

# Шпионаж
kp.spy_on_function(my_func)

# Блокировка импортов
kp.block_imports('os', 'subprocess')</code></pre>

<hr>

<h2 id="metrics">📊 Метрики</h2>

<pre><code>kp.metrics.record_operation(success=True, duration=0.05)
kp.metrics.coffee.drink(duration=300.0)

# Создание метрик
counter = kp.Counter("name", "desc")
gauge = kp.Gauge("name", "desc")
histogram = kp.Histogram("name")
timer = kp.Timer("name")</code></pre>

<hr>

<h2 id="logging">📝 Логирование</h2>

<pre><code>kp.logger.info("Информация")
kp.logger.warning("Предупреждение")
kp.logger.error("Ошибка")
kp.logger.coffee("Кофе-брейк!")
kp.logger.kostyl("Костыль применён")
kp.logger.nuclear("Ядерная ошибка!")</code></pre>

<hr>

<h2 id="async">🔄 Асинхронные костыли</h2>

<pre><code>@kp.async_safe(fallback=None)
@kp.async_retry(max_attempts=3)

breaker = kp.AsyncCircuitBreaker(failure_threshold=5)
limiter = kp.AsyncRateLimiter(max_calls=10, period=1.0)
queue = kp.AsyncKostylQueue(maxsize=100)
manager = kp.TaskManager()</code></pre>

<hr>

<h2 id="patcher">💉 Патчер (AST)</h2>

<pre><code>kp.patch_string("x = a / b", add_safety=True)
kp.patch_file("script.py", output_path="fixed.py")
kp.patch_directory("./src", aggressive=True)
kp.create_patched_copy("script.py")</code></pre>

<hr>

<h2 id="monkey">🐒 Monkey Patcher (Runtime)</h2>

<pre><code>from kostylpy.monkey_patcher import monkey

monkey.patch("module.func", new_func)
monkey.rollback()
monkey.rollback_all()
monkey.report()

BuiltinPatches.patch_all()
kp.patch_all_the_things()</code></pre>

<hr>

<h2 id="constants">📋 Константы</h2>

<pre><code>from kostylpy.constants import (
    KOSTYLPY_VERSION,     # "3.0.0-beta-kostyl"
    PANIC_THRESHOLD,       # 42
    MAGIC_NUMBER,          # 42
    Emoji,                 # Emoji.KOSTYL, Emoji.COFFEE...
    Colors,                # Colors.RED, Colors.GREEN...
)</code></pre>

<hr>

<h2 id="full-example">🎯 Полный пример</h2>

<pre><code>import kostylpy as kp

kp.config.debug = True

@kp.safe(fallback={"status": "error"})
@kp.retry(max_attempts=3, delay=0.1)
def get_user(user_id):
    with kp.KostylContext("запрос"):
        kp.TypeValidator(int).validate(user_id).raise_if_invalid()
        user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        kp.metrics.record_operation(success=True)
        return user

user = get_user(42)
kp.logger.info(f"Пользователь: {user}")
print(kp.core.report())</code></pre>

<hr>

<p align="center">
    🦿 Документация написана на костылях. Если что-то непонятно — читайте исходники.
</p>