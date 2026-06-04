---
name: 🐛 Сообщение о баге<br>
about: Что-то сломалось? Нужно больше костылей!<br>
title: '[BUG] '<br>
labels: ['bug', 'нужен костыль']<br>
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
    --danger: #f85149;
    --warning: #d2991d;
    --success: #3fb950;
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

  .bug-header {
    background: linear-gradient(135deg, #2d1b1b 0%, #1a1010 100%);
    border: 1px solid var(--danger);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    text-align: center;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .bug-header h1 { color: var(--danger); margin: 0 0 8px; font-size: 1.8em; }
  .bug-header p { color: var(--text-secondary); margin: 0; font-style: italic; }

  .section {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .section h2 { color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 8px; margin: 0 0 12px; }
  .section h3 { color: var(--text); margin: 12px 0 8px; }

  code {
    background: #1a1a2e;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', Consolas, monospace;
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
    max-width: 100%;
    white-space: pre-wrap;
  }
  pre code { background: none; padding: 0; font-size: 0.85em; }

  .steps { list-style: none; padding: 0; counter-reset: step; }
  .steps li {
    counter-increment: step;
    padding: 12px 12px 12px 48px;
    position: relative;
    margin: 8px 0;
    background: var(--bg);
    border-radius: 8px;
    border: 1px solid var(--border);
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .steps li::before {
    content: counter(step);
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 28px;
    height: 28px;
    line-height: 28px;
    text-align: center;
    background: var(--accent);
    color: var(--bg);
    border-radius: 50%;
    font-weight: bold;
    font-size: 0.9em;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    max-width: 100%;
    display: block;
    overflow-x: auto;
  }
  th, td { padding: 8px 12px; border: 1px solid var(--border); text-align: left; max-width: 45vw; word-wrap: break-word; }
  th { background: var(--bg); color: var(--accent); }
  td { color: var(--text-secondary); }

  .coffee-meter {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    max-width: 100%;
  }
  .coffee-meter .bar { flex: 1; height: 10px; background: var(--border); border-radius: 5px; overflow: hidden; min-width: 50px; }
  .coffee-meter .fill { height: 100%; background: linear-gradient(90deg, #d2991d, #f0c040); border-radius: 5px; }

  .tip {
    background: #1a2e1a;
    border-left: 4px solid var(--success);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    max-width: 100%;
  }
  .tip strong { color: var(--success); }

  .warning-box {
    background: #2d2d1b;
    border-left: 4px solid var(--warning);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    max-width: 100%;
  }

  .footer { text-align: center; color: var(--text-secondary); font-size: 0.85em; margin-top: 20px; max-width: 100%; }
  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  input[type="text"], textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    color: var(--text);
    font-family: inherit;
    font-size: 0.95em;
    max-width: 100%;
    box-sizing: border-box;
  }
  textarea { min-height: 120px; resize: vertical; }
  input:focus, textarea:focus { outline: none; border-color: var(--accent); }

  @media (max-width: 768px) {
    body { padding: 10px; }
    .steps li { padding-left: 40px; }
  }
</style>

<div class="bug-header">
  <h1>🐛 Найден баг!</h1>
  <p>Спокойно. Сейчас всё починим. Костылями.</p>
</div>

<!-- ОПИСАНИЕ -->
<div class="section">
  <h2>🐛 Описание бага</h2>
  <p>Чёткое и краткое описание того, что сломалось.</p>
  <textarea placeholder="Опишите, что пошло не так. Чем подробнее — тем быстрее починим."></textarea>
  
  <div class="tip" style="margin-top: 12px;">
    <strong>💡 Совет:</strong> Хороший баг-репорт содержит: что делали, что ожидали, что получили.
  </div>
</div>

<!-- КАК ВОСПРОИЗВЕСТИ -->
<div class="section">
  <h2>🔄 Как воспроизвести</h2>
  <p>Пожалуйста, опишите шаги, чтобы мы могли повторить ошибку у себя:</p>
  
  <ol class="steps">
    <li>Импортировать <code>kostylpy</code></li>
    <li>Вызвать проблемную функцию</li>
    <li>Увидеть ошибку</li>
  </ol>

  <h3>📝 Код, вызывающий ошибку</h3>
  <pre><code>import kostylpy as kp

# Здесь ваш код
...</code></pre>

  <div class="warning-box">
    <strong>⚠️ Важно:</strong> Убедитесь, что код воспроизводится на последней версии kostylpy. <code>pip install --upgrade kostylpy</code>
  </div>
</div>

<!-- ОЖИДАНИЯ -->
<div class="section">
  <h2>🤔 Ожидаемое поведение</h2>
  <p>Опишите, что должно было произойти вместо ошибки.</p>
  <textarea placeholder="Я ожидал, что функция вернёт 42, а не упадёт с ValueError..."></textarea>
</div>

<!-- ОКРУЖЕНИЕ -->
<div class="section">
  <h2>🖥️ Окружение</h2>
  <p>Эта информация критически важна для воспроизведения бага.</p>
  
  <table>
    <tr>
      <th>Параметр</th>
      <th>Значение</th>
    </tr>
    <tr>
      <td>💻 Операционная система</td>
      <td><input type="text" placeholder="Ubuntu 22.04 / Windows 11 / macOS 14"></td>
    </tr>
    <tr>
      <td>🐍 Версия Python</td>
      <td><input type="text" placeholder="3.11.5"></td>
    </tr>
    <tr>
      <td>🦿 Версия kostylpy</td>
      <td><input type="text" placeholder="3.0.0-beta-kostyl"></td>
    </tr>
    <tr>
      <td>☕ Уровень кофеина</td>
      <td>
        <div class="coffee-meter">
          <span>☕</span>
          <span class="bar"><span class="fill" style="width: 87%;"></span></span>
          <span>87%</span>
        </div>
      </td>
    </tr>
  </table>
</div>

<!-- ДОПОЛНИТЕЛЬНО -->
<div class="section">
  <h2>📸 Скриншоты / Логи</h2>
  <p>Приложите скриншоты ошибки или фрагменты логов. Это очень помогает.</p>
  <textarea placeholder="Вставьте сюда логи или ссылки на скриншоты..."></textarea>

  <h2>📝 Дополнительная информация</h2>
  <p>Любые другие детали, которые могут быть полезны.</p>
  <textarea placeholder="Всё, что считаете важным..."></textarea>
</div>

<!-- FOOTER -->
<hr>
<div class="footer">
  <p>
    🦿 Спасибо за баг-репорт! Мы починим это. Костылями.
  </p>
  <p style="margin-top: 4px;">
    <small>Не забудьте проверить, что вы используете последнюю версию kostylpy.</small>
  </p>
</div>