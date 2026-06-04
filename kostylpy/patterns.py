"""
Паттерны замены kostylpy.
Набор регулярных выражений и правил для автоматического поиска
и костылизации проблемного кода. Находит баги, уязвимости,
плохие практики и закомментированный код.

Содержит:
- CodePattern — шаблон для поиска в коде
- PatternCategory — категории паттернов
- PatternSeverity — серьёзность найденного
- PatternMatch — результат совпадения
- PatternRegistry — реестр всех паттернов
- Встроенные паттерны (50+ штук)
- Функции для применения паттернов
- Авто-фиксы для найденных проблем
"""

import re
import ast
import sys
import os
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем константы
try:
    from .constants import Emoji, Colors
except ImportError:
    class Emoji:
        KOSTYL = "🦿"
        ERROR = "❌"
        WARNING = "⚠️"
        INFO = "ℹ️"
        FIX = "🩹"
        BUG = "🐛"
        SECURITY = "🔒"
        PERFORMANCE = "⚡"
        STYLE = "✨"
        DANGER = "💀"
        SUCCESS = "✅"
    class Colors:
        @staticmethod
        def red(t): return t
        @staticmethod
        def yellow(t): return t
        @staticmethod
        def green(t): return t
        RESET = ""

# ═══════════════════════════════════════════════════════════════
# КАТЕГОРИИ И СЕРЬЁЗНОСТЬ
# ═══════════════════════════════════════════════════════════════

class PatternCategory(Enum):
    """Категории паттернов."""
    BUG = ("🐛", "Потенциальный баг")
    SECURITY = ("🔒", "Уязвимость безопасности")
    PERFORMANCE = ("⚡", "Проблема производительности")
    STYLE = ("✨", "Стиль кода")
    BEST_PRACTICE = ("📚", "Лучшие практики")
    DEPRECATED = ("⏳", "Устаревший код")
    ERROR_PRONE = ("💀", "Склонный к ошибкам")
    KOSTYL = ("🦿", "Требует костыля")
    PYTHONIC = ("🐍", "Не-pythonic")
    COMPATIBILITY = ("🔧", "Совместимость")

class PatternSeverity(Enum):
    """Серьёзность паттерна."""
    INFO = (1, "ℹ️", "Информация")
    LOW = (2, "🟢", "Низкая")
    MEDIUM = (3, "🟡", "Средняя")
    HIGH = (4, "🟠", "Высокая")
    CRITICAL = (5, "🔴", "Критическая")
    NUCLEAR = (10, "💀", "Ядерная")

# ═══════════════════════════════════════════════════════════════
# ПАТТЕРН И СОВПАДЕНИЕ
# ═══════════════════════════════════════════════════════════════

@dataclass
class PatternMatch:
    """Результат совпадения паттерна."""
    pattern_name: str
    category: PatternCategory
    severity: PatternSeverity
    line_number: int
    column: int
    matched_text: str
    message: str
    suggestion: str = ""
    auto_fix: Optional[str] = None
    context: str = ""  # Окружающий код
    file_path: str = ""
    
    def to_dict(self) -> dict:
        return {
            'pattern': self.pattern_name,
            'category': self.category.value[1],
            'severity': self.severity.value[2],
            'line': self.line_number,
            'column': self.column,
            'matched': self.matched_text[:100],
            'message': self.message,
            'suggestion': self.suggestion,
            'file': self.file_path,
        }
    
    def __str__(self):
        return (
            f"{self.severity.value[1]} [{self.category.value[0]} {self.pattern_name}] "
            f"Строка {self.line_number}: {self.message}"
        )

