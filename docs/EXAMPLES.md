<h1>🎮 Примеры использования kostylpy</h1>

<p><em>От Hello World до продакшен-системы — всё на костылях</em></p>

<hr>

<h2>📑 Содержание</h2>

<table>
    <tr><th>#</th><th>Пример</th><th>Файл</th><th>Что демонстрирует</th></tr>
    <tr>
        <td>1</td>
        <td><a href="#hello">Hello World</a></td>
        <td><code>hello_world.py</code></td>
        <td>Базовые фичи: safe, retry, контексты, валидаторы</td>
    </tr>
    <tr>
        <td>2</td>
        <td><a href="#web">Веб-сервер</a></td>
        <td><code>web_server.py</code></td>
        <td>Роутер, БД, сессии, валидация запросов</td>
    </tr>
    <tr>
        <td>3</td>
        <td><a href="#ds">Data Science</a></td>
        <td><code>data_science.py</code></td>
        <td>Статистика, корреляции, регрессия, кластеризация</td>
    </tr>
    <tr>
        <td>4</td>
        <td><a href="#prod">Продакшен</a></td>
        <td><code>production.py</code></td>
        <td>Логи, метрики, очереди, мониторинг, фоновые процессы</td>
    </tr>
</table>

<hr>

<h2 id="hello">1. Hello World на костылях</h2>

<p><strong>Файл:</strong> <code>hello_world.py</code> | <strong>Сложность:</strong> Лёгкая | <strong>Время:</strong> ~5 сек</p>

<p>Самый простой пример. Показывает базовые возможности библиотеки на нескольких строках кода.</p>

<h3>🚀 Запуск</h3>
<pre><code>cd examples
python hello_world.py</code></pre>

<h3>📝 Ключевые моменты</h3>

<p><strong>Безопасные функции:</strong></p>
<pre><code>@kp.safe(fallback="Всё сломалось, но мы держимся!")
def greet(name):
    if not isinstance(name, str):
        raise ValueError("Имя должно быть строкой!")
    return f"Привет, {name}!"

print(greet("Мир"))   # "Привет, Мир!"
print(greet(42))       # "Всё сломалось, но мы держимся!"</code></pre>

<p><strong>Повторные попытки:</strong></p>
<pre><code>@kp.retry(max_attempts=5, delay=0.1, fallback="Не удалось")
def unstable_greeting():
    # Пробует 5 раз, потом сдаётся
    ...</code></pre>

<p><strong>Защищённый блок:</strong></p>
<pre><code>with kp.KostylContext("опасная операция"):
    print("Внутри блока...")
    raise RuntimeError("Ошибка!")  # Подавлена!
    print("Это не выполнится")

print("А мы всё ещё живы!")  # Выполнится</code></pre>

<hr>

<h2 id="web">2. Веб-сервер на костылях</h2>

<p><strong>Файл:</strong> <code>web_server.py</code> | <strong>Сложность:</strong> Средняя | <strong>Время:</strong> ~10 сек</p>

<p>Полноценный веб-сервер с роутером, базой данных, сессиями и валидацией. Работает без Flask!</p>

<h3>🚀 Запуск</h3>
<pre><code>python examples/web_server.py</code></pre>

<h3>📝 Архитектура</h3>

<table>
    <tr><th>Компонент</th><th>Описание</th></tr>
    <tr><td><code>Database</code></td><td>JSON-база данных с автосохранением</td></tr>
    <tr><td><code>Router</code></td><td>Маршрутизатор запросов</td></tr>
    <tr><td><code>handle_register</code></td><td>Регистрация с валидацией</td></tr>
    <tr><td><code>handle_login</code></td><td>Вход с созданием сессии</td></tr>
    <tr><td><code>handle_profile</code></td><td>Профиль пользователя</td></tr>
</table>

<h3>📝 Ключевые моменты</h3>

<p><strong>Валидация запросов:</strong></p>
<pre><code>username_validator = kp.StringValidator(min_length=3, max_length=30)
password_validator = kp.PasswordValidator(min_length=6)
email_validator = kp.EmailValidator()

if not username_validator.validate(username).is_valid:
    errors.append('Имя пользователя должно быть от 3 до 30 символов')</code></pre>

<p><strong>Безопасная БД:</strong></p>
<pre><code>@kp.safe(fallback=None)
def get_user(self, user_id: str):
    return self._data.users.get(user_id)</code></pre>

<p><strong>Нагрузочный тест:</strong></p>
<pre><code># 20 запросов за доли секунды
for i in range(20):
    resp = router.route('/api/login', data={'username': f'user_{i}'})
# RPS: ~200 на костылях!</code></pre>

<hr>

<h2 id="ds">3. Data Science на костылях</h2>

<p><strong>Файл:</strong> <code>data_science.py</code> | <strong>Сложность:</strong> Средняя | <strong>Время:</strong> ~8 сек</p>

