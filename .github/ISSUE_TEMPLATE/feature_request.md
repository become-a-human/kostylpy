---
name: ✨ Запрос фичи<br>
about: Предложите идею для нового костыля!<br>
title: '[FEATURE] '<br>
labels: ['enhancement', 'новый костыль']<br>
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
    --purple: #a371f7;
    --success: #3fb950;
    --warning: #d2991d;
    --danger: #f85149;
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

  .feature-header {
    background: linear-gradient(135deg, #1a1a3a 0%, #101020 100%);
    border: 1px solid var(--purple);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    text-align: center;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .feature-header h1 { color: var(--purple); margin: 0 0 8px; font-size: 1.8em; }
  .feature-header p { color: var(--text-secondary); margin: 0; font-style: italic; }

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

  .feature-card {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 12px 0;
    max-width: 100%;
  }
  .feature-card-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    max-width: 100%;
    min-width: 0;
    -webkit-tap-highlight-color: transparent;
  }
  .feature-card-item .icon { font-size: 2em; margin-bottom: 8px; }
  .feature-card-item .label { color: var(--text-secondary); font-size: 0.9em; }

  .tip {
    background: #1a2e1a;
    border-left: 4px solid var(--success);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    max-width: 100%;
  }
  .tip strong { color: var(--success); }

  textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    color: var(--text);
    font-family: inherit;
    font-size: 0.95em;
    min-height: 100px;
    resize: vertical;
    max-width: 100%;
    box-sizing: border-box;
  }
  textarea:focus { outline: none; border-color: var(--purple); }

  .footer { text-align: center; color: var(--text-secondary); font-size: 0.85em; margin-top: 20px; max-width: 100%; }
  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  @media (max-width: 768px) {
    body { padding: 10px; }
    .feature-card { grid-template-columns: 1fr 1fr; }
  }
  @media (max-width: 480px) {
    .feature-card { grid-template-columns: 1fr; }
  }
</style>

<div class="feature-header">
  <h1>✨ Идея для нового костыля!</h1>
  <p>Отлично! Расскажите, что вы придумали.</p>
</div>

<!-- ЧТО -->
<div class="section">
  <h2>✨ Описание фичи</h2>
  <p>Опишите костыль, который вы хотите видеть в библиотеке.</p>
  <textarea placeholder="Я хочу, чтобы kostylpy умел автоматически патчить..."></textarea>

  <div class="feature-card" style="margin-top: 16px;">
    <div class="feature-card-item">
      <div class="icon">🛡️</div>
      <div class="label">Защита</div>
    </div>
    <div class="feature-card-item">
      <div class="icon">🔄</div>
      <div class="label">Восстановление</div>
    </div>
    <div class="feature-card-item">
      <div class="icon">📊</div>
      <div class="label">Метрики</div>
    </div>
    <div class="feature-card-item">
      <div class="icon">☕</div>
      <div class="label">Кофе</div>
    </div>
  </div>
</div>

<!-- ЗАЧЕМ -->
<div class="section">
  <h2>🤔 Зачем это нужно?</h2>
  <p>Какую проблему решает этот костыль? Почему без него нельзя?</p>
  <textarea placeholder="Без этого костыля мой код падает каждый второй запрос..."></textarea>

  <div class="tip">
    <strong>💡 Совет:</strong> Опишите реальный сценарий использования. Это поможет нам понять важность фичи.
  </div>
</div>

<!-- API -->
<div class="section">
  <h2>📝 Предлагаемое API</h2>
  <p>Покажите, как должен выглядеть ваш костыль в коде.</p>
  <pre><code># Как это должно выглядеть
import kostylpy as kp

@kp.new_crutch(parameter="value")
def my_function():
    ...</code></pre>
</div>

<!-- АЛЬТЕРНАТИВЫ -->
<div class="section">
  <h2>🔄 Альтернативы</h2>
  <p>Какие ещё способы решения проблемы вы рассматривали?</p>
  <textarea placeholder="Можно конечно обернуть всё в try-except, но это не по-костыльному..."></textarea>
</div>

<!-- ДОПОЛНИТЕЛЬНО -->
<div class="section">
  <h2>📝 Дополнительно</h2>
  <p>Ссылки, примеры из других библиотек, мокапы — всё что угодно.</p>
  <textarea placeholder="Вот пример из другой библиотеки..."></textarea>
</div>

<hr>
<div class="footer">
  <p>
    ✨ Спасибо за идею! Мы рассмотрим её после кофе-брейка.
  </p>
  <p style="margin-top: 4px;">
    <small>Хорошие костыли делают мир лучше. 🦿</small>
  </p>
</div>