@dataclass
class CodePattern:
    """Шаблон для поиска в коде."""
    name: str
    category: PatternCategory
    severity: PatternSeverity
    description: str
    # Один или несколько паттернов
    patterns: List[str] = field(default_factory=list)
    # AST-проверка (функция, принимающая AST узел)
    ast_check: Optional[Callable] = None
    # Авто-фикс (функция или строка замены)
    fix: Optional[Union[str, Callable]] = None
    # Сообщение при нахождении
    message_template: str = "Найдено: {match}"
    # Подсказка по исправлению
    suggestion: str = ""
    # Флаги регулярного выражения
    flags: int = 0
    
    def check_line(self, line: str, line_num: int) -> List[PatternMatch]:
        """Проверяет строку на совпадение."""
        matches = []
        
        for pattern in self.patterns:
            for match in re.finditer(pattern, line, self.flags):
                matches.append(PatternMatch(
                    pattern_name=self.name,
                    category=self.category,
                    severity=self.severity,
                    line_number=line_num,
                    column=match.start(),
                    matched_text=match.group(),
                    message=self.message_template.format(match=match.group()),
                    suggestion=self.suggestion,
                    auto_fix=self._get_fix(match, line) if self.fix else None,
                ))
        
        return matches
    
    def _get_fix(self, match: re.Match, line: str) -> Optional[str]:
        """Получает исправление для совпадения."""
        if self.fix is None:
            return None
        
        if callable(self.fix):
            return self.fix(match, line)
        elif isinstance(self.fix, str):
            # Простая замена
            return match.expand(self.fix)
        
        return None

# ═══════════════════════════════════════════════════════════════
# ВСТРОЕННЫЕ ПАТТЕРНЫ
# ═══════════════════════════════════════════════════════════════

