<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦿 Kostylpy API Reference</title>
<style>
    /* ═══════════════════════════════════════════════════ */
    /* БАЗОВЫЙ СБРОС */
    /* ═══════════════════════════════════════════════════ */
    * {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    input, textarea, pre, code {
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        user-select: text !important;
    }
    *:focus { outline: none !important; box-shadow: none !important; }

    :root {
        --bg: #0d1117;
        --bg-secondary: #161b22;
        --border: #30363d;
        --text: #c9d1d9;
        --text-secondary: #8b949e;
        --accent: #58a6ff;
        --accent-emphasis: #79c0ff;
        --danger: #f85149;
        --warning: #d2991d;
        --success: #3fb950;
        --purple: #a371f7;
        --orange: #d18616;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.7;
        padding: 20px;
        overflow-x: hidden;
        max-width: 100vw;
    }

    .api-header {
        text-align: center;
        padding: 40px 20px 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 30px;
        max-width: 100%;
    }
    .api-header h1 { font-size: 2.5em; color: var(--accent-emphasis); border: none; margin-bottom: 8px; }
    .api-header .subtitle { color: var(--text-secondary); font-style: italic; font-size: 1.1em; }

    .toc {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 40px;
        max-width: 100%;
    }
    .toc h2 { border: none; margin: 0 0 16px; font-size: 1.3em; color: var(--text); }
    .toc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 8px;
        max-width: 100%;
    }
    .toc-grid a {
        color: var(--accent);
        text-decoration: none;
        padding: 6px 10px;
        border-radius: 6px;
        transition: background 0.15s;
        -webkit-user-select: text;
        -moz-user-select: text;
        user-select: text;
        white-space: nowrap;
    }
    .toc-grid a:hover { background: var(--border); text-decoration: none; }

    h2 {
        color: var(--accent-emphasis);
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        margin: 40px 0 20px;
        font-size: 1.6em;
        max-width: 100%;
    }
    h3 { color: var(--text); margin: 28px 0 12px; font-size: 1.2em; }
    h3 code { font-size: 0.95em; color: var(--accent-emphasis); }
    h4 { color: var(--text-secondary); margin: 20px 0 8px; font-size: 1em; }

    code {
        background: var(--bg-secondary);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
        font-size: 0.88em;
        max-width: 100%;
        display: inline-block;
        vertical-align: top;
    }
    pre {
        background: var(--bg-secondary);
        padding: 18px 20px;
        border-radius: 10px;
        overflow-x: auto;
        border: 1px solid var(--border);
        margin: 12px 0 20px;
        max-width: 100%;
        white-space: pre-wrap;
    }
    pre code { background: none; padding: 0; font-size: 0.85em; line-height: 1.6; }

    a {
        color: var(--accent);
        text-decoration: none;
        -webkit-user-select: text;
        -moz-user-select: text;
        user-select: text;
    }
    a:hover { text-decoration: underline; }
    strong { color: #e6edf3; }
    em { color: var(--text-secondary); }

    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; margin-right: 4px; }
    .badge-class { background: #1a1a3a; color: var(--purple); }
    .badge-method { background: #1a3a2a; color: var(--success); }
    .badge-prop { background: #3a2a1a; color: var(--orange); }

    .params { list-style: none; padding: 0; margin: 8px 0 16px 20px; }
    .params li { padding: 4px 0; color: var(--text-secondary); max-width: 100%; }
    .params li code { color: var(--accent-emphasis); font-weight: 600; }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        max-width: 100%;
        display: block;
        overflow-x: auto;
    }
    th, td {
        padding: 10px 14px;
        border: 1px solid var(--border);
        text-align: left;
        max-width: 45vw;
        word-wrap: break-word;
    }
    th { background: var(--bg-secondary); color: var(--accent); font-weight: 600; }

    .api-footer {
        text-align: center;
        padding: 30px 20px;
        margin-top: 40px;
        border-top: 1px solid var(--border);
        color: var(--text-secondary);
        font-style: italic;
        max-width: 100%;
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 30px 0; }

    @media (max-width: 768px) {
        body { padding: 10px; }
        .toc-grid { grid-template-columns: 1fr 1fr; }
        pre { font-size: 0.75em; }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.3em; }
        .toc-grid a { white-space: normal; }
    }
    @media (max-width: 480px) {
        body { padding: 8px; }
        .toc-grid { grid-template-columns: 1fr; }
        pre code { font-size: 0.7em; }
        .api-header { padding: 20px 10px; }
    }
</style>
</head>
<body>

<div class="container">

    <div class="api-header">
        <h1>🦿 Kostylpy API Reference</h1>
        <p class="subtitle">
            Полная документация по API библиотеки kostylpy.<br>
            <small>(Насколько "полная" может быть документация к костылям.)</small>
        </p>
    </div>

    <div class="toc">
        <h2>📑 Оглавление</h2>
        <div class="toc-grid">
            <a href="#core">🏗️ Ядро</a>
            <a href="#config">⚙️ Конфигурация</a>
            <a href="#decorators">🛡️ Декораторы</a>
            <a href="#context">📦 Контекстные менеджеры</a>
            <a href="#validators">✅ Валидаторы</a>
            <a href="#utils">🔧 Утилиты</a>
            <a href="#factories">🏭 Фабрики</a>
            <a href="#interceptors">🕵️ Перехватчики</a>
            <a href="#metrics">📊 Метрики</a>
            <a href="#logging">📝 Логирование</a>
            <a href="#async">🔄 Асинхронные костыли</a>
            <a href="#patcher">💉 Патчер</a>
            <a href="#monkey">🐒 Monkey Patcher</a>
            <a href="#constants">📋 Константы</a>
            <a href="#full-example">🎯 Полный пример</a>
        </div>
    </div>

    <!-- CORE -->
    <h2 id="core">🏗️ Ядро (Core)</h2>

    <h3><code>kostylpy.KostylPy</code> <span class="badge badge-class">class singleton</span></h3>
    <p>Главный класс библиотеки. Один на весь процесс.</p>

    <pre><code>from kostylpy.core import KostylPy
core = KostylPy()</code></pre>

    <h4>Свойства <span class="badge badge-prop">props</span></h4>
    <ul class="params">
        <li><code>status</code> — <em>"активно"</em>, <em>"деградировано"</em>, <em>"паника!"</em></li>
        <li><code>is\_active</code> → <code>bool</code></li>
        <li><code>is\_panic</code> → <code>bool</code></li>
        <li><code>uptime</code> → <code>float</code> (секунды)</li>
        <li><code>config</code> — экземпляр <code>KostylConfig</code></li>
        <li><code>logger</code> — экземпляр <code>KostylLogger</code></li>
        <li><code>metrics</code> — экземпляр <code>KostylMetrics</code></li>
    </ul>

    <h4>Методы <span class="badge badge-method">methods</span></h4>
    <ul class="params">
        <li><code>health\_check()</code> → <code>dict</code></li>
        <li><code>stats()</code> → <code>dict</code></li>
        <li><code>report()</code> → <code>str</code></li>
        <li><code>get\_module(name)</code> → <code>module | None</code></li>
        <li><code>is\_module\_loaded(name)</code> → <code>bool</code></li>
        <li><code>loaded\_modules()</code> → <code>list[str]</code></li>
    </ul>

    <hr>

    <!-- CONFIG -->
    <h2 id="config">⚙️ Конфигурация (Config)</h2>

    <h3><code>kostylpy.config</code> <span class="badge badge-class">singleton</span></h3>
    <p>Глобальный экземпляр конфигурации. Загружается из файлов, переменных окружения и магии.</p>

    <pre><code>from kostylpy.config import config, get\_config

config.get('debug')                    # False
config.get('network.default\_timeout')  # 30.0

# Быстрый доступ
config.debug              # False
config.panic\_threshold    # 42
config.coffee\_required    # True

# Установка
config.set('debug', True, reason="Нужна отладка")</code></pre>

    <h4>Свойства</h4>
    <ul class="params">
        <li><code>debug</code>, <code>verbose</code>, <code>log\_level</code></li>
        <li><code>panic\_threshold</code> — порог паники (по умолчанию <strong>42</strong>)</li>
        <li><code>coffee\_required</code> — <code>True</code> всегда</li>
        <li><code>default\_timeout</code>, <code>retry\_count</code></li>
    </ul>

    <h4>Методы</h4>
    <ul class="params">
        <li><code>get(key, default=None)</code> — значение с точками: <code>'network.timeout'</code></li>
        <li><code>set(key, value)</code> / <code>has(key)</code> / <code>all()</code></li>
        <li><code>load\_file(path)</code> / <code>load\_env(prefix)</code> / <code>load\_all()</code></li>
        <li><code>save(path)</code> / <code>validate()</code> / <code>report()</code></li>
    </ul>

    <hr>

    <!-- DECORATORS -->
    <h2 id="decorators">🛡️ Декораторы</h2>

    <h3><code>@kostylpy.safe</code> <span class="badge badge-method">decorator</span></h3>
    <p>Функция <strong>никогда не упадёт</strong>.</p>
    <pre><code>@kp.safe(fallback="всё ок")
def risky():
    raise ValueError("Ошибка!")
result = risky()  # "всё ок"</code></pre>
    <h4>Параметры</h4>
    <ul class="params">
        <li><code>fallback</code> — значение при ошибке</li>
        <li><code>log\_errors</code> (<code>bool</code>)</li>
        <li><code>reraise</code> (<code>bool | list[type]</code>) — пробросить исключения</li>
        <li><code>on\_error</code> (<code>callable</code>) — обработчик</li>
        <li><code>max\_failures</code> (<code>int</code>) — лимит ошибок</li>
    </ul>

    <h3><code>@kostylpy.retry</code> <span class="badge badge-method">decorator</span></h3>
    <pre><code>@kp.retry(max\_attempts=3, delay=0.1, backoff=2.0)
def flaky():
    return api.call()</code></pre>
    <h4>Параметры</h4>
    <ul class="params">
        <li><code>max\_attempts</code> (по умолчанию <strong>3</strong>)</li>
        <li><code>delay</code> (<code>float | (min, max)</code>)</li>
        <li><code>backoff</code> — экспоненциальный множитель</li>
        <li><code>exceptions</code> — что ловить</li>
        <li><code>jitter</code> — случайная дрожь</li>
        <li><code>fallback</code> — после всех попыток</li>
    </ul>

    <h3><code>@kostylpy.fallback</code></h3>
    <pre><code>@kp.fallback(0)
def divide(a, b): return a / b</code></pre>

    <h3><code>@kostylpy.cached</code></h3>
    <pre><code>@kp.cached(max\_size=128, ttl=60)
def expensive(x, y): ...</code></pre>

    <h3><code>@kostylpy.deprecated\_kostyl</code></h3>
    <pre><code>@kp.deprecated\_kostyl(reason="старый", alternative="новый")
def old\_func(): ...</code></pre>

    <hr>

    <!-- CONTEXT MANAGERS -->
    <h2 id="context">📦 Контекстные менеджеры</h2>

    <h3><code>KostylContext</code></h3>
    <pre><code>with kp.KostylContext("опасный блок", suppress=True):
    1 / 0  # не упадёт!</code></pre>

    <h3><code>TimerContext</code></h3>
    <pre><code>with kp.TimerContext("замер") as t:
    do\_work()
print(t.elapsed)  # float</code></pre>

    <h3><code>SafeFileContext</code></h3>
    <pre><code>with kp.SafeFileContext("config.json", "r") as f:
    data = f.read()</code></pre>

    <h3><code>kostyl\_block</code></h3>
    <pre><code>with kp.kostyl\_block():
    risky()</code></pre>

    <hr>

    <!-- VALIDATORS -->
    <h2 id="validators">✅ Валидаторы</h2>

    <table>
        <tr><th>Валидатор</th><th>Пример</th></tr>
        <tr><td><code>TypeValidator</code></td><td><code>kp.TypeValidator(int)</code></td></tr>
        <tr><td><code>RangeValidator</code></td><td><code>kp.RangeValidator(min=0, max=100)</code></td></tr>
        <tr><td><code>StringValidator</code></td><td><code>kp.StringValidator(min\_length=3, pattern=r'^\w+$')</code></td></tr>
        <tr><td><code>EmailValidator</code></td><td><code>kp.EmailValidator()</code></td></tr>
        <tr><td><code>PasswordValidator</code></td><td><code>kp.PasswordValidator(min\_length=8, require\_emoji=True)</code></td></tr>
        <tr><td><code>NullValidator</code></td><td><code>kp.NullValidator()</code></td></tr>
        <tr><td><code>FileValidator</code></td><td><code>kp.FileValidator(max\_size\_mb=10)</code></td></tr>
        <tr><td><code>DataValidator</code></td><td><code>kp.DataValidator(schema={"name": StringValidator()})</code></td></tr>
    </table>

    <h3><code>ValidationResult</code></h3>
    <pre><code>result = validator.validate(value)
result.is\_valid         # bool
result.errors           # list[ValidationError]
result.raise\_if\_invalid()
result.get\_or\_default(default)</code></pre>

    <h3><code>ValidationPipeline</code></h3>
    <pre><code>pipe = kp.ValidationPipeline()
pipe.add(kp.TypeValidator(int))
pipe.add(kp.RangeValidator(min=0))
pipe.validate(42)</code></pre>

    <hr>

    <!-- UTILS -->
    <h2 id="utils">🔧 Утилиты</h2>

    <h3>Безопасные структуры данных</h3>
    <pre><code>d = kp.DotDict({'a': {'b': 1}})
d.a.b  # 1

lst = kp.SafeList([1,2,3], default=0)
lst[100]  # 0</code></pre>

    <h3>Безопасный доступ</h3>
    <pre><code>kp.safe\_get(data, 'users.0.name', default='?')  # 'Alice'
kp.safe\_set(data, 'users.0.age', 30)
kp.safe\_divide(100, 0, default=0)  # 0
kp.clamp(value, 0, 100)</code></pre>

    <h3>Форматирование</h3>
    <pre><code>kp.human\_readable\_size(1234567)  # "1.2 МБ"
kp.time\_ago(3661)                # "1 час назад"
kp.truncate("длинный...", 10)    # "длинный..."
kp.slugify("Привет, Мир!")      # "privet-mir"
kp.obfuscate("pass123", 3)      # "pas****"</code></pre>

    <h3>Генераторы</h3>
    <pre><code>kp.random\_string(16)
kp.random\_email()
kp.random\_name()
kp.random\_ip()
kp.random\_emoji()</code></pre>

    <h3>Конвертеры</h3>
    <pre><code>kp.to\_json(obj)
kp.from\_json(text)
kp.to\_base64("hello")
kp.to\_hash("data")</code></pre>

    <hr>

    <!-- FACTORIES -->
    <h2 id="factories">🏭 Фабрики</h2>

    <pre><code># Исключения
exc = kp.ExceptionFactory().produce("ValueError", "Всё плохо")

# Заглушки
stub = kp.StubFactory().produce("function", return\_value=42)

# Случайные костыли
product = kp.RandomKostylFactory().produce()

# Мета-фабрика (создаёт другие фабрики)
factory = kp.MetaFactory().produce("stub")</code></pre>

    <hr>

    <!-- INTERCEPTORS -->
    <h2 id="interceptors">🕵️ Перехватчики</h2>

    <pre><code># Перехват функции
kp.FunctionInterceptor(target\_func=my\_func, mode=kp.InterceptMode.LOG\_ONLY)

# Глобальный перехват
kp.intercept\_all()

# Шпионаж
kp.spy\_on\_function(my\_func)

# Блокировка импортов
kp.block\_imports('os', 'subprocess')</code></pre>

    <hr>

    <!-- METRICS -->
    <h2 id="metrics">📊 Метрики</h2>

    <pre><code>kp.metrics.record\_operation(success=True, duration=0.05)
kp.metrics.coffee.drink(duration=300.0)

# Создание метрик
counter = kp.Counter("name", "desc")
gauge = kp.Gauge("name", "desc")
histogram = kp.Histogram("name")
timer = kp.Timer("name")</code></pre>

    <hr>

    <!-- LOGGING -->
    <h2 id="logging">📝 Логирование</h2>

    <pre><code>kp.logger.info("Информация")
kp.logger.warning("Предупреждение")
kp.logger.error("Ошибка")
kp.logger.coffee("Кофе-брейк!")
kp.logger.kostyl("Костыль применён")
kp.logger.nuclear("Ядерная ошибка!")</code></pre>

    <hr>

    <!-- ASYNC -->
    <h2 id="async">🔄 Асинхронные костыли</h2>

    <pre><code>@kp.async\_safe(fallback=None)
@kp.async\_retry(max\_attempts=3)

breaker = kp.AsyncCircuitBreaker(failure\_threshold=5)
limiter = kp.AsyncRateLimiter(max\_calls=10, period=1.0)
queue = kp.AsyncKostylQueue(maxsize=100)
manager = kp.TaskManager()</code></pre>

    <hr>

    <!-- PATCHER -->
    <h2 id="patcher">💉 Патчер (AST)</h2>

    <pre><code>kp.patch\_string("x = a / b", add\_safety=True)
kp.patch\_file("script.py", output\_path="fixed.py")
kp.patch\_directory("./src", aggressive=True)
kp.create\_patched\_copy("script.py")</code></pre>

    <hr>

    <!-- MONKEY PATCHER -->
    <h2 id="monkey">🐒 Monkey Patcher (Runtime)</h2>

    <pre><code>from kostylpy.monkey\_patcher import monkey

monkey.patch("module.func", new\_func)
monkey.rollback()
monkey.rollback\_all()
monkey.report()

BuiltinPatches.patch\_all()
kp.patch\_all\_the\_things()</code></pre>

    <hr>

    <!-- CONSTANTS -->
    <h2 id="constants">📋 Константы</h2>

    <pre><code>from kostylpy.constants import (
    KOSTYLPY\_VERSION,     # "3.0.0-beta-kostyl"
    PANIC\_THRESHOLD,       # 42
    MAGIC\_NUMBER,          # 42
    Emoji,                 # Emoji.KOSTYL, Emoji.COFFEE...
    Colors,                # Colors.RED, Colors.GREEN...
)</code></pre>

    <hr>

    <!-- FULL EXAMPLE -->
    <h2 id="full-example">🎯 Полный пример</h2>

    <pre><code>import kostylpy as kp

kp.config.debug = True

@kp.safe(fallback={"status": "error"})
@kp.retry(max\_attempts=3, delay=0.1)
def get\_user(user\_id):
    with kp.KostylContext("запрос"):
        kp.TypeValidator(int).validate(user\_id).raise\_if\_invalid()
        user = db.query(f"SELECT * FROM users WHERE id = {user\_id}")
        kp.metrics.record\_operation(success=True)
        return user

user = get\_user(42)
kp.logger.info(f"Пользователь: {user}")
print(kp.core.report())</code></pre>

    <div class="api-footer">
        <p>🦿 Документация написана на костылях. Если что-то непонятно — читайте исходники.</p>
        <p><small>kostylpy v3.0.0-beta-kostyl-enterprise-edition</small></p>
    </div>

</div>
</body>
</html>