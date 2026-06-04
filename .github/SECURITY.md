<!-- .github/SECURITY.md -->

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
  pre, code {
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
    line-height: 1.7;
    padding: 20px;
    overflow-x: hidden;
    max-width: 100vw;
  }

  .security-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #101020 100%);
    border: 2px solid var(--danger);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    text-align: center;
    max-width: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  .security-header h1 { color: var(--danger); margin: 0 0 8px; font-size: 2em; }
  .security-header .subtitle { color: var(--text-secondary); font-style: italic; margin: 0; font-size: 1.1em; }

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
    font-size: 1.3em;
  }
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
  pre code { background: none; padding: 0; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
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
  th { background: var(--bg); color: var(--accent); font-weight: 600; }
  td { color: var(--text-secondary); }

  .version-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
  }
  .version-supported { background: #1a3a2a; color: var(--success); }
  .version-unsupported { background: #2d1b1b; color: var(--danger); }

  .reward-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 12px 0;
    max-width: 100%;
  }
  .reward-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    max-width: 100%;
    min-width: 0;
    -webkit-tap-highlight-color: transparent;
  }
  .reward-card .icon { font-size: 2.5em; margin-bottom: 8px; }
  .reward-card .label { color: var(--text); font-weight: 600; }
  .reward-card .desc { color: var(--text-secondary); font-size: 0.85em; margin-top: 4px; }

  .contact-box {
    background: #1a1a2e;
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 16px 0;
    max-width: 100%;
  }
  .contact-box .email {
    font-size: 1.3em;
    color: var(--accent-emphasis);
    font-family: 'JetBrains Mono', monospace;
    -webkit-user-select: text;
    -moz-user-select: text;
    user-select: text;
  }
  .contact-box .response-time {
    color: var(--text-secondary);
    margin-top: 8px;
    font-size: 0.9em;
  }

  .danger-box {
    background: #2d1b1b;
    border-left: 4px solid var(--danger);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    max-width: 100%;
  }
  .danger-box strong { color: var(--danger); }

  .tip {
    background: #1a2e1a;
    border-left: 4px solid var(--success);
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    max-width: 100%;
  }
  .tip strong { color: var(--success); }

  .footer { text-align: center; color: var(--text-secondary); font-size: 0.85em; margin-top: 20px; max-width: 100%; }
  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  @media (max-width: 768px) {
    body { padding: 10px; }
    .reward-cards { grid-template-columns: 1fr 1fr; }
    h1 { font-size: 1.5em; }
  }
  @media (max-width: 480px) {
    .reward-cards { grid-template-columns: 1fr; }
  }
</style>

<div class="security-header">
  <h1>🔒 Политика безопасности</h1>
  <p class="subtitle">Мы относимся к безопасности серьёзно. Насколько это возможно с костылями.</p>
</div>

<!-- ПОДДЕРЖИВАЕМЫЕ ВЕРСИИ -->
<div class="section">
  <h2>📋 Поддерживаемые версии</h2>

  <table>
    <tr>
      <th>Версия</th>
      <th>Статус</th>
      <th>Поддержка до</th>
    </tr>
    <tr>
      <td><strong>3.0.x</strong></td>
      <td><span class="version-badge version-supported">✅ Поддерживается</span></td>
      <td>Пока не выйдет 4.0</td>
    </tr>
    <tr>
      <td><strong>2.0.x</strong></td>
      <td><span class="version-badge version-unsupported">❌ Не поддерживается</span></td>
      <td>Закончилась вчера</td>
    </tr>
    <tr>
      <td><strong>1.0.x</strong></td>
      <td><span class="version-badge version-unsupported">❌ Не поддерживается</span></td>
      <td>Никогда не существовала</td>
    </tr>
    <tr>
      <td><strong>0.x</strong></td>
      <td><span class="version-badge version-unsupported">💀 Страшно вспоминать</span></td>
      <td>До появления костылей</td>
    </tr>
  </table>
</div>

<!-- КАК СООБЩИТЬ -->
<div class="section">
  <h2>📢 Как сообщить об уязвимости</h2>

  <p>Если вы нашли уязвимость в безопасности — <strong>не создавайте публичный issue</strong>.</p>

  <div class="contact-box">
    <p style="margin-bottom: 12px; color: var(--text-secondary);">Напишите нам на почту:</p>
    <p class="email">🔐 the1stplayergetready@gmail.com</p>
    <p class="response-time">⏱️ Мы ответим в течение <strong>42 часов</strong> и выпустим патч.<br>(Или добавим костылей.)</p>
  </div>

  <div class="tip">
    <strong>🔐 Что включить в отчёт:</strong>
    <ul style="margin: 8px 0 0 20px; color: var(--text-secondary);">
      <li>Описание уязвимости</li>
      <li>Шаги для воспроизведения</li>
      <li>Версия kostylpy</li>
      <li>Ваш уровень кофеина (опционально)</li>
    </ul>
  </div>