<p>Анализ данных без numpy и pandas. Статистика, корреляции, линейная регрессия, поиск аномалий и кластеризация — всё на чистых костылях.</p>

<h3>🚀 Запуск</h3>
<pre><code>python examples/data_science.py</code></pre>

<h3>📝 Что внутри</h3>

<table>
    <tr><th>Раздел</th><th>Метод</th></tr>
    <tr><td>Описательная статистика</td><td>Среднее, медиана, stdev по 5 полям</td></tr>
    <tr><td>Группировка</td><td>Агрегация по отделам (IT, HR, Sales...)</td></tr>
    <tr><td>Корреляции</td><td>Коэффициент Пирсона между парами полей</td></tr>
    <tr><td>Регрессия</td><td>Linear regression (опыт → зарплата)</td></tr>
    <tr><td>Аномалии</td><td>Z-score выбросы</td></tr>
    <tr><td>Кластеризация</td><td>Возрастные группы</td></tr>
</table>

<h3>📝 Ключевые моменты</h3>

<p><strong>Безопасная корреляция:</strong></p>
<pre><code>@kp.safe(fallback=0.0)
def correlation(x: list, y: list) -> float:
    n = len(x)
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    cov = sum((x[i]-mean_x)*(y[i]-mean_y) for i in range(n)) / (n-1)
    return kp.safe_divide(cov, (std_x * std_y), default=0.0)</code></pre>

<p><strong>Предсказание зарплаты:</strong></p>
<pre><code>Модель: зарплата = 2500 × опыт + 45000

Предсказания:
├─ Опыт 1 год  → зарплата 47,500 ₽
├─ Опыт 5 лет  → зарплата 57,500 ₽
├─ Опыт 10 лет → зарплата 70,000 ₽
├─ Опыт 20 лет → зарплата 95,000 ₽
└─ Опыт 30 лет → зарплата 120,000 ₽</code></pre>

<hr>

<h2 id="prod">4. Продакшен-система</h2>

<p><strong>Файл:</strong> <code>production.py</code> | <strong>Сложность:</strong> Высокая | <strong>Время:</strong> ~15 сек</p>

<p>Серьёзное приложение с логированием, метриками, пулом соединений БД, кешем, очередью задач и фоновым мониторингом.</p>

<h3>🚀 Запуск</h3>
<pre><code>python examples/production.py</code></pre>

<h3>📝 Архитектура</h3>

<table>
    <tr><th>Компонент</th><th>Описание</th></tr>
    <tr><td><code>ConnectionPool</code></td><td>Пул соединений с БД</td></tr>
    <tr><td><code>Cache</code></td><td>Кеш с TTL и автоочисткой</td></tr>
    <tr><td><code>TaskQueue</code></td><td>Очередь задач с 4 воркерами</td></tr>
    <tr><td><code>HealthChecker</code></td><td>Проверка здоровья системы</td></tr>
    <tr><td><code>background_stats</code></td><td>Фоновая статистика</td></tr>
    <tr><td><code>background_health</code></td><td>Фоновая проверка здоровья</td></tr>
</table>

<h3>📝 Ключевые моменты</h3>

<p><strong>Логирование всего:</strong></p>
<pre><code>kp.logger.info("🚀 Система запускается...")
kp.logger.warning("⚠️ Система нездорова!")
kp.logger.coffee("☕ Кофе готов!")
kp.logger.kostyl("🦿 Применён костыль")</code></pre>

<p><strong>Метрики в реальном времени:</strong></p>
<pre><code>kp.metrics.record_operation(success=True, duration=0.05)
kp.metrics.coffee.drink(duration=300.0)

print(f"Успешность: {kp.metrics.success_rate:.1f}%")
print(f"Кофе: {kp.metrics.coffee.total_coffees} кружек")</code></pre>

<p><strong>Очередь задач:</strong></p>
<pre><code>task_queue.enqueue('send_email', {'to': 'admin@example.com'})
task_queue.enqueue('generate_report', {'type': 'monthly'})
task_queue.enqueue('backup_database', {})
task_queue.enqueue('clear_cache', {})</code></pre>

<hr>

<h2>💡 Советы по использованию</h2>

<p><strong>🟢 Начинайте с hello_world.py</strong> — самый простой пример, показывает все базовые концепции за 5 минут.</p>

<p><strong>🟢 Используйте KostylContext для опасных операций</strong> — работа с БД, сетевые запросы, парсинг.</p>

<p><strong>🟢 Не забывайте про метрики</strong> — <code>kp.metrics.record_operation()</code> одна строка, а сколько пользы!</p>

<p><strong>🟢 Кофе-метрика — это важно</strong> — <code>kp.metrics.coffee.drink()</code> без неё костыли не работают.</p>

<hr>

<p align="center">
    🦿 Все примеры работают из коробки — просто запустите их!
</p>

<p align="center">
    <a href="API.md">📚 API Reference</a> •
    <a href="../README.md">🏠 Главная</a>
</p>