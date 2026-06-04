<h1 align="center">
    <img src="assets/logo.png" alt="kostylpy" width="400" onerror="this.style.display='none'">
    <br>
    🦿 kostylpy
</h1>

<p align="center">
    <strong>Профессиональная библиотека костылей для Python</strong>
    <br>
    <em>"Работает — не трогай. Не работает — добавь костылей."</em>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/version-3.0.0--beta--kostyl-blue" alt="Version">
    <img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/license-WTFPL%2BKostyl-green.svg" alt="License">
    <img src="https://img.shields.io/badge/coffee-required-brown.svg" alt="Coffee">
    <img src="https://img.shields.io/badge/status-works%20on%20crutches-orange.svg" alt="Status">
    <img src="https://img.shields.io/badge/tests-50%2B-brightgreen.svg" alt="Tests">
    <img src="https://img.shields.io/badge/modules-15-blueviolet.svg" alt="Modules">
</p>

<p align="center">
    <b>
        <a href="#установка">📦 Установка</a> •
        <a href="#быстрый-старт">🚀 Быстрый старт</a><br>
        <a href="#возможности">🎯 Возможности</a> •
        <a href="#cli">🖥️ CLI</a> •
        <a href="#примеры">🎮 Примеры</a><br>
        <a href="#структура">📁 Структура</a> •
        <a href="#тесты">🧪 Тесты</a> •
        <a href="#лицензия">📜 Лицензия</a>
    </b>
</p>

<hr>

<h2>🤔 Что это?</h2>

<p>
    Просто импортируй этот модуль, и весь твой код станет <strong>неубиваемым</strong>.
    Серьёзно. Мы патчим всё: <code>print</code>, <code>open</code>, <code>import</code>,
    деление, индексы, атрибуты — даже сам интерпретатор начинает работать через костыли.
</p>

<hr>

<h2 id="установка">📦 Установка</h2>

<pre><code>pip install kostylpy</code></pre>

<h3>Из исходников:</h3>
<pre><code>git clone https://github.com/become-a-human/kostylpy.git
cd kostylpy
pip install -e .</code></pre>

<h3>С опциональными зависимостями:</h3>
<pre><code>pip install kostylpy[all]     # Всё сразу
pip install kostylpy[yaml]    # YAML конфиги
pip install kostylpy[psutil]  # Метрики памяти</code></pre>

<hr>

<h2 id="быстрый-старт">🚀 Быстрый старт</h2>

<pre><code>import kostylpy as kp

# Всё! Теперь ваш код под защитой!

print("Hello World!")  # Никогда не падает

f = open("/nonexistent/file.txt")  # Не падает!
print(f.read())  # ""

import super_mega_library  # Не падает!

@kp.safe(fallback="Всё ок!")
def risky_function():
    raise ValueError("Ошибка!")

print(risky_function())  # "Всё ок!"</code></pre>

<hr>

<h2 id="возможности">🎯 Основные возможности</h2>

<h3>🛡️ Декораторы</h3>
<pre><code>@kp.safe(fallback="запасное значение")
def api_call():
    return requests.get("https://api.example.com")

@kp.retry(max_attempts=3, delay=0.1, backoff=2.0)
def flaky_operation():
    return connect_to_database()

@kp.fallback(0)
def divide(a, b):
    return a / b

@kp.cached(max_size=128, ttl=60)
def expensive_computation(x, y):
    time.sleep(1)
    return x * y</code></pre>

<h3>📦 Контекстные менеджеры</h3>
<pre><code>with kp.KostylContext("опасная операция"):
    result = 1 / 0  # Не упадёт!

with kp.TimerContext("запрос к БД") as timer:
    db.query("SELECT * FROM users")
print(f"Запрос занял {timer.elapsed:.2f}с")

with kp.SafeFileContext("config.json", "r") as f:
    config = json.load(f.read())</code></pre>

<h3>✅ Валидаторы</h3>
<pre><code>kp.TypeValidator(int).validate(42).is_valid       # True
kp.StringValidator(min_length=3, max_length=50)
kp.EmailValidator().validate("user@example.com").is_valid
kp.PasswordValidator(min_length=8, require_emoji=True)  # 🔒</code></pre>

<h3>📊 Утилиты</h3>
<pre><code>data = kp.DotDict({'users': [{'name': 'Alice'}]})
kp.safe_get(data, 'users.0.name', default='Unknown')  # 'Alice'

kp.safe_divide(100, 0, default=float('inf'))  # float('inf')

items = kp.SafeList([1, 2, 3], default=0)
items[100]  # 0, не IndexError!

