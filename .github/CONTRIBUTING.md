<style>
  /* ═══════════════════════════════════════════════════ */
  /* БАЗОВЫЙ СБРОС И ЗАЩИТА */
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
    max-width: 100%;
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
    --orange: #d18616;
    --pink: #db61a2;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    padding: 20px;
    overflow-x: hidden;
    max-width: 100vw;
  }

  .header {
    text-align: center;
    padding: 40px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
    max-width: 100%;
  }
  .header h1 {
    font-size: 2.5em;
    color: var(--accent-emphasis);
    border: none;
    margin-bottom: 8px;
  }
  .header p {
    color: var(--text-secondary);
    font-style: italic;
    font-size: 1.1em;
  }

  h2 {
    color: var(--accent-emphasis);
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin: 40px 0 20px;
    font-size: 1.5em;
    max-width: 100%;
  }
  h3 { color: var(--text); margin: 24px 0 12px; font-size: 1.15em; }

  code {
    background: #1a1a2e;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
    font-size: 0.9em;
    color: #e6edf3;
    max-width: 100%;
    display: inline-block;
    vertical-align: top;
  }
  pre {
    background: #0a0e14;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 12px 0;
    max-width: 100%;
    white-space: pre-wrap;
  }
  pre code { background: none; padding: 0; font-size: 0.85em; }

  .principles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin: 20px 0;
    max-width: 100%;
  }
  .principle-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    max-width: 100%;
    min-width: 0;
    -webkit-tap-highlight-color: transparent;
  }
  .principle-card .number {
    font-size: 3em;
    font-weight: bold;
    color: var(--accent);
    opacity: 0.15;
    position: absolute;
    top: -10px;
    right: 10px;
    pointer-events: none;
  }
  .principle-card h3 {
    margin: 0 0 8px;
    color: var(--accent-emphasis);
  }
  .principle-card p { color: var(--text-secondary); margin: 0; font-size: 0.95em; }

  .steps {
    list-style: none;
    padding: 0;
    counter-reset: step;
  }
  .steps li {
    counter-increment: step;
    padding: 16px 16px 16px 60px;
    position: relative;
    margin: 12px 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .steps li::before {
    content: counter(step);
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
    line-height: 32px;
    text-align: center;
    background: var(--accent);
    color: var(--bg);
    border-radius: 50%;
    font-weight: bold;
    font-size: 1em;
  }
  .steps li strong { display: block; margin-bottom: 4px; }
  .steps li code { font-size: 0.85em; }

  .tip {
    background: #1a2e1a;
    border-left: 4px solid var(--success);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    max-width: 100%;
  }
  .tip strong { color: var(--success); }

  .warning-box {
    background: #2d2d1b;
    border-left: 4px solid var(--warning);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    max-width: 100%;
  }
  .warning-box strong { color: var(--warning); }

  .danger-box {
    background: #2d1b1b;
    border-left: 4px solid var(--danger);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    max-width: 100%;
  }
  .danger-box strong { color: var(--danger); }

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
  td { color: var(--text-secondary); }
  td:first-child { color: var(--text); font-family: monospace; }

  .command-block {
    background: #0a0e14;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 0.9em;
    max-width: 100%;
    overflow-x: auto;
    white-space: pre-wrap;
  }
  .command-block .prompt { color: var(--success); }
  .command-block .cmd { color: var(--accent-emphasis); }
  .command-block .comment { color: var(--text-secondary); }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
    margin-right: 6px;
  }
  .badge-green { background: #1a3a2a; color: var(--success); }
  .badge-yellow { background: #3a3a1a; color: var(--warning); }
  .badge-red { background: #2d1b1b; color: var(--danger); }
  .badge-purple { background: #1a1a3a; color: var(--purple); }
  .badge-pink { background: #3a1a3a; color: var(--pink); }

  .coffee-tracker {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin: 20px 0;
    max-width: 100%;
  }
  .coffee-tracker .cups { font-size: 1.5em; }
  .coffee-tracker .bar {
    flex: 1;
    height: 10px;
    background: var(--border);
    border-radius: 5px;
    overflow: hidden;
    min-width: 50px;
  }
  .coffee-tracker .fill {
    height: 100%;
    background: linear-gradient(90deg, #d2991d, #f0c040);
    border-radius: 5px;
  }

  .footer {
    text-align: center;
    padding: 30px 20px;
    margin-top: 40px;
    border-top: 1px solid var(--border);
    color: var(--text-secondary);
    max-width: 100%;
  }
  hr { border: none; border-top: 1px solid var(--border); margin: 30px 0; }

  a {
    color: var(--accent);
    -webkit-user-select: text;
    -moz-user-select: text;
    user-select: text;
    text-decoration: none;
  }
  a:hover { text-decoration: underline; }

  strong { color: #e6edf3; }
  em { color: var(--text-secondary); }

  @media (max-width: 768px) {
    body { padding: 10px; }
    .principles-grid { grid-template-columns: 1fr; }
    .steps li { padding-left: 45px; }
    h1 { font-size: 1.8em; }
    h2 { font-size: 1.3em; }
  }
</style>

<div class="header">
  <h1>🤝 Контрибьюция в kostylpy</h1>
  <p>Спасибо, что решили помочь проекту! Вот как это сделать правильно.</p>
</div>

<!-- ПОЧЕМУ -->
<h2>🌟 Почему стоит контрибьютить?</h2>

<div class="principles-grid">
  <div class="principle-card">
    <div class="number">01</div>
    <h3>Сделать мир лучше</h3>
    <p>Каждый новый костыль спасает чей-то код от падения в продакшене.</p>
  </div>
  <div class="principle-card">
    <div class="number">02</div>
    <h3>Войти в историю</h3>
    <p>Ваше имя будет вписано в анналы костылестроения. Или в git log, как минимум.</p>
  </div>
  <div class="principle-card">
    <div class="number">03</div>
    <h3>Бесконечный кофе</h3>
    <p>Ну, не буквально. Но <code>kp.metrics.coffee.drink()</code> будет работать.</p>
  </div>
</div>

<hr>

<!-- ЗАПОВЕДИ -->
<h2>📯 Заповеди контрибьютора</h2>

<div class="principles-grid">
  <div class="principle-card" style="border-left: 4px solid var(--warning);">
    <h3>☕ 1. Кофе обязателен</h3>
    <p>Без кофе костыли не работают. Это научный факт. Минимум одна кружка перед коммитом.</p>
  </div>
  <div class="principle-card" style="border-left: 4px solid var(--success);">
    <h3>🧪 2. Тесты для новых костылей</h3>
    <p>Каждый костыль должен быть протестирован. <code>make test</code> — твой лучший друг.</p>
  </div>
  <div class="principle-card" style="border-left: 4px solid var(--danger);">
    <h3>⚠️ 3. Не ломай существующие костыли</h3>
    <p>Они хрупкие. Они держат продакшен. Будь осторожен.</p>
  </div>
  <div class="principle-card" style="border-left: 4px solid var(--purple);">
    <h3>📖 4. Читай исходники</h3>
    <p>Документация может устареть. Исходники — никогда. (Потому что мы их не меняем.)</p>
  </div>
  <div class="principle-card" style="border-left: 4px solid var(--accent);">
    <h3>💬 5. Обсуждай перед большими PR</h3>
    <p>Создай issue и обсуди идею до того, как написать 1000 строк кода.</p>
  </div>
  <div class="principle-card" style="border-left: 4px solid var(--pink);">
    <h3>🦿 6. Помни: всё есть костыль</h3>
    <p>Твой код, мой код, сам Python. Прими это. Добавь ещё костылей.</p>
  </div>
</div>

<hr>

<!-- ПРОЦЕСС -->
<h2>🚀 Процесс контрибьюции</h2>

<ol class="steps">
  <li>
    <strong>Форкни репозиторий</strong>
    <code>git clone https://github.com/YOUR_USERNAME/kostylpy.git</code>
  </li>
  <li>
    <strong>Создай ветку</strong>
    <code>git checkout -b feature/my-awesome-crutch</code>
    <br>
    <small style="color: var(--text-secondary);">Ветки именуем так: <code>feature/...</code>, <code>fix/...</code>, <code>docs/...</code>, <code>test/...</code></small>
  </li>
  <li>
    <strong>Установи зависимости для разработки</strong>
    <code>pip install -e .[dev]</code>
  </li>
  <li>
    <strong>Добавь костылей</strong>
    <br>
    <small style="color: var(--text-secondary);">Пиши код. Не забывай про документацию и тесты.</small>
  </li>
  <li>
    <strong>Запусти тесты</strong>
    <code>make test</code>
  </li>
  <li>
    <strong>Проверь стиль</strong>
    <code>make lint</code>
  </li>
  <li>
    <strong>Запушь и создай Pull Request</strong>
    <code>git push origin feature/my-awesome-crutch</code>
  </li>
</ol>

<div class="coffee-tracker">
  <span class="cups">☕☕☕</span>
  <span>Прогресс контрибьюции:</span>
  <span class="bar"><span class="fill" style="width: 100%;"></span></span>
  <span style="color: var(--success); font-weight: bold;">Готово!</span>
</div>

<hr>

<!-- КАК ПИСАТЬ КОД -->
<h2>📝 Стандарты кода</h2>

<h3>Стиль</h3>
<ul style="padding-left: 20px; color: var(--text-secondary);">
  <li style="margin: 6px 0;">Следуем <strong>PEP 8</strong> с длиной строки до <strong>120 символов</strong></li>
  <li style="margin: 6px 0;">Используем <strong>type hints</strong> где это уместно</li>
  <li style="margin: 6px 0;">Документируем публичные функции в <strong>docstrings</strong></li>
  <li style="margin: 6px 0;">Комментарии пишем на <strong>русском</strong> или <strong>английском</strong></li>
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

<div class="tip">
  <strong>💡 Совет:</strong> Посмотри на существующие модули в <code>kostylpy/</code> — они показывают стиль проекта.
</div>

<hr>

<!-- ТЕСТЫ -->
<h2>🧪 Тестирование</h2>

<p>Каждый новый костыль <strong>должен</strong> иметь тесты. Без исключений. (Даже с исключениями.)</p>

<h3>Запуск тестов</h3>

<div class="command-block">
  <span class="prompt">$</span> <span class="cmd">make test</span> <span class="comment"># Все тесты</span><br>
  <span class="prompt">$</span> <span class="cmd">make test-core</span> <span class="comment"># Только ядро</span><br>
  <span class="prompt">$</span> <span class="cmd">make test-decorators</span> <span class="comment"># Только декораторы</span><br>
  <span class="prompt">$</span> <span class="cmd">make test-coverage</span> <span class="comment"># С покрытием</span>
</div>

<h3>Где лежат тесты</h3>
<ul style="padding-left: 20px; color: var(--text-secondary);">
  <li style="margin: 6px 0;"><code>tests/test_core.py</code> — тесты ядра</li>
  <li style="margin: 6px 0;"><code>tests/test_decorators.py</code> — тесты декораторов</li>
  <li style="margin: 6px 0;"><code>tests/test_patcher.py</code> — тесты патчера</li>
  <li style="margin: 6px 0;"><code>tests/test_interceptors.py</code> — тесты перехватчиков</li>
  <li style="margin: 6px 0;"><code>tests/test_integration.py</code> — интеграционные тесты</li>
</ul>

<div class="warning-box">
  <strong>⚠️ Важно:</strong> Если ваш PR ломает существующие тесты — он не будет принят. Запускайте <code>make test</code> перед пушем.
</div>

<hr>

<!-- ДОКУМЕНТАЦИЯ -->
<h2>📚 Документация</h2>

<p>Документация — это не обязательно. Но если вы её пишете:</p>

<ul style="padding-left: 20px; color: var(--text-secondary);">
  <li style="margin: 6px 0;"><strong>API Reference:</strong> <code>docs/API.html</code> — описание публичного API</li>
  <li style="margin: 6px 0;"><strong>Примеры:</strong> <code>docs/EXAMPLES.html</code> — примеры использования</li>
  <li style="margin: 6px 0;"><strong>Философия:</strong> <code>docs/PHILOSOPHY.html</code> — зачем мы это делаем</li>
</ul>

<div class="tip">
  <strong>💡 Совет:</strong> Лучшая документация — это хорошие тесты и понятные примеры.
</div>

<hr>

<!-- КОММУНИКАЦИЯ -->
<h2>💬 Коммуникация</h2>

<table>
  <tr>
    <th>Канал</th>
    <th>Для чего</th>
  </tr>
  <tr>
    <td>🐙 <strong>GitHub Issues</strong></td>
    <td>Баг-репорты и запросы фич</td>
  </tr>
  <tr>
    <td>🔄 <strong>Pull Requests</strong></td>
    <td>Предложения изменений</td>
  </tr>
  <tr>
    <td>💬 <strong>Discussions</strong></td>
    <td>Вопросы и обсуждения</td>
  </tr>
</table>

<div class="danger-box">
  <strong>🚫 Запрещено:</strong>
  <ul style="margin: 8px 0 0; padding-left: 20px;">
    <li style="margin: 4px 0;">Оскорбления и токсичное поведение</li>
    <li style="margin: 4px 0;">Спам и реклама</li>
    <li style="margin: 4px 0;">Код без костылей</li>
  </ul>
</div>

<hr>

<!-- БОНУС -->
<h2>🎁 Бонус: Что мы особенно ценим</h2>

<div class="principles-grid">
  <div class="principle-card">
    <h3>🦿 Креативные костыли</h3>
    <p>Чем неожиданнее решение — тем лучше. Удивите нас.</p>
  </div>
  <div class="principle-card">
    <h3>📊 Хорошие метрики</h3>
    <p>Добавили <code>Counter</code> или <code>Gauge</code>? Мы любим метрики.</p>
  </div>
  <div class="principle-card">
    <h3>☕ Кофе-интеграции</h3>
    <p>Всё что связано с кофе — автоматический approve.</p>
  </div>
  <div class="principle-card">
    <h3>🐛 Исправление багов</h3>
    <p>Починили то, что мы сломали? Вы — герой.</p>
  </div>
</div>

<hr>

<!-- ФУТЕР -->
<div class="footer">
  <p>
    🦿 <strong>Спасибо, что помогаете проекту!</strong>
  </p>
  <p style="margin-top: 8px;">
    Каждый новый костыль делает мир чуточку надёжнее.
  </p>
  <p style="margin-top: 16px;">
    <span class="badge badge-green">☕ Кофе</span>
    <span class="badge badge-purple">🦿 Костыли</span>
    <span class="badge badge-yellow">🚀 Продакшен</span>
    <span class="badge badge-pink">💖 Open Source</span>
  </p>
  <p style="margin-top: 16px;">
    <small>kostylpy v3.0.0-beta-kostyl-enterprise-edition</small><br>
    <small>Руководство одобрено Коллективом костылестроителей</small>
  </p>
</div>