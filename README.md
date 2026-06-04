<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦿 kostylpy — Профессиональная библиотека костылей для Python</title>
<style>
    /* ═══════════════════════════════════════════════════ */
    /* БАЗОВЫЙ СБРОС И ЗАЩИТА ОТ ВЫХОДА ЗА ЭКРАН */
    /* ═══════════════════════════════════════════════════ */
    * {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        hyphens: auto;
        /* Запрет выделения */
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        /* Убираем синюю обводку */
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    /* Разрешаем выделение только в полях ввода и коде */
    input, textarea, pre, code {
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        user-select: text !important;
    }

    /* Убираем обводку при фокусе */
    *:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    input:focus, textarea:focus {
        outline: none !important;
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3) !important;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background: #0d1117;
        color: #c9d1d9;
        line-height: 1.6;
        overflow-x: hidden;
        max-width: 100vw;
    }

    h1, h2, h3 {
        color: #58a6ff;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        max-width: 100%;
        overflow-wrap: break-word;
    }
    h1 { text-align: center; border: none; font-size: 2.5em; }

    code {
        background: #161b22;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
        max-width: 100%;
        display: inline-block;
        vertical-align: top;
    }
    pre {
        background: #161b22;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid #30363d;
        max-width: 100%;
        white-space: pre-wrap;
    }
    pre code { background: none; padding: 0; }

    a {
        color: #58a6ff;
        text-decoration: none;
        -webkit-user-select: text;
        -moz-user-select: text;
        user-select: text;
    }
    a:hover { text-decoration: underline; }

    blockquote {
        border-left: 3px solid #30363d;
        margin: 16px 0;
        padding: 8px 16px;
        color: #8b949e;
        background: #161b22;
        border-radius: 4px;
        max-width: 100%;
    }
    hr { border: none; border-top: 1px solid #30363d; margin: 32px 0; }
    img { max-width: 100%; }
    .badge { display: inline-block; margin: 4px; }

    .section-nav {
        text-align: center;
        margin: 20px 0;
        max-width: 100%;
    }
    .section-nav a { margin: 0 8px; font-weight: bold; }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0;
        max-width: 100%;
    }
    .feature-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        max-width: 100%;
        min-width: 0;
        /* Убираем обводку при нажатии */
        -webkit-tap-highlight-color: transparent;
    }
    .feature-card h3 { border: none; margin-top: 0; padding: 0; }

    .warning-box {
        background: #2d1b1b;
        border: 1px solid #f85149;
        border-radius: 8px;
        padding: 16px;
        margin: 20px 0;
        max-width: 100%;
    }
    .warning-box h2 { color: #f85149; }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        max-width: 100%;
        display: block;
        overflow-x: auto;
    }
    th, td {
        padding: 8px 12px;
        border: 1px solid #30363d;
        text-align: left;
        max-width: 50vw;
        word-wrap: break-word;
    }
    th { background: #161b22; }

    .footer {
        text-align: center;
        margin-top: 40px;
        color: #8b949e;
        max-width: 100%;
    }

    /* Мобильные */
    @media (max-width: 768px) {
        body { padding: 10px; }
        .feature-grid { grid-template-columns: 1fr; }
        pre { font-size: 0.75em; }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.3em; }
    }
    @media (max-width: 480px) {
        body { padding: 8px; }
        pre code { font-size: 0.7em; }
    }
</style>
</head>
<body>

<h1 align="center">
    <img src="assets/logo.png" alt="kostylpy" width="420" onerror="this.style.display='none'">
    <br>
    🦿 kostylpy
</h1>

<p align="center">
    <strong>Профессиональная библиотека костылей для Python</strong>
    <br>
    <em>"Работает — не трогай. Не работает — добавь костылей."</em>
</p>

<p align="center">
    <span class="badge"><img src="https://img.shields.io/badge/version-3.0.0--beta--kostyl-blue" alt="Version"></span>
    <span class="badge"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python"></span>
    <span class="badge"><img src="https://img.shields.io/badge/license-WTFPL%2BKostyl-green.svg" alt="License"></span>
    <span class="badge"><img src="https://img.shields.io/badge/coffee-required-brown.svg" alt="Coffee"></span>
    <span class="badge"><img src="https://img.shields.io/badge/status-works%20on%20crutches-orange.svg" alt="Status"></span>
