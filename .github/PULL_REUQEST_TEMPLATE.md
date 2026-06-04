---
name: 🦿 Pull Request <br>
about: Добавляем костыли в проект!<br>
title: '[PR] '<br>
labels: ['pull request', 'новый костыль']<br>
assignees: ''<br>
---

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
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 20px;
    overflow-x: hidden;
    max-width: 100vw;
  }

  .pr-header {
    background: linear-gradient(135deg, #1a2e1a 0%, #101a10 100%);
    border: 1px solid var(--success);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    text-align: center;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .pr-header h1 { color: var(--success); margin: 0 0 8px; font-size: 1.8em; }
  .pr-header .subtitle { color: var(--text-secondary); font-style: italic; margin: 0; }

  .section {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .section h2 {
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 0 0 12px;
    font-size: 1.2em;
  }
  .section h3 { color: var(--text); margin: 12px 0 8px; font-size: 1em; }

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
    margin: 8px 0;
    max-width: 100%;
    white-space: pre-wrap;
  }
  pre code { background: none; padding: 0; font-size: 0.85em; line-height: 1.5; }

  .checklist {
    list-style: none;
    padding: 0;
    margin: 12px 0;
  }
  .checklist li {
    padding: 10px 12px 10px 40px;
    position: relative;
    margin: 6px 0;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .checklist li::before {
    content: '';
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    border: 2px solid var(--border);
    border-radius: 4px;
    background: var(--bg-secondary);
  }
  .checklist li.checked::before {
    background: var(--success);
    border-color: var(--success);
    content: '✓';
    color: var(--bg);
    text-align: center;
    line-height: 20px;
    font-size: 0.8em;
    font-weight: bold;
  }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
    margin-right: 6px;
  }
  .badge-success { background: #1a3a2a; color: var(--success); }
  .badge-warning { background: #3a3a1a; color: var(--warning); }
  .badge-danger { background: #2d1b1b; color: var(--danger); }
  .badge-info { background: #1a1a3a; color: var(--purple); }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 12px 0;
    max-width: 100%;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin: 12px 0;
    max-width: 100%;
  }

  .stat-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    max-width: 100%;
    min-width: 0;
    -webkit-tap-highlight-color: transparent;
  }
  .stat-card .value {
    font-size: 1.8em;
    font-weight: bold;
    color: var(--accent-emphasis);
  }
  .stat-card .label {
    color: var(--text-secondary);
    font-size: 0.85em;
    margin-top: 4px;
  }

  .progress-bar {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0;
    max-width: 100%;
  }
  .progress-bar .fill {
    height: 100%;
    background: linear-gradient(90deg, var(--success), #7ee787);
    border-radius: 4px;
  }

  .linked-issues {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0;
    max-width: 100%;
  }
  .linked-issue {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.9em;
    color: var(--accent);
  }
  .linked-issue::before { content: '🔗 '; }

  .tip {
    background: #1a2e1a;
    border-left: 4px solid var(--success);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
    max-width: 100%;
  }
  .tip strong { color: var(--success); }

  .warning-box {
    background: #2d2d1b;
    border-left: 4px solid var(--warning);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
    max-width: 100%;
  }
  .warning-box strong { color: var(--warning); }

  .danger-box {
    background: #2d1b1b;
    border-left: 4px solid var(--danger);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
    max-width: 100%;
  }
  .danger-box strong { color: var(--danger); }

  textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    color: var(--text);
    font-family: inherit;
    font-size: 0.95em;
    min-height: 80px;
    resize: vertical;
    max-width: 100%;
    box-sizing: border-box;
  }
  textarea:focus { outline: none; border-color: var(--accent); }

  .footer { text-align: center; color: var(--text-secondary); font-size: 0.85em; margin-top: 20px; max-width: 100%; }
  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  @media (max-width: 768px) {
    body { padding: 10px; }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
  }
</style>

<div class="pr-header">
  <h1>🦿 Pull Request</h1>
  <p class="subtitle">Добавляем костыли. Делаем мир надёжнее.</p>
</div>

<!-- БЫСТРЫЙ ОБЗОР -->
<div class="section">
  <h2>📊 Быстрый обзор</h2>

  <div class="grid-3">
    <div class="stat-card">
      <div class="value">+42</div>
      <div class="label">Строк кода</div>
    </div>
    <div class="stat-card">
      <div class="value">3</div>
      <div class="label">Файлов изменено</div>
    </div>
    <div class="stat-card">
      <div class="value">✅</div>
      <div class="label">Тесты проходят</div>
    </div>
  </div>

  <div style="margin-top: 12px;">
    <span style="color: var(--text-secondary);">Готовность к мёрджу:</span>
    <div class="progress-bar">
      <div class="fill" style="width: 100%;"></div>
    </div>
  </div>
</div>

<!-- ОПИСАНИЕ -->
<div class="section">
  <h2>🦿 Описание изменений</h2>
  <p>Опишите, какие костыли вы добавили и зачем.</p>
  <textarea placeholder="Добавлен новый декоратор @kp.mega_crutch, который делает X, Y и Z..."></textarea>

  <div class="tip">
    <strong>💡 Совет:</strong> Хорошее описание помогает ревьюерам понять ваш код. Пишите как для себя через полгода.
  </div>
</div>

<!-- ТИП ИЗМЕНЕНИЙ -->
<div class="section">
  <h2>🏷️ Тип изменений</h2>

  <div class="grid-2">
    <div>
      <h3>Что изменилось?</h3>
      <ul style="list-style: none; padding: 0;">
        <li style="padding: 6px 0;">✅ <span class="badge badge-success">feature</span> Новая фича</li>
        <li style="padding: 6px 0;">🐛 <span class="badge badge-danger">fix</span> Исправление бага</li>
        <li style="padding: 6px 0;">📚 <span class="badge badge-info">docs</span> Документация</li>
        <li style="padding: 6px 0;">🔧 <span class="badge badge-warning">refactor</span> Рефакторинг</li>
        <li style="padding: 6px 0;">🧪 <span class="badge badge-success">test</span> Тесты</li>
      </ul>
    </div>
    <div>
      <h3>Breaking change?</h3>
      <ul style="list-style: none; padding: 0;">
        <li style="padding: 6px 0;">✅ Нет, всё совместимо</li>
        <li style="padding: 6px 0;">⚠️ Да, есть изменения API</li>
      </ul>
    </div>
  </div>
</div>

<!-- ЧЕКЛИСТ -->
<div class="section">
  <h2>✅ Чеклист</h2>

  <ul class="checklist">
    <li class="checked">Код соответствует стилю костылей</li>
    <li class="checked">Добавлены тесты для новых костылей</li>
    <li class="checked">Все существующие тесты проходят (<code>make test</code>)</li>
    <li class="checked">Линтер доволен (<code>make lint</code>)</li>
    <li class="checked">Документация обновлена (если нужно)</li>
    <li class="checked">Кофе выпит ☕</li>
  </ul>
</div>

<!-- КАК ТЕСТИРОВАТЬ -->
<div class="section">
  <h2>🧪 Как тестировать</h2>
  <p>Опишите, как проверить ваши изменения.</p>

  <pre><code># Запустить тесты
make test

# Запустить конкретный тест
python -m pytest tests/test_decorators.py -v -k "test_new_crutch"

# Проверить на примере
python examples/hello_world.py</code></pre>

  <div class="warning-box">
    <strong>⚠️ Важно:</strong> Убедитесь, что ваши изменения не ломают существующие примеры из <code>examples/</code>.
  </div>
</div>

<!-- СКРИНШОТЫ -->
<div class="section">
  <h2>📸 Скриншоты / Демо</h2>
  <p>Если ваши изменения влияют на вывод или поведение — приложите скриншоты.</p>
  <textarea placeholder="Вставьте ссылки на скриншоты или опишите как увидеть результат..."></textarea>
</div>

<!-- СВЯЗАННЫЕ ISSUES -->
<div class="section">
  <h2>🔗 Связанные issues</h2>
  <p>Укажите issues, которые закрывает этот PR.</p>

  <div class="linked-issues">
    <span class="linked-issue">Closes #123</span>
    <span class="linked-issue">Related #456</span>
  </div>
</div>

<!-- ДОПОЛНИТЕЛЬНО -->
<div class="section">
  <h2>📝 Дополнительно</h2>
  <p>Любая другая информация для ревьюеров.</p>
  <textarea placeholder="Здесь можно написать о принятых архитектурных решениях, альтернативах, которые рассматривались, или просто поблагодарить за ревью..."></textarea>
</div>

<!-- ФУТЕР -->
<hr>
<div class="footer">
  <p>
    🦿 Спасибо за вклад в развитие kostylpy!
  </p>
  <p style="margin-top: 4px;">
    <small>Ваш PR будет рассмотрен после кофе-брейка. Обычно это занимает 1-2 рабочих дня.</small>
  </p>
  <p style="margin-top: 8px;">
    <span class="badge badge-info">☕ Кофе</span>
    <span class="badge badge-success">🦿 Костыли</span>
    <span class="badge badge-warning">🚀 Продакшен</span>
  </p>
</div>