</div>

<!-- НАГРАДА -->
<div class="section">
  <h2>🏆 Награда за найденные уязвимости</h2>

  <div class="reward-cards">
    <div class="reward-card">
      <div class="icon">🦿</div>
      <div class="label">Вечная благодарность</div>
      <div class="desc">Ваше имя в README (очень мелким шрифтом)</div>
    </div>
    <div class="reward-card">
      <div class="icon">☕</div>
      <div class="label">Виртуальный кофе</div>
      <div class="desc">1 кофе-брейк в вашу честь</div>
    </div>
    <div class="reward-card">
      <div class="icon">📜</div>
      <div class="label">Сертификат</div>
      <div class="desc">PDF-сертификат костылестроителя</div>
    </div>
    <div class="reward-card">
      <div class="icon">🌟</div>
      <div class="label">Звезда на GitHub</div>
      <div class="desc">Ну, вы и так её поставите</div>
    </div>
  </div>

  <div class="danger-box" style="margin-top: 20px;">
    <strong>⚠️ Важно:</strong> Мы <strong>не выплачиваем</strong> денежные вознаграждения (bug bounties).
    Всё что у нас есть — это костыли и кофе.
  </div>
</div>

<!-- АУДИТ -->
<div class="section">
  <h2>🔍 Аудит безопасности</h2>

  <table>
    <tr>
      <th>Тип аудита</th>
      <th>Статус</th>
      <th>Комментарий</th>
    </tr>
    <tr>
      <td>Внешний аудит</td>
      <td><span class="version-badge version-unsupported">❌ Не проводился</span></td>
      <td>Слишком дорого</td>
    </tr>
    <tr>
      <td>Внутренний аудит</td>
      <td><span class="version-badge version-unsupported">❌ Не проводился</span></td>
      <td>Слишком лень</td>
    </tr>
    <tr>
      <td>Автоматическое сканирование</td>
      <td><span class="version-badge version-supported">✅ Проведено</span></td>
      <td>Линтер сказал "всё ок"</td>
    </tr>
    <tr>
      <td>Ручное тестирование</td>
      <td><span class="version-badge version-supported">✅ Проведено</span></td>
      <td>Автор сказал "работает"</td>
    </tr>
    <tr>
      <td>Проверка кофе-метрики</td>
      <td><span class="version-badge version-supported">✅ Проведено</span></td>
      <td>87% заряда</td>
    </tr>
  </table>
</div>

<!-- РЕКОМЕНДАЦИИ -->
<div class="section">
  <h2>🛡️ Рекомендации по безопасности</h2>

  <ul style="padding-left: 20px; color: var(--text-secondary);">
    <li style="margin: 8px 0;">
      <strong>Не используйте в продакшене.</strong> Серьёзно. Это шутка.
    </li>
    <li style="margin: 8px 0;">
      <strong>Если всё же используете</strong> — убедитесь что <code>kp.config.debug = False</code>.
    </li>
    <li style="margin: 8px 0;">
      <strong>Не передавайте</strong> чувствительные данные в <code>print()</code>. Мы перехватываем print, но лучше не рисковать.
    </li>
    <li style="margin: 8px 0;">
      <strong>Блокируйте опасные импорты:</strong> <code>kp.block_imports('os', 'subprocess')</code>.
    </li>
    <li style="margin: 8px 0;">
      <strong>Пейте кофе.</strong> Без кофе костыли не работают.
    </li>
  </ul>
</div>

<!-- ОТВЕТСТВЕННОСТЬ -->
<div class="section">
  <h2>⚠️ Раскрытие ответственности</h2>

  <div class="danger-box">
    <p>
      Эта библиотека <strong>не предназначена</strong> для использования в средах, 
      требующих реальной безопасности.
    </p>
    <p style="margin-top: 8px;">
      Если вы используете kostylpy для защиты:
    </p>
    <ul style="margin: 8px 0 0 20px; color: var(--text-secondary);">
      <li>Банковских систем — <strong>НЕ НАДО</strong></li>
      <li>Медицинских данных — <strong>НЕ НАДО</strong></li>
      <li>Ядерных реакторов — <strong>ТОЧНО НЕ НАДО</strong></li>
    </ul>
    <p style="margin-top: 12px;">
      Мы снимаем с себя всякую ответственность. Используйте на свой страх и риск.
    </p>
    <p>
      И добавьте костылей.
    </p>
  </div>
</div>

<!-- ФУТЕР -->
<hr>
<div class="footer">
  <p>
    🔒 Безопасность — это важно. Костыли — ещё важнее.
  </p>
  <p style="margin-top: 4px;">
    <small>Последнее обновление: когда-то в 2026 году</small>
  </p>
  <p style="margin-top: 4px;">
    <small>kostylpy v3.0.0-beta-kostyl-enterprise-edition</small>
  </p>
</div>