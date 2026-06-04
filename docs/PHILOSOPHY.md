<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦿 Философия kostylpy</title>
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
        --orange: #d18616;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.8;
        padding: 20px;
        overflow-x: hidden;
        max-width: 100vw;
    }
    .container { max-width: 800px; margin: 0 auto; }

    .header {
        text-align: center;
        padding: 40px 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 40px;
        max-width: 100%;
    }
    .header h1 { font-size: 2.5em; color: var(--accent-emphasis); border: none; margin-bottom: 8px; }
    .header .subtitle { color: var(--text-secondary); font-style: italic; font-size: 1.2em; }

    h2 {
        color: var(--accent-emphasis);
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        margin: 40px 0 20px;
        font-size: 1.5em;
        max-width: 100%;
    }

    .principle {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        border-left: 4px solid var(--accent);
        max-width: 100%;
        min-width: 0;
        -webkit-tap-highlight-color: transparent;
    }
    .principle:nth-child(odd) { border-left-color: var(--purple); }
    .principle:nth-child(3n) { border-left-color: var(--success); }
    .principle:nth-child(4n) { border-left-color: var(--warning); }
    .principle h3 { color: var(--text); margin: 0 0 12px; font-size: 1.3em; }
    .principle .number {
        display: inline-block;
        width: 36px;
        height: 36px;
        line-height: 36px;
        text-align: center;
        background: var(--accent);
        color: var(--bg);
        border-radius: 50%;
        font-weight: bold;
        margin-right: 12px;
        font-size: 1.1em;
    }

    .quote {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        font-style: italic;
        font-size: 1.1em;
        position: relative;
        max-width: 100%;
    }
    .quote::before {
        content: '"';
        position: absolute;
        top: -10px;
        left: 16px;
        font-size: 4em;
        color: var(--accent);
        opacity: 0.3;
    }
    .quote .author { margin-top: 12px; color: var(--text-secondary); font-style: normal; font-size: 0.9em; }

    .commandment {
        background: linear-gradient(135deg, #1a1a2e 0%, #161b22 100%);
        border: 2px solid var(--accent);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        text-align: center;
        max-width: 100%;
    }
    .commandment h3 { color: var(--accent-emphasis); margin-bottom: 16px; }
    .commandment ol { text-align: left; display: inline-block; }
    .commandment li { padding: 8px 0; font-size: 1.05em; max-width: 100%; }

    .coffee-meter {
        display: flex;
        align-items: center;
        gap: 8px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 20px 0;
        max-width: 100%;
    }
    .coffee-meter .bar { flex: 1; height: 12px; background: var(--border); border-radius: 6px; overflow: hidden; min-width: 50px; }
    .coffee-meter .fill { height: 100%; background: linear-gradient(90deg, #d2991d, #f0c040); border-radius: 6px; }

    code {
        background: var(--bg-secondary);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9em;
        max-width: 100%;
        display: inline-block;
        vertical-align: top;
    }

    a {
        color: var(--accent);
        -webkit-user-select: text;
        -moz-user-select: text;
        user-select: text;
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

    @media (max-width: 768px) {
        body { padding: 10px; }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.3em; }
        .principle { padding: 16px; }
        .quote { font-size: 1em; }
    }
</style>
</head>
<body>

<div class="container">

    <div class="header">
        <h1>🦿 Философия kostylpy</h1>
        <p class="subtitle">Или "Почему костыли — это не баг, а фича"</p>
    </div>

    <!-- INTRO -->
    <div class="quote">
        <p>Любой код может упасть. Но с достаточным количеством костылей — никогда.</p>
        <p class="author">— Коллектив костылестроителей им. В.Е.Лосипедова</p>
    </div>

    <p>
        <strong>kostylpy</strong> — это не просто библиотека. Это <strong>образ жизни</strong>.
        Это философия разработки, которая гласит: если что-то может сломаться — 
        обложи это костылями. Если не может — всё равно обложи, на всякий случай.
    </p>

    <div class="coffee-meter">
        <span class="cup">☕</span>
        <span>Уровень кофеина:</span>
        <span class="bar"><span class="fill"></span></span>
        <span class="label">87% (достаточно для костылей)</span>
    </div>

    <hr>

    <!-- PRINCIPLES -->
    <h2>📜 Основные принципы</h2>

    <div class="principle">
        <h3><span class="number">1</span> Работает — не трогай</h3>
        <p>
            Это <strong>священное правило</strong>. Если код работает — 
            не пытайся его улучшить, отрефакторить или оптимизировать.
            Даже если там <code>return False</code> вместо <code>pass</code>.
            Даже если там вложенный <code>try-except</code> на 10 уровней.
            <strong>РАБОТАЕТ — ЗНАЧИТ РАБОТАЕТ.</strong>
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: любой рефакторинг создаёт новые баги. Не рефакторь.</em>
        </p>
    </div>

    <div class="principle">
        <h3><span class="number">2</span> Не работает — добавь костылей</h3>
        <p>
            Если код всё-таки упал — не паникуй. Просто добавь ещё костылей.
            Один костыль хорошо, два лучше, три — продакшен-реди.
            Если костылей больше <strong>42</strong> — ты на верном пути.
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: количество костылей прямо пропорционально надёжности системы.</em>
        </p>
    </div>

    <div class="principle">
        <h3><span class="number">3</span> Кофе обязателен</h3>
        <p>
            Без кофе костыли не работают. Это научный факт.
            Минимум одна кружка перед каждым деплоем.
            Оптимально — непрерывный поток кофеина в течение всего рабочего дня.
            <strong>Кофе-метрика в kostylpy не просто так.</strong>
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: если кофе закончился — останови разработку.</em>
        </p>
    </div>

    <div class="principle">
        <h3><span class="number">4</span> Тесты — для слабаков</h3>
        <p>
            Если код работает на проде — зачем тесты? Но если уж пишешь тесты —
            они тоже должны быть на костылях. <code>@kp.safe</code> в каждом тесте.
            <code>try-except</code> вокруг каждого assert'а.
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: лучший тест — это продакшен.</em>
        </p>
    </div>

    <div class="principle">
        <h3><span class="number">5</span> Документация не нужна</h3>
        <p>
            Читайте исходники. Если непонятно — добавьте костылей.
            Документация устаревает, исходники — никогда (потому что мы их не меняем, см. принцип 1).
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: этот документ — исключение, подтверждающее правило.</em>
        </p>
    </div>

    <div class="principle">
        <h3><span class="number">6</span> Всё есть костыль</h3>
        <p>
            Эта библиотека — костыль. Ваш код — костыль. Весь софт — костыль.
            Даже сам Python — это костыль над C. А C — костыль над ассемблером.
            Примите это и добавьте ещё костылей.
        </p>
        <p style="margin-top: 8px; color: var(--text-secondary);">
            <em>Следствие: нет смысла бороться с костылями. Станьте с ними одним целым.</em>
        </p>
    </div>

    <hr>

    <!-- COMMANDMENTS -->
    <h2>📯 10 заповедей костылестроителя</h2>

    <div class="commandment">
        <ol>
            <li><strong>Не рефакторь</strong> работающий код.</li>
            <li><strong>Не удаляй</strong> старые костыли — они ещё пригодятся.</li>
            <li><strong>Не доверяй</strong> входным данным — валидируй всё.</li>
            <li><strong>Не падай</strong> — используй <code>@kp.safe</code>.</li>
            <li><strong>Повторяй</strong> при ошибке — <code>@kp.retry</code> твой друг.</li>
            <li><strong>Логируй всё</strong> — <code>kp.logger</code> помнит.</li>
            <li><strong>Измеряй всё</strong> — <code>kp.metrics</code> считает.</li>
            <li><strong>Пей кофе</strong> — <code>kp.metrics.coffee.drink()</code>.</li>
            <li><strong>Делись костылями</strong> — создавай Pull Request'ы.</li>
            <li><strong>Помни</strong>: ты не один такой. Все пишут костыли.</li>
        </ol>
    </div>

    <hr>

    <!-- WISDOM -->
    <h2>🧠 Мудрость костылестроителей</h2>

    <div class="quote">
        <p>Костыли — это не баг, а фича. Архитектурное решение.</p>
        <p class="author">— Сеньор-разработчик на код-ревью</p>
    </div>

    <div class="quote">
        <p>Если ваш код работает без костылей — значит вы просто ещё не нашли баги.</p>
        <p class="author">— Отдел тестирования</p>
    </div>

    <div class="quote">
        <p>Я не пишу костыли. Я создаю временные архитектурные решения с неопределённым сроком действия.</p>
        <p class="author">— Архитектор ПО</p>
    </div>

    <div class="quote">
        <p>Это не баг, это фича. Костыльная фича.</p>
        <p class="author">— Продакт-менеджер</p>
    </div>

    <div class="quote">
        <p>Костыли — это как джаз. Если ты не понимаешь, что происходит, просто добавь ещё костылей.</p>
        <p class="author">— Джазовый программист</p>
    </div>

    <hr>

    <!-- ZEN -->
    <h2>🧘 Дзен костылизации</h2>

    <div class="principle">
        <h3>Медитация первая: Принятие</h3>
        <p>
            Ты не можешь написать идеальный код. Никто не может. 
            Прими свои ограничения. Прими костыли. Стань с ними единым целым.
        </p>
    </div>

    <div class="principle">
        <h3>Медитация вторая: Отпускание</h3>
        <p>
            Отпусти страх перед багами. Они всё равно будут.
            Отпусти желание всё исправить. Просто добавь костыль.
            Отпусти тревогу перед деплоем в пятницу вечером. Костыли спасут.
        </p>
    </div>

    <div class="principle">
        <h3>Медитация третья: Просветление</h3>
        <p>
            Ты достиг просветления когда:
            <br>— Твой <code>try-except</code> занимает больше строк, чем бизнес-логика
            <br>— Ты добавляешь костыли на автопилоте
            <br>— Ты видишь красоту в <code>except: pass</code>
            <br>— Кофе закончился, но ты продолжаешь
        </p>
    </div>

    <hr>

    <!-- FINAL -->
    <h2>🌟 Путь костылестроителя</h2>

    <p style="text-align: center; font-size: 1.1em;">
        <strong>Junior</strong> — боится костылей<br>
        <strong>Middle</strong> — использует костыли<br>
        <strong>Senior</strong> — понимает костыли<br>
        <strong>Lead</strong> — проектирует костыли<br>
        <strong>Architect</strong> — сам стал костылём<br>
        <strong>Kostyl Master</strong> — 🦿
    </p>

    <hr>

    <!-- FOOTER -->
    <div class="footer">
        <p>
            🦿 <strong>Помни:</strong> ты не один. Все пишут костыли.
            Просто мы сделали это красиво.
        </p>
        <p style="margin-top: 12px;">
            <a href="API.md">📚 API Reference</a> •
            <a href="EXAMPLES.md">🎮 Примеры</a> •
            <a href="../README.md">🏠 Главная</a>
        </p>
        <p style="margin-top: 16px;">
            <small>kostylpy v3.0.0-beta-kostyl-enterprise-edition</small><br>
            <small>Философия одобрена Коллективом костылестроителей им. В.Е.Лосипедова</small>
        </p>
    </div>

</div>

</body>
</html>