BUILTIN_PATTERNS: List[CodePattern] = [
    # ═══════════════════════════════════════════
    # БАГИ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="bare-except",
        category=PatternCategory.BUG,
        severity=PatternSeverity.HIGH,
        description="Голый except (ловит даже SystemExit и KeyboardInterrupt)",
        patterns=[r'except\s*:'],
        message_template="Голый except! Ловит вообще всё, включая системные исключения.",
        suggestion="Используйте 'except Exception:' или конкретный тип исключения.",
        fix=r'except Exception:  # kostylpy: добавлен Exception',
    ),
    
    CodePattern(
        name="mutable-default-arg",
        category=PatternCategory.BUG,
        severity=PatternSeverity.HIGH,
        description="Изменяемый аргумент по умолчанию (list, dict, set)",
        patterns=[
            r'def\s+\w+\s*\([^)]*=\s*\[\s*\]',
            r'def\s+\w+\s*\([^)]*=\s*\{\s*\}',
            r'def\s+\w+\s*\([^)]*=\s*set\(\s*\)',
        ],
        message_template="Изменяемый аргумент по умолчанию! Все вызовы разделяют один объект.",
        suggestion="Используйте None и создавайте объект внутри функции.",
    ),
    
    CodePattern(
        name="silent-exception-pass",
        category=PatternCategory.BUG,
        severity=PatternSeverity.MEDIUM,
        description="Пустой блок except с pass",
        patterns=[r'except[^:]*:\s*pass\s*$'],
        message_template="Пустой except с pass — ошибка будет молча проглочена.",
        suggestion="Как минимум логируйте ошибку: except Exception as e: logger.error(e)",
    ),
    
    CodePattern(
        name="return-in-finally",
        category=PatternCategory.BUG,
        severity=PatternSeverity.HIGH,
        description="return в блоке finally (перезаписывает исключения)",
        patterns=[r'finally\s*:[^}]*\breturn\b'],
        message_template="return в finally! Исключения будут потеряны.",
        suggestion="Не используйте return в finally.",
    ),
    
    CodePattern(
        name="undefined-variable-in-except",
        category=PatternCategory.BUG,
        severity=PatternSeverity.MEDIUM,
        description="Потенциально неопределённая переменная в except",
        patterns=[r'except\s+\w+\s+as\s+(\w+)[^:]*:[^}]*\b\1\b'],
        message_template="Переменная исключения может быть не определена.",
        suggestion="Проверьте область видимости переменной исключения.",
    ),
    
    # ═══════════════════════════════════════════
    # БЕЗОПАСНОСТЬ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="dangerous-eval",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.NUCLEAR,
        description="Использование eval() — выполнение произвольного кода",
        patterns=[r'\beval\s*\('],
        message_template="eval()! Выполнение произвольного кода — КРИТИЧЕСКАЯ уязвимость!",
        suggestion="Замените на ast.literal_eval() или другой безопасный парсер.",
    ),
    
    CodePattern(
        name="dangerous-exec",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.NUCLEAR,
        description="Использование exec() — выполнение произвольного кода",
        patterns=[r'\bexec\s*\('],
        message_template="exec()! КРИТИЧЕСКАЯ уязвимость безопасности!",
        suggestion="Никогда не используйте exec() с пользовательскими данными.",
    ),
    
    CodePattern(
        name="hardcoded-password",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.CRITICAL,
        description="Закодированный пароль в коде",
        patterns=[
            r'(?i)(password|passwd|pwd|secret|token|api_key)\s*=\s*["\'][^"\']+["\']',
        ],
        message_template="Пароль/секрет в коде! Попадёт в репозиторий.",
        suggestion="Используйте переменные окружения или секретный менеджер.",
    ),
    
    CodePattern(
        name="sql-injection-risk",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.CRITICAL,
        description="Потенциальная SQL-инъекция (конкатенация строк в запросе)",
        patterns=[
            r'(?i)(execute|cursor\.execute)\s*\(\s*["\'].*%s.*["\'].*%',
            r'(?i)(execute|cursor\.execute)\s*\(\s*f["\']',
            r'(?i)\.format\s*\([^)]*\)\s*\.execute',
        ],
        message_template="Возможная SQL-инъекция! Не конкатенируйте строки в SQL.",
        suggestion="Используйте параметризованные запросы: cursor.execute(sql, params)",
    ),
    
    CodePattern(
        name="insecure-deserialization",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.CRITICAL,
        description="Небезопасная десериализация (pickle)",
        patterns=[r'\bpickle\.loads?\s*\('],
        message_template="pickle.loads() с недоверенными данными — выполнение кода!",
        suggestion="Используйте JSON или другие безопасные форматы.",
    ),
    
    CodePattern(
        name="http-not-https",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.MEDIUM,
        description="Использование HTTP вместо HTTPS",
        patterns=[r'["\']http://[^"\']+["\']'],
        message_template="HTTP используется вместо HTTPS.",
        suggestion="Используйте HTTPS для всех внешних запросов.",
    ),
    
    # ═══════════════════════════════════════════
    # ПРОИЗВОДИТЕЛЬНОСТЬ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="linear-list-search",
        category=PatternCategory.PERFORMANCE,
        severity=PatternSeverity.LOW,
        description="Поиск в списке (O(n)) вместо множества (O(1))",
        patterns=[r'if\s+\w+\s+in\s+\[[^\]]+\]:'],
        message_template="Поиск в списке — O(n). Для больших списков используйте set.",
        suggestion="Замените список на множество: if x in {...}",
    ),
    
    CodePattern(
        name="string-concatenation-loop",
        category=PatternCategory.PERFORMANCE,
        severity=PatternSeverity.MEDIUM,
        description="Конкатенация строк в цикле (создаёт много временных объектов)",
        patterns=[r'for\s+\w+\s+in[^:]*:\s*\w+\s*\+=\s*["\']'],
        message_template="Конкатенация строк в цикле — O(n²).",
        suggestion="Используйте ''.join() или StringIO.",
    ),
    
    CodePattern(
        name="list-comprehension-side-effects",
        category=PatternCategory.PERFORMANCE,
        severity=PatternSeverity.LOW,
        description="Списковое включение с побочными эффектами",
        patterns=[r'\[[^\]]*\.append\s*\([^\]]*\]'],
        message_template="Списковое включение с побочными эффектами — антипаттерн.",
        suggestion="Используйте обычный цикл for.",
    ),
    
    CodePattern(
        name="repeated-dot-access",
        category=PatternCategory.PERFORMANCE,
        severity=PatternSeverity.LOW,
        description="Повторный доступ через точку в цикле",
        patterns=[r'for[^:]*:\s*\w+\.\w+\.\w+'],
        message_template="Повторный доступ к атрибутам в цикле.",
        suggestion="Сохраните ссылку в локальную переменную.",
    ),
    
    # ═══════════════════════════════════════════
    # СТИЛЬ КОДА
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="print-debug",
        category=PatternCategory.STYLE,
        severity=PatternSeverity.LOW,
        description="Отладочный print в коде",
        patterns=[
            r'print\s*\(\s*["\'](DEBUG|TEST|HERE|TEMP)',
            r'print\s*\(\s*["\']\d+["\']\s*\)',
        ],
        message_template="Похоже на отладочный print.",
        suggestion="Удалите перед коммитом или используйте logging.debug().",
    ),
    
    CodePattern(
        name="todo-fixme",
        category=PatternCategory.STYLE,
        severity=PatternSeverity.INFO,
        description="TODO/FIXME/HACK в коде",
        patterns=[r'#\s*(TODO|FIXME|HACK|XXX|KLUDGE|WORKAROUND)\b'],
        message_template="Найдена пометка {match}.",
        suggestion="Не забудьте исправить перед релизом!",
    ),
    
    CodePattern(
        name="commented-code",
        category=PatternCategory.STYLE,
        severity=PatternSeverity.LOW,
        description="Закомментированный код",
        patterns=[
            r'^\s*#\s*(def |class |if |for |while |return |import |from )',
        ],
        message_template="Закомментированный код.",
        suggestion="Удалите закомментированный код, он есть в истории git.",
    ),
    
    CodePattern(
        name="trailing-whitespace",
        category=PatternCategory.STYLE,
        severity=PatternSeverity.INFO,
        description="Пробелы в конце строки",
        patterns=[r'[ \t]+$'],
        message_template="Пробелы в конце строки.",
        suggestion="Настройте редактор на автоматическое удаление.",
        fix=r'',  # Удалить пробелы
    ),
    
    CodePattern(
        name="mixed-indentation",
        category=PatternCategory.STYLE,
        severity=PatternSeverity.MEDIUM,
        description="Смешанные табы и пробелы",
        patterns=[r'^\t+ [ ]', r'^ [ ]+\t'],
        message_template="Смешанные табы и пробелы в отступах!",
        suggestion="Используйте только пробелы (4 пробела на отступ).",
    ),
    
    # ═══════════════════════════════════════════
    # ЛУЧШИЕ ПРАКТИКИ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="global-variable",
        category=PatternCategory.BEST_PRACTICE,
        severity=PatternSeverity.MEDIUM,
        description="Использование global",
        patterns=[r'\bglobal\s+\w+'],
        message_template="Использование global — плохая практика.",
        suggestion="Передавайте переменные как параметры или используйте класс.",
    ),
    
    CodePattern(
        name="wildcard-import",
        category=PatternCategory.BEST_PRACTICE,
        severity=PatternSeverity.MEDIUM,
        description="Импорт со звёздочкой",
        patterns=[r'from\s+\S+\s+import\s+\*'],
        message_template="Импорт * загрязняет пространство имён.",
        suggestion="Импортируйте только нужные имена.",
    ),
    
    CodePattern(
        name="too-broad-except",
        category=PatternCategory.BEST_PRACTICE,
        severity=PatternSeverity.MEDIUM,
        description="Слишком широкий except (ловит всё)",
        patterns=[r'except\s+(Exception|BaseException)\s*:'],
        message_template="Слишком широкий except.",
        suggestion="Ловите конкретные типы исключений.",
    ),
    
    CodePattern(
        name="no-context-manager",
        category=PatternCategory.BEST_PRACTICE,
        severity=PatternSeverity.LOW,
        description="Открытие файла без контекстного менеджера",
        patterns=[r'(\w+)\s*=\s*open\s*\([^)]+\)(?!.*\bwith\b)'],
        message_template="open() без with — файл может не закрыться.",
        suggestion="Используйте: with open(...) as f:",
    ),
    
    CodePattern(
        name="magic-numbers",
        category=PatternCategory.BEST_PRACTICE,
        severity=PatternSeverity.LOW,
        description="Магические числа (кроме 0, 1, -1, 2)",
        patterns=[
            r'(?<!\w)(?<!["\'])(?<!#\s)(?<!\.)(\d{3,}|[3-9]\d{1,})(?!\w)(?!["\'])',
        ],
        message_template="Магическое число: {match}.",
        suggestion="Вынесите в именованную константу.",
    ),
    
    # ═══════════════════════════════════════════
    # УСТАРЕВШИЙ КОД
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="python2-print",
        category=PatternCategory.DEPRECATED,
        severity=PatternSeverity.HIGH,
        description="Python 2 синтаксис print",
        patterns=[r'^\s*print\s+[^(]'],
        message_template="Python 2 синтаксис print (без скобок).",
        suggestion="Добавьте скобки: print(...)",
        fix=r'print(\g<0>)',  # Не идеально, но идея понятна
    ),
    
    CodePattern(
        name="old-style-class",
        category=PatternCategory.DEPRECATED,
        severity=PatternSeverity.LOW,
        description="Класс в старом стиле (без object)",
        patterns=[r'class\s+\w+\s*:'],
        message_template="Класс без явного наследования.",
        suggestion="В Python 3 все классы new-style, но лучше указать явно.",
    ),
    
    CodePattern(
        name="deprecated-assert-equals",
        category=PatternCategory.DEPRECATED,
        severity=PatternSeverity.LOW,
        description="Устаревший assertAlmostEquals",
        patterns=[r'\.assertAlmostEquals?\s*\('],
        message_template="Устаревший метод тестирования.",
        suggestion="Используйте assertEqual/assertAlmostEqual.",
    ),
    
    # ═══════════════════════════════════════════
    # СКЛОННЫЕ К ОШИБКАМ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="division-by-zero-risk",
        category=PatternCategory.ERROR_PRONE,
        severity=PatternSeverity.HIGH,
        description="Потенциальное деление на ноль",
        patterns=[r'(\w+)\s*/\s*(\w+)\s*$'],
        message_template="Возможно деление на ноль без проверки.",
        suggestion="Добавьте проверку: if denominator != 0:",
    ),
    
    CodePattern(
        name="none-comparison-with-is",
        category=PatternCategory.ERROR_PRONE,
        severity=PatternSeverity.MEDIUM,
        description="Сравнение с None через ==",
        patterns=[r'==\s*None|None\s*=='],
        message_template="Сравнение с None через == вместо is.",
        suggestion="Используйте 'is None' или 'is not None'.",
    ),
    
    CodePattern(
        name="mutable-keyword-default",
        category=PatternCategory.ERROR_PRONE,
        severity=PatternSeverity.MEDIUM,
        description="Изменяемый объект как значение по умолчанию",
        patterns=[r'=\s*\{\s*\}\s*[,)]', r'=\s*\[\s*\]\s*[,)]'],
        message_template="Изменяемый объект как аргумент по умолчанию!",
        suggestion="Используйте None и создавайте объект в теле функции.",
    ),
    
    CodePattern(
        name="float-equality",
        category=PatternCategory.ERROR_PRONE,
        severity=PatternSeverity.MEDIUM,
        description="Сравнение float через ==",
        patterns=[r'\d+\.\d+\s*==\s*\d+\.\d+'],
        message_template="Сравнение float через == ненадёжно.",
        suggestion="Используйте math.isclose() или допуск.",
    ),
    
    # ═══════════════════════════════════════════
    # КОСТЫЛИ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="nested-try-except",
        category=PatternCategory.KOSTYL,
        severity=PatternSeverity.MEDIUM,
        description="Вложенные try-except (костыль на костыле)",
        patterns=[r'try\s*:.*try\s*:'],
        message_template="Вложенные try-except — костыль в костыле!",
        suggestion="Рефакторите в отдельные функции.",
    ),
    
    CodePattern(
        name="except-pass-continue",
        category=PatternCategory.KOSTYL,
        severity=PatternSeverity.MEDIUM,
        description="except с pass или continue",
        patterns=[r'except[^:]*:\s*(pass|continue)\s*$'],
        message_template="except с {match} — молчаливое игнорирование ошибки.",
        suggestion="Хотя бы логируйте ошибки.",
    ),
    
    CodePattern(
        name="type-comparison-string",
        category=PatternCategory.KOSTYL,
        severity=PatternSeverity.MEDIUM,
        description="Сравнение типа через строку",
        patterns=[r'type\s*\(\s*\w+\s*\)\s*==\s*["\']\w+["\']'],
        message_template="Сравнение типа со строкой — костыль!",
        suggestion="Используйте isinstance() или type() == тип.",
    ),
    
    CodePattern(
        name="boolean-in-list",
        category=PatternCategory.KOSTYL,
        severity=PatternSeverity.LOW,
        description="True/False в списке/словаре",
        patterns=[r'\[[^\]]*\b(True|False)\b[^\]]*\]'],
        message_template="Булево значение в структуре данных.",
        suggestion="Это нормально, но проверьте логику.",
    ),
    
    CodePattern(
        name="sleep-in-production",
        category=PatternCategory.KOSTYL,
        severity=PatternSeverity.MEDIUM,
        description="time.sleep() в продакшен коде",
        patterns=[r'time\.sleep\s*\([^)]+\)'],
        message_template="time.sleep() в коде! Серьёзно?",
        suggestion="Используйте асинхронные альтернативы или перепроектируйте.",
    ),
    
    # ═══════════════════════════════════════════
    # НЕ-PYTHONIC
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="len-zero-check",
        category=PatternCategory.PYTHONIC,
        severity=PatternSeverity.LOW,
        description="Проверка len(x) == 0 вместо not x",
        patterns=[r'len\s*\(\s*\w+\s*\)\s*==\s*0'],
        message_template="len(x) == 0 вместо 'not x'.",
        suggestion="Используйте 'if not x:' (более pythonic).",
    ),
    
    CodePattern(
        name="for-range-len",
        category=PatternCategory.PYTHONIC,
        severity=PatternSeverity.LOW,
        description="for i in range(len(x)) вместо enumerate",
        patterns=[r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\('],
        message_template="range(len(x)) вместо enumerate().",
        suggestion="Используйте: for i, item in enumerate(x):",
    ),
    
    CodePattern(
        name="dict-keys-iteration",
        category=PatternCategory.PYTHONIC,
        severity=PatternSeverity.LOW,
        description="Итерация по dict.keys() в цикле",
        patterns=[r'for\s+\w+\s+in\s+\w+\.keys\s*\(\s*\)\s*:'],
        message_template=".keys() избыточен при итерации по словарю.",
        suggestion="Просто: for key in dict:",
    ),
    
    # ═══════════════════════════════════════════
    # СОВМЕСТИМОСТЬ
    # ═══════════════════════════════════════════
    
    CodePattern(
        name="python2-unicode",
        category=PatternCategory.COMPATIBILITY,
        severity=PatternSeverity.LOW,
        description="u'строка' (Python 2 синтаксис)",
        patterns=[r"u['\"]"],
        message_template="Python 2 unicode-префикс. В Python 3 не нужен.",
        suggestion="Удалите префикс 'u'.",
    ),
    
    CodePattern(
        name="platform-dependent-path",
        category=PatternCategory.COMPATIBILITY,
        severity=PatternSeverity.MEDIUM,
        description="Платформозависимый путь (обратные слеши)",
        patterns=[r'["\'][A-Za-z]:\\[^"\']+\\[^"\']+["\']'],
        message_template="Windows-путь в коде. Не работает на Linux/Mac.",
        suggestion="Используйте pathlib.Path или os.path.join().",
    ),
    
    CodePattern(
        name="encoding-not-specified",
        category=PatternCategory.COMPATIBILITY,
        severity=PatternSeverity.MEDIUM,
        description="open() без указания кодировки",
        patterns=[r'open\s*\([^)]*\)(?!.*encoding)'],
        message_template="open() без encoding= — может сломаться на Windows.",
        suggestion="Всегда указывайте encoding='utf-8'.",
    ),
]

# ═══════════════════════════════════════════════════════════════
# РЕЕСТР ПАТТЕРНОВ
# ═══════════════════════════════════════════════════════════════

class PatternRegistry:
    """Управляет всеми паттернами."""
    
    def __init__(self):
        self._patterns: Dict[str, CodePattern] = {}
        self._by_category: Dict[PatternCategory, List[CodePattern]] = {}
        self._by_severity: Dict[PatternSeverity, List[CodePattern]] = {}
        
        # Загружаем встроенные паттерны
        for pattern in BUILTIN_PATTERNS:
            self.register(pattern)
    
    def register(self, pattern: CodePattern):
        """Регистрирует паттерн."""
        self._patterns[pattern.name] = pattern
        
        if pattern.category not in self._by_category:
            self._by_category[pattern.category] = []
        self._by_category[pattern.category].append(pattern)
        
        if pattern.severity not in self._by_severity:
            self._by_severity[pattern.severity] = []
        self._by_severity[pattern.severity].append(pattern)
    
    def get(self, name: str) -> Optional[CodePattern]:
        return self._patterns.get(name)
    
    def get_all(self) -> List[CodePattern]:
        return list(self._patterns.values())
    
    def get_by_category(self, category: PatternCategory) -> List[CodePattern]:
        return self._by_category.get(category, [])
    
    def get_by_severity(self, severity: PatternSeverity) -> List[CodePattern]:
        return self._by_severity.get(severity, [])
    
    def scan_line(self, line: str, line_num: int) -> List[PatternMatch]:
        """Сканирует одну строку всеми паттернами."""
        matches = []
        for pattern in self._patterns.values():
            try:
                line_matches = pattern.check_line(line, line_num)
                matches.extend(line_matches)
            except Exception:
                pass  # Паттерн сломался — игнорируем
        return matches
    
    def scan_code(self, source: str, file_path: str = "") -> List[PatternMatch]:
        """Сканирует весь код."""
        all_matches = []
        
        for line_num, line in enumerate(source.split('\n'), 1):
            matches = self.scan_line(line, line_num)
            for match in matches:
                match.file_path = file_path
            all_matches.extend(matches)
        
        return all_matches
    
    def scan_file(self, filepath: str) -> List[PatternMatch]:
        """Сканирует файл."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            return self.scan_code(source, filepath)
        except Exception as e:
            return [PatternMatch(
                pattern_name="scan-error",
                category=PatternCategory.ERROR_PRONE,
                severity=PatternSeverity.HIGH,
                line_number=0,
                column=0,
                matched_text="",
                message=f"Не удалось просканировать файл: {e}",
                file_path=filepath,
            )]
    
    def stats(self) -> Dict:
        """Статистика паттернов."""
        return {
            'total_patterns': len(self._patterns),
            'categories': {
                cat.value[1]: len(patterns)
                for cat, patterns in self._by_category.items()
            },
            'severities': {
                sev.value[2]: len(patterns)
                for sev, patterns in self._by_severity.items()
            },
        }
    
    def report(self) -> str:
        """Отчёт о паттернах."""
        s = self.stats()
        report = f"""
{Emoji.BUG} ═══════════════════════════════════════
{Emoji.BUG} KOSTYLPY PATTERN SCANNER
{Emoji.BUG} ═══════════════════════════════════════

Всего паттернов: {s['total_patterns']}

Категории:
"""
        for cat, count in s['categories'].items():
            report += f"  {cat}: {count}\n"
        
        report += f"\nСерьёзность:\n"
        for sev, count in s['severities'].items():
            report += f"  {sev}: {count}\n"
        
        report += f"\n{Emoji.BUG} ═══════════════════════════════════════"
        return report

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ РЕЕСТР
# ═══════════════════════════════════════════════════════════════

patterns = PatternRegistry()

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def scan_code(source: str, file_path: str = "") -> List[PatternMatch]:
    """Быстрое сканирование кода."""
    return patterns.scan_code(source, file_path)

def scan_file(filepath: str) -> List[PatternMatch]:
    """Быстрое сканирование файла."""
    return patterns.scan_file(filepath)

def apply_fixes(source: str, matches: List[PatternMatch], auto_apply: bool = False) -> str:
    """Применяет исправления к исходному коду."""
    if not auto_apply:
        return source
    
    lines = source.split('\n')
    fixes_by_line: Dict[int, List[PatternMatch]] = {}
    
    for match in matches:
        if match.auto_fix:
            if match.line_number not in fixes_by_line:
                fixes_by_line[match.line_number] = []
            fixes_by_line[match.line_number].append(match)
    
    # Применяем исправления (с конца, чтобы не сбить нумерацию)
    for line_num in sorted(fixes_by_line.keys(), reverse=True):
        if line_num <= len(lines):
            line = lines[line_num - 1]
            for match in fixes_by_line[line_num]:
                if match.auto_fix:
                    # Простая замена первого совпадения
                    line = line.replace(match.matched_text, match.auto_fix, 1)
            lines[line_num - 1] = line
    
    return '\n'.join(lines)

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основное
    'PatternRegistry',
    'patterns',  # Глобальный реестр
    
    # Классы
    'CodePattern',
    'PatternMatch',
    'PatternCategory',
    'PatternSeverity',
    
    # Встроенные паттерны
    'BUILTIN_PATTERNS',
    
    # Функции
    'scan_code',
    'scan_file',
    'apply_fixes',
]

print(f"{Emoji.BUG} kostylpy.patterns: загружено {len(BUILTIN_PATTERNS)} паттернов")
print(f"   Категорий: {len(PatternCategory)}")
print(f"   Уровней серьёзности: {len(PatternSeverity)}")