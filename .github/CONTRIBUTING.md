<h1>🤝 Контрибьюция в kostylpy</h1>

<p><em>Спасибо, что решили помочь проекту! Вот как это сделать правильно.</em></p>

<hr>

<h2>🌟 Почему стоит контрибьютить?</h2>

<h3>01. Сделать мир лучше</h3>
<p>Каждый новый костыль спасает чей-то код от падения в продакшене.</p>

<h3>02. Войти в историю</h3>
<p>Ваше имя будет вписано в анналы костылестроения. Или в git log, как минимум.</p>

<h3>03. Бесконечный кофе</h3>
<p>Ну, не буквально. Но <code>kp.metrics.coffee.drink()</code> будет работать.</p>

<hr>

<h2>📯 Заповеди контрибьютора</h2>

<h3>☕ 1. Кофе обязателен</h3>
<p>Без кофе костыли не работают. Это научный факт. Минимум одна кружка перед коммитом.</p>

<h3>🧪 2. Тесты для новых костылей</h3>
<p>Каждый костыль должен быть протестирован. <code>make test</code> — твой лучший друг.</p>

<h3>⚠️ 3. Не ломай существующие костыли</h3>
<p>Они хрупкие. Они держат продакшен. Будь осторожен.</p>

<h3>📖 4. Читай исходники</h3>
<p>Документация может устареть. Исходники — никогда. (Потому что мы их не меняем.)</p>

<h3>💬 5. Обсуждай перед большими PR</h3>
<p>Создай issue и обсуди идею до того, как написать 1000 строк кода.</p>

<h3>🦿 6. Помни: всё есть костыль</h3>
<p>Твой код, мой код, сам Python. Прими это. Добавь ещё костылей.</p>

<hr>

<h2>🚀 Процесс контрибьюции</h2>

<ol>
    <li>
        <strong>Форкни репозиторий</strong><br>
        <code>git clone https://github.com/YOUR_USERNAME/kostylpy.git</code>
    </li>
    <li>
        <strong>Создай ветку</strong><br>
        <code>git checkout -b feature/my-awesome-crutch</code><br>
        <em>Ветки именуем: feature/..., fix/..., docs/..., test/...</em>
    </li>
    <li>
        <strong>Установи зависимости для разработки</strong><br>
        <code>pip install -e .[dev]</code>
    </li>
    <li>
        <strong>Добавь костылей</strong><br>
        <em>Пиши код. Не забывай про документацию и тесты.</em>
    </li>
    <li>
        <strong>Запусти тесты</strong><br>
        <code>make test</code>
    </li>
    <li>
        <strong>Проверь стиль</strong><br>
        <code>make lint</code>
    </li>
    <li>
        <strong>Запушь и создай Pull Request</strong><br>
        <code>git push origin feature/my-awesome-crutch</code>
    </li>
</ol>

<hr>

<h2>📝 Стандарты кода</h2>

<h3>Стиль</h3>
<ul>
    <li>Следуем <strong>PEP 8</strong> с длиной строки до <strong>120 символов</strong></li>
    <li>Используем <strong>type hints</strong> где это уместно</li>
    <li>Документируем публичные функции в <strong>docstrings</strong></li>
    <li>Комментарии пишем на <strong>русском</strong> или <strong>английском</strong></li>
</ul>

<h3>Именование</h3>
<table>
    <tr><th>Что</th><th>Стиль</th><th>Пример</th></tr>
    <tr><td>Функции</td><td>snake_case</td><td><code>def safe_divide():</code></td></tr>
    <tr><td>Классы</td><td>PascalCase</td><td><code>class KostylContext:</code></td></tr>
    <tr><td>Константы</td><td>UPPER_CASE</td><td><code>PANIC_THRESHOLD = 42</code></td></tr>
    <tr><td>Приватные</td><td>_underscore</td><td><code>def _internal_helper():</code></td></tr>
</table>