kp.human_readable_size(1234567)   # "1.2 МБ"
kp.time_ago(3661)                 # "1 час назад"</code></pre>

<h3>🔄 Асинхронные костыли</h3>
<pre><code>@kp.async_safe(fallback=None)
async def fetch_data(url):
    return await response.json()

breaker = kp.AsyncCircuitBreaker(failure_threshold=5)
result = await breaker.call(risky_async, arg1)

limiter = kp.AsyncRateLimiter(max_calls=10, period=1.0)
await limiter.acquire()</code></pre>

<h3>📈 Метрики и логирование</h3>
<pre><code>kp.metrics.record_operation(success=True, duration=0.05)
kp.metrics.coffee.drink(duration=300.0)

kp.logger.info("Система запущена")
kp.logger.warning("Заканчивается кофе!")
kp.logger.coffee("Кофе-брейк!")
kp.logger.kostyl("Применён костыль")</code></pre>

<hr>

<h2 id="cli">🖥️ CLI</h2>

<pre><code>python -m kostylpy run main.py
python -m kostylpy scan main.py
python -m kostylpy patch main.py -o fixed.py
python -m kostylpy patch ./project --aggressive
python -m kostylpy check
python -m kostylpy report
python -m kostylpy version
python -m kostylpy help</code></pre>

<hr>

<h2 id="структура">📁 Структура проекта</h2>

<pre><code>kostylpy/
├── kostylpy/
│   ├── __init__.py
│   ├── __main__.py
│   ├── core.py
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── utils.py
│   ├── decorators.py
│   ├── context_managers.py
│   ├── validators.py
│   ├── factories.py
│   ├── interceptors.py
│   ├── metrics.py
│   ├── logging_kostyl.py
│   ├── async_kostyl.py
│   ├── patcher.py
│   ├── patterns.py
│   └── monkey_patcher.py
├── tests/
│   ├── test_core.py
│   ├── test_decorators.py
│   ├── test_patcher.py
│   ├── test_interceptors.py
│   └── test_integration.py
├── examples/
│   ├── hello_world.py
│   ├── web_server.py
│   ├── data_science.py
│   └── production.py
├── docs/
├── setup.py
├── pyproject.toml
├── LICENSE
└── README.md</code></pre>

<hr>

<h2 id="тесты">🧪 Тесты</h2>

<pre><code># Все тесты
python -m pytest tests/ -v

# Конкретный модуль
python -m pytest tests/test_decorators.py -v

# С coverage
python -m pytest tests/ --cov=kostylpy --cov-report=html</code></pre>

<hr>

<h2 id="примеры">🎮 Примеры</h2>

<table>
    <tr><th>Пример</th><th>Описание</th><th>Запуск</th></tr>
    <tr><td><code>hello_world.py</code></td><td>Базовое использование</td><td><code>python examples/hello_world.py</code></td></tr>
    <tr><td><code>web_server.py</code></td><td>Веб-сервер на костылях</td><td><code>python examples/web_server.py</code></td></tr>
    <tr><td><code>data_science.py</code></td><td>Анализ данных</td><td><code>python examples/data_science.py</code></td></tr>
    <tr><td><code>production.py</code></td><td>Продакшен-система</td><td><code>python examples/production.py</code></td></tr>
</table>

<hr>

<h2 id="лицензия">📜 Лицензия</h2>

<p>
    <strong>WTFPL + Kostyl Clause</strong> — 
    делайте что хотите, но если сломаете — сами виноваты. И добавьте костылей.
</p>
<p>
    📄 <a href="LICENSE">Полный текст лицензии</a>
</p>

<hr>

<h2 align="center">☕ Поддержать проект</h2>

<p align="center">
    Если эта библиотека спасла ваш проект от падения:
</p>

<p align="center">
    ⭐ Поставьте звезду на GitHub •
    ☕ Заварите кофе •
    📢 Расскажите друзьям •
    🔧 Пришлите Pull Request
</p>

<hr>

<h2 align="center">🦿 Философия kostylpy</h2>

<blockquote>
    <p>"Любой код может упасть. Но с достаточным количеством костылей — никогда."</p>
</blockquote>

<blockquote>
    <p>"Костыли — это не баг, а фича. Архитектурное решение."</p>
</blockquote>

<blockquote>
    <p>"Если ваш код работает без костылей — значит вы просто ещё не нашли баги."</p>
</blockquote>

<hr>

<p align="center">
    <strong>Made with 🦿, ☕ and infinite crutches</strong>
    <br>
    <br>
    Kostylpy © 2026 — настоящее и будущее костыльной разработки
    <br>
    <br>
    <a href="#top">К оглавлению</a>
    <br>
</p>

</body>
</html>