</p>

<p align="center" class="section-nav">
    <b>
        <a href="#install">📦 Установка</a> •
        <a href="#quickstart">🚀 Быстрый старт</a> •
        <a href="#features">🎯 Возможности</a> •
        <a href="#cli">🖥️ CLI</a> •
        <a href="#structure">📁 Структура</a> •
        <a href="#examples">🎮 Примеры</a> •
        <a href="#tests">🧪 Тесты</a> •
        <a href="#license">📜 Лицензия</a>
    </b>
</p>

<hr>

<h2>🤔 Что это?</h2>

<p>Просто импортируй этот модуль, и весь твой код станет <strong>неубиваемым</strong>. Мы патчим всё: <code>print</code>, <code>open</code>, <code>import</code>, деление, индексы, атрибуты — даже сам интерпретатор начинает работать через костыли.</p>

<div class="feature-grid">
    <div class="feature-card">
        <h3>🛡️ Защита от падений</h3>
        <p>Ваш код никогда не упадёт. Никогда. Серьёзно.</p>
    </div>
    <div class="feature-card">
        <h3>🔄 Авто-восстановление</h3>
        <p>Повторные попытки, fallback-значения, circuit breaker.</p>
    </div>
    <div class="feature-card">
        <h3>📊 Метрики и логи</h3>
        <p>Полный мониторинг костылей в реальном времени.</p>
    </div>
    <div class="feature-card">
        <h3>☕ Кофе-метрика</h3>
        <p>Считает количество выпитого кофе. Жизненно важно.</p>
    </div>
</div>

<hr>

<h2 id="install">📦 Установка</h2>

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

<h2 id="quickstart">🚀 Быстрый старт</h2>

<pre><code>import kostylpy as kp

# Всё! Теперь ваш код под защитой!

print("Hello World!")  # Никогда не падает

f = open("/nonexistent/file.txt")  # Не падает!
print(f.read())  # ""

import super\_mega\_library  # Не падает!

@kp.safe(fallback="Всё ок!")
def risky\_function():
    raise ValueError("Ошибка!")

print(risky\_function())  # "Всё ок!"</code></pre>

<hr>

<h2 id="features">🎯 Основные возможности</h2>

<h3>🛡️ Декораторы</h3>
<pre><code>@kp.safe(fallback="запасное значение")
def api\_call():
    return requests.get("https://api.example.com")

@kp.retry(max\_attempts=3, delay=0.1, backoff=2.0)
def flaky\_operation():
    return connect\_to\_database()

@kp.fallback(0)
def divide(a, b):
    return a / b

@kp.cached(max\_size=128, ttl=60)
def expensive\_computation(x, y):
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
<pre><code>kp.TypeValidator(int).validate(42).is\_valid       # True
kp.StringValidator(min\_length=3, max\_length=50)
kp.EmailValidator().validate("user@example.com").is\_valid
kp.PasswordValidator(min\_length=8, require\_emoji=True)  # 🔒</code></pre>

<h3>📊 Утилиты</h3>
<pre><code>data = kp.DotDict({'users': [{'name': 'Alice'}]})
kp.safe\_get(data, 'users.0.name', default='Unknown')  # 'Alice'

kp.safe\_divide(100, 0, default=float('inf'))  # float('inf')

items = kp.SafeList([1, 2, 3], default=0)
items[100]  # 0, не IndexError!

kp.human\_readable\_size(1234567)   # "1.2 МБ"
kp.time\_ago(3661)                 # "1 час назад"</code></pre>

<h3>📈 Метрики и логирование</h3>
<pre><code>kp.metrics.record\_operation(success=True, duration=0.05)
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

<h2 id="structure">📁 Структура проекта</h2>