<h3>Пример хорошего костыля</h3>
<pre><code>@kp.safe(fallback=None)
def my_new_crutch(data: dict, key: str, default: Any = None) -> Any:
    """
    Безопасно извлекает значение из словаря.
    
    Args:
        data: Исходный словарь
        key: Ключ для поиска
        default: Значение по умолчанию
    
    Returns:
        Значение из словаря или default
    """
    with kp.KostylContext("извлечение данных"):
        return kp.safe_get(data, key, default=default)</code></pre>

<p><strong>💡 Совет:</strong> Посмотри на существующие модули в <code>kostylpy/</code> — они показывают стиль проекта.</p>

<hr>

<h2>🧪 Тестирование</h2>

<p>Каждый новый костыль <strong>должен</strong> иметь тесты. Без исключений. (Даже с исключениями.)</p>

<h3>Запуск тестов</h3>
<pre><code>make test              # Все тесты
make test-core         # Только ядро
make test-decorators   # Только декораторы
make test-coverage     # С покрытием</code></pre>

<h3>Где лежат тесты</h3>
<ul>
    <li><code>tests/test_core.py</code> — тесты ядра</li>
    <li><code>tests/test_decorators.py</code> — тесты декораторов</li>
    <li><code>tests/test_patcher.py</code> — тесты патчера</li>
    <li><code>tests/test_interceptors.py</code> — тесты перехватчиков</li>
    <li><code>tests/test_integration.py</code> — интеграционные тесты</li>
</ul>

<p><strong>⚠️ Важно:</strong> Если ваш PR ломает существующие тесты — он не будет принят. Запускайте <code>make test</code> перед пушем.</p>

<hr>

<h2>📚 Документация</h2>

<p>Документация — это не обязательно. Но если вы её пишете:</p>
<ul>
    <li><strong>API Reference:</strong> <code>docs/API.md</code> — описание публичного API</li>
    <li><strong>Примеры:</strong> <code>docs/EXAMPLES.md</code> — примеры использования</li>
    <li><strong>Философия:</strong> <code>docs/PHILOSOPHY.md</code> — зачем мы это делаем</li>
</ul>

<p><strong>💡 Совет:</strong> Лучшая документация — это хорошие тесты и понятные примеры.</p>

<hr>

<h2>💬 Коммуникация</h2>

<table>
    <tr><th>Канал</th><th>Для чего</th></tr>
    <tr><td>🐙 <strong>GitHub Issues</strong></td><td>Баг-репорты и запросы фич</td></tr>
    <tr><td>🔄 <strong>Pull Requests</strong></td><td>Предложения изменений</td></tr>
    <tr><td>💬 <strong>Discussions</strong></td><td>Вопросы и обсуждения</td></tr>
</table>

<p><strong>🚫 Запрещено:</strong></p>
<ul>
    <li>Оскорбления и токсичное поведение</li>
    <li>Спам и реклама</li>
    <li>Код без костылей</li>
</ul>

<hr>

<h2>🎁 Бонус: Что мы особенно ценим</h2>

<h3>🦿 Креативные костыли</h3>
<p>Чем неожиданнее решение — тем лучше. Удивите нас.</p>

<h3>📊 Хорошие метрики</h3>
<p>Добавили <code>Counter</code> или <code>Gauge</code>? Мы любим метрики.</p>

<h3>☕ Кофе-интеграции</h3>
<p>Всё что связано с кофе — автоматический approve.</p>

<h3>🐛 Исправление багов</h3>
<p>Починили то, что мы сломали? Вы — герой.</p>

<hr>

<p align="center">
    🦿 <strong>Спасибо, что помогаете проекту!</strong>
</p>

<p align="center">
    Каждый новый костыль делает мир чуточку надёжнее.
</p>

<p align="center">
    <em>kostylpy v3.0.0-beta-kostyl-enterprise-edition</em><br>
    <em>Руководство одобрено Коллективом костылестроителей</em>
</p>