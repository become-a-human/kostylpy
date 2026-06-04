<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦿 Kostylpy — Примеры использования</title>
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
        --success: #3fb950;
        --warning: #d2991d;
        --danger: #f85149;
        --purple: #a371f7;
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
    .container { max-width: 960px; margin: 0 auto; }

    .header {
        text-align: center;
        padding: 40px 20px 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 30px;
        max-width: 100%;
    }
    .header h1 { font-size: 2.5em; color: var(--accent-emphasis); border: none; margin-bottom: 8px; }
    .header p { color: var(--text-secondary); font-size: 1.1em; }

    h2 {
        color: var(--accent-emphasis);
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        margin: 40px 0 20px;
        font-size: 1.6em;
        max-width: 100%;
    }
    h3 { color: var(--text); margin: 24px 0 12px; font-size: 1.2em; }
    h4 { color: var(--text-secondary); margin: 16px 0 8px; }

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

    .example-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        max-width: 100%;
        min-width: 0;
        -webkit-tap-highlight-color: transparent;
    }
    .example-card h3 { margin-top: 0; border-bottom: 1px solid var(--border); padding-bottom: 12px; }
    .example-card .meta {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin: 8px 0 16px;
        font-size: 0.9em;
        color: var(--text-secondary);
        max-width: 100%;
    }
    .example-card .meta span {
        background: var(--bg);
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid var(--border);
    }

    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; margin-right: 4px; }
    .badge-easy { background: #1a3a2a; color: var(--success); }
    .badge-medium { background: #3a3a1a; color: var(--warning); }
    .badge-hard { background: #2d1b1b; color: var(--danger); }
    .badge-all { background: #1a1a3a; color: var(--purple); }

    .output-block {
        background: #0a0e14;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        font-family: monospace;
        font-size: 0.85em;
        color: #7ee787;
        max-width: 100%;
        overflow-x: auto;
        white-space: pre-wrap;
    }

    .tip {
        background: #1a2e1a;
        border-left: 4px solid var(--success);
        padding: 12px 16px;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
        max-width: 100%;
    }
    .tip strong { color: var(--success); }

    .footer {
        text-align: center;
        padding: 30px 20px;
        margin-top: 40px;
        border-top: 1px solid var(--border);
        color: var(--text-secondary);
        max-width: 100%;
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 30px 0; }

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
        border: 1px solid var(--border);
        text-align: left;
        max-width: 50vw;
        word-wrap: break-word;
    }
    th { background: var(--bg-secondary); }

    @media (max-width: 768px) {
        body { padding: 10px; }
        .example-card .meta { flex-direction: column; gap: 8px; }
        pre { font-size: 0.75em; }
        h1 { font-size: 1.8em; }
    }
</style>
</head>
<body>

    <div class="header">
        <h1>🎮 Примеры использования kostylpy</h1>
        <p>От Hello World до продакшен-системы — всё на костылях</p>
    </div>

    <h2>📑 Содержание</h2>

    <table>
        <tr>
            <th>#</th>
            <th>Пример</th>
            <th>Файл</th>
            <th>Сложность</th>
            <th>Что демонстрирует</th>
        </tr>
        <tr>
            <td>1</td>
            <td><a href="#hello">Hello World</a></td>
            <td><code>hello\_world.py</code></td>
            <td><span class="badge badge-easy">Лёгкий</span></td>
            <td>Базовые фичи: safe, retry, контексты, валидаторы</td>
        </tr>
        <tr>
            <td>2</td>
            <td><a href="#web">Веб-сервер</a></td>
            <td><code>web\_server.py</code></td>
            <td><span class="badge badge-medium">Средний</span></td>
            <td>Роутер, БД, сессии, валидация запросов</td>
        </tr>
        <tr>
            <td>3</td>
            <td><a href="#ds">Data Science</a></td>
            <td><code>data\_science.py</code></td>
            <td><span class="badge badge-medium">Средний</span></td>
            <td>Статистика, корреляции, регрессия, кластеризация</td>
        </tr>
        <tr>
            <td>4</td>
            <td><a href="#prod">Продакшен</a></td>
            <td><code>production.py</code></td>
            <td><span class="badge badge-hard">Сложный</span></td>
            <td>Логи, метрики, очереди, мониторинг, фоновые процессы</td>
        </tr>
    </table>

    <hr>

    <!-- ============================== -->
    <!-- HELLO WORLD -->
    <!-- ============================== -->
    <div class="example-card" id="hello">
        <h3>1. Hello World на костылях</h3>
        <div class="meta">
            <span>📁 hello\_world.py</span>
            <span><span class="badge badge-easy">Лёгкий</span></span>
            <span>⏱️ ~5 сек</span>
        </div>

        <p>Самый простой пример. Показывает базовые возможности библиотеки на нескольких строках кода.</p>

        <h4>🚀 Запуск</h4>
        <pre><code>cd examples
python hello\_world.py</code></pre>

        <h4>📝 Ключевые моменты</h4>

        <p><strong>Безопасные функции:</strong></p>
        <pre><code>@kp.safe(fallback="Всё сломалось, но мы держимся!")
def greet(name):
    if not isinstance(name, str):
        raise ValueError("Имя должно быть строкой!")
    return f"Привет, {name}!"

print(greet("Мир"))   # "Привет, Мир!"
print(greet(42))       # "Всё сломалось, но мы держимся!"</code></pre>

        <p><strong>Повторные попытки:</strong></p>
        <pre><code>@kp.retry(max\_attempts=5, delay=0.1, fallback="Не удалось")
def unstable\_greeting():
    # Пробует 5 раз, потом сдаётся
    ...</code></pre>

        <p><strong>Защищённый блок:</strong></p>
        <pre><code>with kp.KostylContext("опасная операция"):
    print("Внутри блока...")
    raise RuntimeError("Ошибка!")  # Подавлена!
    print("Это не выполнится")

print("А мы всё ещё живы!")  # Выполнится</code></pre>

        <h4>📊 Пример вывода</h4>
        <div class="output-block">
            ============================================================<br>
            🦿 HELLO WORLD НА КОСТЫЛЯХ<br>
            ============================================================<br>
            <br>
            Hello World!<br>
            Этот print никогда не падает.<br>
            <br>
            📌 Безопасные функции:<br>
            Привет, Мир!<br>
            Всё сломалось, но мы держимся!<br>
            <br>
            📌 Контекстный менеджер:<br>
            &nbsp;&nbsp;&nbsp;Внутри защищённого блока...<br>
            &nbsp;&nbsp;&nbsp;А мы всё ещё живы!<br>
            <br>
            ✅ HELLO WORLD УСПЕШНО ОТРАБОТАЛ
        </div>
    </div>

    <!-- ============================== -->
    <!-- WEB SERVER -->
    <!-- ============================== -->
    <div class="example-card" id="web">
        <h3>2. Веб-сервер на костылях</h3>
        <div class="meta">
            <span>📁 web\_server.py</span>
            <span><span class="badge badge-medium">Средний</span></span>
            <span>⏱️ ~10 сек</span>
        </div>

        <p>Полноценный веб-сервер с роутером, базой данных, сессиями и валидацией. Работает без Flask!</p>

        <h4>🚀 Запуск</h4>
        <pre><code>python examples/web\_server.py</code></pre>

        <h4>📝 Архитектура</h4>

        <table>
            <tr><th>Компонент</th><th>Описание</th></tr>
            <tr><td><code>Database</code></td><td>JSON-база данных с автосохранением</td></tr>
            <tr><td><code>Router</code></td><td>Маршрутизатор запросов</td></tr>
            <tr><td><code>handle\_register</code></td><td>Регистрация с валидацией</td></tr>
            <tr><td><code>handle\_login</code></td><td>Вход с созданием сессии</td></tr>
            <tr><td><code>handle\_profile</code></td><td>Профиль пользователя</td></tr>
        </table>

        <h4>📝 Ключевые моменты</h4>

        <p><strong>Валидация запросов:</strong></p>
        <pre><code>username\_validator = kp.StringValidator(min\_length=3, max\_length=30)
password\_validator = kp.PasswordValidator(min\_length=6)
email\_validator = kp.EmailValidator()

if not username\_validator.validate(username).is\_valid:
    errors.append('Имя пользователя должно быть от 3 до 30 символов')</code></pre>

        <p><strong>Безопасная БД:</strong></p>
        <pre><code>@kp.safe(fallback=None)
def get\_user(self, user\_id: str):
    return self.\_data.users.get(user\_id)</code></pre>

        <p><strong>Нагрузочный тест:</strong></p>
        <pre><code># 20 запросов за доли секунды
for i in range(20):
    resp = router.route('/api/login', data={'username': f'user\_{i}'})
# RPS: ~200 на костылях!</code></pre>
    </div>

    <!-- ============================== -->
    <!-- DATA SCIENCE -->
    <!-- ============================== -->
    <div class="example-card" id="ds">
        <h3>3. Data Science на костылях</h3>
        <div class="meta">
            <span>📁 data\_science.py</span>
            <span><span class="badge badge-medium">Средний</span></span>
            <span>⏱️ ~8 сек</span>
        </div>

        <p>Анализ данных без numpy и pandas. Статистика, корреляции, линейная регрессия, поиск аномалий и кластеризация — всё на чистых костылях.</p>

        <h4>🚀 Запуск</h4>
        <pre><code>python examples/data\_science.py</code></pre>

        <h4>📝 Что внутри</h4>

        <table>
            <tr><th>Раздел</th><th>Метод</th></tr>
            <tr><td>Описательная статистика</td><td>Среднее, медиана, stdev по 5 полям</td></tr>
            <tr><td>Группировка</td><td>Агрегация по отделам (IT, HR, Sales...)</td></tr>
            <tr><td>Корреляции</td><td>Коэффициент Пирсона между парами полей</td></tr>
            <tr><td>Регрессия</td><td>Linear regression (опыт → зарплата)</td></tr>
            <tr><td>Аномалии</td><td>Z-score выбросы</td></tr>
            <tr><td>Кластеризация</td><td>Возрастные группы</td></tr>
        </table>

        <h4>📝 Ключевые моменты</h4>

        <p><strong>Безопасная корреляция:</strong></p>
        <pre><code>@kp.safe(fallback=0.0)
def correlation(x: list, y: list) -> float:
    """Коэффициент корреляции Пирсона."""
    n = len(x)
    mean\_x = statistics.mean(x)
    mean\_y = statistics.mean(y)
    cov = sum((x[i] - mean\_x) * (y[i] - mean\_y) for i in range(n)) / (n - 1)
    return kp.safe\_divide(cov, (std\_x * std\_y), default=0.0)</code></pre>

        <p><strong>Предсказание зарплаты:</strong></p>
        <pre><code>Модель: зарплата = 2500 × опыт + 45000

Предсказания:
├─ Опыт 1 год  → зарплата 47,500 ₽
├─ Опыт 5 лет  → зарплата 57,500 ₽
├─ Опыт 10 лет → зарплата 70,000 ₽
├─ Опыт 20 лет → зарплата 95,000 ₽
└─ Опыт 30 лет → зарплата 120,000 ₽</code></pre>
    </div>

    <!-- ============================== -->
    <!-- PRODUCTION -->
    <!-- ============================== -->
    <div class="example-card" id="prod">
        <h3>4. Продакшен-система</h3>
        <div class="meta">
            <span>📁 production.py</span>
            <span><span class="badge badge-hard">Сложный</span></span>
            <span>⏱️ ~15 сек</span>
        </div>

        <p>Серьёзное приложение с логированием, метриками, пулом соединений БД, кешем, очередью задач и фоновым мониторингом. Демонстрирует все возможности kostylpy в одном файле.</p>

        <h4>🚀 Запуск</h4>
        <pre><code>python examples/production.py</code></pre>

        <h4>📝 Архитектура</h4>

        <table>
            <tr><th>Компонент</th><th>Описание</th></tr>
            <tr><td><code>ConnectionPool</code></td><td>Пул соединений с БД</td></tr>
            <tr><td><code>Cache</code></td><td>Кеш с TTL и автоочисткой</td></tr>
            <tr><td><code>TaskQueue</code></td><td>Очередь задач с 4 воркерами</td></tr>
            <tr><td><code>HealthChecker</code></td><td>Проверка здоровья системы</td></tr>
            <tr><td><code>background\_stats</code></td><td>Фоновая статистика</td></tr>
            <tr><td><code>background\_health</code></td><td>Фоновая проверка здоровья</td></tr>
        </table>

        <h4>📝 Ключевые моменты</h4>

        <p><strong>Логирование всего:</strong></p>
        <pre><code>kp.logger.info("🚀 Система запускается...")
kp.logger.warning("⚠️ Система нездорова!")
kp.logger.coffee("☕ Кофе готов!")
kp.logger.kostyl("🦿 Применён костыль")</code></pre>

        <p><strong>Метрики в реальном времени:</strong></p>
        <pre><code>kp.metrics.record\_operation(success=True, duration=0.05)
kp.metrics.coffee.drink(duration=300.0)

print(f"Успешность: {kp.metrics.success\_rate:.1f}%")
print(f"Кофе: {kp.metrics.coffee.total\_coffees} кружек")</code></pre>

        <p><strong>Очередь задач:</strong></p>
        <pre><code>task\_queue.enqueue('send\_email', {'to': 'admin@example.com'})
task\_queue.enqueue('generate\_report', {'type': 'monthly'})
task\_queue.enqueue('backup\_database', {})
task\_queue.enqueue('clear\_cache', {})</code></pre>

        <h4>📊 Финальный отчёт</h4>
        <div class="output-block">
            🗄️ База данных:<br>
            &nbsp;&nbsp;&nbsp;Соединений: 2/50<br>
            &nbsp;&nbsp;&nbsp;Создано: 5<br>
            <br>
            💾 Кеш:<br>
            &nbsp;&nbsp;&nbsp;Размер: 2 записей<br>
            &nbsp;&nbsp;&nbsp;Попаданий: 75.0%<br>
            <br>
            📬 Очередь:<br>
            &nbsp;&nbsp;&nbsp;Добавлено: 6 задач<br>
            &nbsp;&nbsp;&nbsp;Обработано: 6<br>
            <br>
            ☕ Кофе:<br>
            &nbsp;&nbsp;&nbsp;Всего: 2 кофе-брейка<br>
            <br>
            🦿 KOSTYLPY:<br>
            &nbsp;&nbsp;&nbsp;Версия: 3.0.0-beta-kostyl<br>
            &nbsp;&nbsp;&nbsp;Костылей: множество
        </div>
    </div>

    <hr>

    <!-- ============================== -->
    <!-- TIPS -->
    <!-- ============================== -->
    <h2>💡 Советы по использованию</h2>

    <div class="tip">
        <strong>Начинайте с hello\_world.py</strong><br>
        Самый простой пример, показывающий все базовые концепции за 5 минут.
    </div>

    <div class="tip">
        <strong>Используйте KostylContext для опасных операций</strong><br>
        Работа с БД, сетевые запросы, парсинг — оборачивайте в <code>KostylContext</code>.
    </div>

    <div class="tip">
        <strong>Не забывайте про метрики</strong><br>
        <code>kp.metrics.record\_operation()</code> — одна строка, а сколько пользы!
    </div>

    <div class="tip">
        <strong>Кофе-метрика — это важно</strong><br>
        <code>kp.metrics.coffee.drink()</code> — без неё костыли не работают.
    </div>

    <hr>

    <!-- ============================== -->
    <!-- FOOTER -->
    <!-- ============================== -->
    <div class="footer">
        <p>
            🦿 Все примеры работают из коробки — просто запустите их!
        </p>
        <p style="margin-top: 8px;">
            <a href="API.md">📚 API Reference</a> •
            <a href="../README.md">🏠 Главная</a> •
        </p>
        <p style="margin-top: 16px;">
            <small>kostylpy v3.0.0-beta-kostyl-enterprise-edition</small>
        </p>
    </div>

</body>
</html>