<pre><code>kostylpy/
├── kostylpy/
│   ├── \_\_init\_\_.py
│   ├── \_\_main\_\_.py
│   ├── core.py
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── utils.py
│   ├── decorators.py
│   ├── context\_managers.py
│   ├── validators.py
│   ├── factories.py
│   ├── interceptors.py
│   ├── metrics.py
│   ├── logging\_kostyl.py
│   ├── async\_kostyl.py
│   ├── patcher.py
│   ├── patterns.py
│   └── monkey\_patcher.py
├── tests/
│   ├── test\_core.py
│   ├── test\_decorators.py
│   ├── test\_patcher.py
│   ├── test\_interceptors.py
│   └── test\_integration.py
├── examples/
│   ├── hello\_world.py
│   ├── web\_server.py
│   ├── data\_science.py
│   └── production.py
├── docs/
├── setup.py
├── pyproject.toml
├── LICENSE
└── README.md</code></pre>

<hr>

<h2 id="tests">🧪 Тесты</h2>

<pre><code># Все тесты
python -m pytest tests/ -v

# Конкретный модуль
python -m pytest tests/test\_decorators.py -v

# С coverage
python -m pytest tests/ --cov=kostylpy --cov-report=html</code></pre>

<hr>

<h2 id="examples">🎮 Примеры</h2>

<table>
    <tr><th>Пример</th><th>Описание</th><th>Запуск</th></tr>
    <tr><td><code>hello\_world.py</code></td><td>Базовое использование</td><td><code>python examples/hello\_world.py</code></td></tr>
    <tr><td><code>web\_server.py</code></td><td>Веб-сервер на костылях</td><td><code>python examples/web\_server.py</code></td></tr>
    <tr><td><code>data\_science.py</code></td><td>Анализ данных</td><td><code>python examples/data\_science.py</code></td></tr>
    <tr><td><code>production.py</code></td><td>Продакшен-система</td><td><code>python examples/production.py</code></td></tr>
</table>

<hr>

<div class="warning-box">
    <h2>⚠️ Дисклеймер</h2>
    <p><strong>Эта библиотека — шутка. Серьёзно.</strong></p>
    <p>Не используйте её в реальном продакшене. Хотя... она и так работает. На костылях.</p>
    <ul>
        <li>Может замедлить код в 1000 раз</li>
        <li>Может скрыть реальные ошибки</li>
        <li>Вызывает привыкание к костылям</li>
    </ul>
</div>

<hr>

<h2 id="license">📜 Лицензия</h2>

<div class="section" style="text-align: center;">
    <p style="font-size: 1.1em; margin-bottom: 16px;">
        Эта библиотека распространяется под лицензией
    </p>

    <div style="
        background: linear-gradient(135deg, #1a1a2e, #161b22);
        border: 1px solid var(--purple);
        border-radius: 12px;
        padding: 20px;
        display: inline-block;
    ">
        <p style="font-size: 1.3em; margin: 0; color: var(--purple);">
            <strong>WTFPL</strong>
        </p>
        <p style="margin: 4px 0; color: var(--text-secondary);">
            + 🦿 <strong>Kostyl Clause</strong>
        </p>
    </div>

    <div class="principles-grid" style="margin-top: 16px;">
        <div class="principle-card" style="text-align: center;">
            <div style="font-size: 2em;">✅</div>
            <div class="label" style="margin-top: 4px;">Делайте что хотите</div>
        </div>
        <div class="principle-card" style="text-align: center;">
            <div style="font-size: 2em;">🦿</div>
            <div class="label" style="margin-top: 4px;">Добавляйте костыли</div>
        </div>
        <div class="principle-card" style="text-align: center;">
            <div style="font-size: 2em;">☕</div>
            <div class="label" style="margin-top: 4px;">Пейте кофе</div>
        </div>
    </div>

    <p style="margin-top: 16px; color: var(--text-secondary);">
        📄 Всё остальное — в <a href="LICENSE">полном тексте лицензии</a>.
        <br>
        <small>(Спойлер: там тоже ничего важного.)</small>
    </p>
</div>

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