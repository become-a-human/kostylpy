"""
Константы kostylpy.
Все магические числа, строки и прочая ерунда, которую нельзя размазывать по коду.
Собраны в одном месте чтобы никто не нашёл.

Содержит:
- Версии и метаданные
- Статусы и коды
- Пороговые значения
- Маппинги и справочники
- Эмодзи (очень важные)
- Настройки по умолчанию
- Константы для всех подсистем
- Запасные значения
- Магические числа
"""

import sys
import os
import platform
from enum import Enum, auto

# ═══════════════════════════════════════════════════════════════
# ВЕРСИИ И МЕТАДАННЫЕ
# ═══════════════════════════════════════════════════════════════

KOSTYLPY_VERSION = "3.0.0-beta-kostyl"
KOSTYLPY_CODENAME = "Великий Костыль"
KOSTYLPY_BUILD = 9001  # It's over 9000!
KOSTYLPY_RELEASE_DATE = "2024-01-01"  # Никогда не обновлялась
KOSTYLPY_AUTHOR = "Коллектив костылестроителей им. В.Е.Лосипедова"
KOSTYLPY_LICENSE = "WTFPL + Kostyl Clause"
KOSTYLPY_WEBSITE = "http://localhost:8080/kostylpy"  # Локальный сайт
KOSTYLPY_EMAIL = "kostyl@crutch.enterprise"
KOSTYLPY_SLOGAN = "Работает — не трогай"
KOSTYLPY_MOTTO = "Если работает — добавь ещё костылей"

# ═══════════════════════════════════════════════════════════════
# ПОРОГОВЫЕ ЗНАЧЕНИЯ
# ═══════════════════════════════════════════════════════════════

# Паника
PANIC_THRESHOLD = 42  # После скольких костылей начинается паника
PANIC_COOLDOWN = 10.0  # Секунд между паниками
MAX_CRUTCHES_BEFORE_CRASH = 999  # Теоретический предел
MAX_COFFEE_BREAKS = 5  # Максимум кофе-брейков

# Ретраи
DEFAULT_RETRY_COUNT = 3  # Стандартное количество попыток
DEFAULT_RETRY_DELAY = 0.1  # Стандартная задержка
MAX_RETRY_COUNT = 100  # Абсолютный максимум попыток
EXPONENTIAL_BACKOFF_BASE = 2.0  # База для экспоненциальной задержки

# Таймауты
DEFAULT_TIMEOUT = 30.0  # Стандартный таймаут
CONNECTION_TIMEOUT = 10.0  # Таймаут соединения
READ_TIMEOUT = 30.0  # Таймаут чтения
WRITE_TIMEOUT = 30.0  # Таймаут записи
MAX_TIMEOUT = 3600.0  # Час — максимум

# Размеры
DEFAULT_BUFFER_SIZE = 8192  # Стандартный размер буфера
MAX_STRING_LENGTH = 1_000_000  # Максимальная длина строки
MAX_LIST_SIZE = 10_000  # Максимальный размер списка
MAX_DICT_SIZE = 10_000  # Максимальный размер словаря
MAX_FILE_SIZE_MB = 100  # Максимальный размер файла в МБ

# Логирование
MAX_LOG_SIZE = 10_000  # Максимальное количество записей в логе
LOG_ROTATION_COUNT = 5  # Количество файлов ротации
LOG_TRUNCATE_LENGTH = 500  # Обрезать сообщения длиннее этого

# ═══════════════════════════════════════════════════════════════
# КОДЫ И СТАТУСЫ
# ═══════════════════════════════════════════════════════════════

class ExitCodes(Enum):
    """Коды выхода программы."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    KOSTYL_OVERFLOW = 42
    COFFEE_DEPLETED = 43
    TOO_MANY_CRUTCHES = 100
    CRUTCH_BROKEN = 101
    PANIC_MODE = 200
    APOCALYPSE = 255

class StatusCodes(Enum):
    """Статусные коды операций."""
    OK = "ok"
    ERROR = "error"
    WARNING = "warning"
    CRITICAL = "critical"
    KOSTYL = "kostyl"  # Особый статус
    PENDING = "pending"
    UNKNOWN = "unknown"

# ═══════════════════════════════════════════════════════════════
# ЭМОДЗИ (КРИТИЧЕСКИ ВАЖНЫЕ)
# ═══════════════════════════════════════════════════════════════

class Emoji:
    """Эмодзи для всех случаев жизни."""
    # Основные
    KOSTYL = "🦿"
    CRUTCH = "🔧"
    MONKEY = "🐒"
    MONKEY_SEE = "🙈"
    MONKEY_DO = "🙉"
    MONKEY_SCREAM = "🙊"
    
    # Статусы
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    DEBUG = "🐛"
    CRITICAL = "💀"
    NUCLEAR = "☢️"
    APOCALYPSE = "🔥"
    HEAT_DEATH = "❄️"
    
    # Действия
    LOADING = "⏳"
    WORKING = "⚙️"
    SLEEPING = "😴"
    COFFEE = "☕"
    COFFEE_BREAK = "☕🔧"
    PARTY = "🎉"
    FIX = "🩹"
    BANDAGE = "🩹"
    
    # Объекты
    FILE = "📄"
    FOLDER = "📁"
    CHART = "📊"
    DATABASE = "🗄️"
    NETWORK = "🌐"
    LOCK = "🔒"
    KEY = "🔑"
    BUG = "🐛"
    FEATURE = "✨"
    
    # Люди
    DEVELOPER = "👨‍💻"
    DEVELOPER_FEMALE = "👩‍💻"
    DEBUGGER = "🔍"
    TESTER = "🧪"
    MANAGER = "👔"
    USER = "🧑"
    
    # Погода (для логов)
    SUN = "☀️"
    RAIN = "🌧️"
    STORM = "⛈️"
    TORNADO = "🌪️"
    
    # Специальные
    MAGIC = "🪄"
    CRYSTAL_BALL = "🔮"
    UNICORN = "🦄"
    RAINBOW = "🌈"
    POOP = "💩"
    CLOWN = "🤡"
    
    @classmethod
    def random(cls) -> str:
        """Случайный эмодзи (потому что почему бы и нет)."""
        import random
        all_emoji = [
            v for k, v in cls.__dict__.items()
            if not k.startswith('_') and isinstance(v, str) and len(v) == 1
        ]
        return random.choice(all_emoji) if all_emoji else "❓"

# ═══════════════════════════════════════════════════════════════
# ЦВЕТА ДЛЯ ТЕРМИНАЛА
# ═══════════════════════════════════════════════════════════════

class Colors:
    """ANSI цвета для терминала."""
    # Базовые
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Цвета текста
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Яркие цвета
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Фоны
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Оборачивает текст в цвет."""
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def red(cls, text: str) -> str:
        return cls.colorize(text, cls.RED)
    
    @classmethod
    def green(cls, text: str) -> str:
        return cls.colorize(text, cls.GREEN)
    
    @classmethod
    def yellow(cls, text: str) -> str:
        return cls.colorize(text, cls.YELLOW)
    
    @classmethod
    def blue(cls, text: str) -> str:
        return cls.colorize(text, cls.BLUE)
    
    @classmethod
    def bold(cls, text: str) -> str:
        return cls.colorize(text, cls.BOLD)

# ═══════════════════════════════════════════════════════════════
# МАППИНГИ И СПРАВОЧНИКИ
# ═══════════════════════════════════════════════════════════════

# Замены модулей
FALLBACK_MODULES = {
    'numpy': 'math',
    'pandas': 'csv',
    'matplotlib': 'webbrowser',
    'requests': 'urllib.request',
    'flask': 'http.server',
    'django': 'http.server',
    'sqlalchemy': 'sqlite3',
    'redis': 'pickle',
    'celery': 'threading',
    'tensorflow': 'random',
    'torch': 'random',
    'sklearn': 'statistics',
    'beautifulsoup4': 'html.parser',
    'lxml': 'xml.etree.ElementTree',
    'pillow': 'tkinter',
}

# HTTP статусы с костыльными названиями
HTTP_STATUS_KOSTYL = {
    200: "Всё ок, но это не точно",
    301: "Переехали на костылях",
    404: "Не найдено (даже костыли не помогли)",
    418: "Я — заварочный костыль",
    500: "Сервер упал, но мы его подняли костылями",
    502: "Плохой шлюз (надо починить костылём)",
    503: "Сервис на костылях, подождите",
}

# Типы ошибок и их серьёзность
ERROR_SEVERITY_MAP = {
    'ValueError': 'MODERATE',
    'TypeError': 'MODERATE',
    'KeyError': 'MINOR',
    'IndexError': 'MINOR',
    'AttributeError': 'MINOR',
    'FileNotFoundError': 'MAJOR',
    'ImportError': 'MAJOR',
    'MemoryError': 'NUCLEAR',
    'RecursionError': 'NUCLEAR',
    'SystemError': 'APOCALYPTIC',
}

# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКИ ПО УМОЛЧАНИЮ
# ═══════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    # Основные настройки
    'debug': False,
    'verbose': False,
    'log_level': 'INFO',
    'panic_threshold': PANIC_THRESHOLD,
    'coffee_required': True,
    
    # Модули
    'modules': {
        'interceptors': True,
        'validators': True,
        'monkey_patcher': True,
        'async_kostyl': True,
        'factories': True,
    },
    
    # Кеширование
    'cache': {
        'enabled': False,
        'max_size': 1000,
        'ttl': 3600,
    },
    
    # Логирование
    'logging': {
        'enabled': True,
        'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        'file': 'kostylpy.log',
        'max_size_mb': 10,
        'backup_count': 3,
    },
    
    # Сеть
    'network': {
        'default_timeout': DEFAULT_TIMEOUT,
        'retry_count': DEFAULT_RETRY_COUNT,
        'user_agent': f'kostylpy/{KOSTYLPY_VERSION}',
    },
    
    # Безопасность
    'security': {
        'block_dangerous_calls': True,
        'sanitize_input': True,
        'hash_passwords': True,
    },
}

# ═══════════════════════════════════════════════════════════════
# ШАБЛОНЫ И ФОРМАТЫ
# ═══════════════════════════════════════════════════════════════

# Формат даты и времени
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Регулярные выражения
REGEX_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'url': r'^https?://[^\s<>"]+|www\.[^\s<>"]+$',
    'phone': r'^\+?[\d\s\-\(\)]{7,}$',
    'ip': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    'hex_color': r'^#[0-9a-fA-F]{6}$',
}

# ═══════════════════════════════════════════════════════════════
# МАГИЧЕСКИЕ ЧИСЛА
# ═══════════════════════════════════════════════════════════════

# Почему эти числа здесь? Потому что.
MAGIC_NUMBER = 42  # Ответ на главный вопрос жизни, вселенной и всего такого
PI_APPROX = 3.14  # Примерно
E_APPROX = 2.71  # Тоже примерно
GOLDEN_RATIO = 1.618  # Золотое сечение

# Случайные константы (почему бы и нет)
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24
DAYS_IN_WEEK = 7
WEEKS_IN_YEAR = 52.1429  # Примерно
SECONDS_IN_YEAR = 31536000

BYTES_IN_KB = 1024
BYTES_IN_MB = 1048576
BYTES_IN_GB = 1073741824

# ═══════════════════════════════════════════════════════════════
# ЗАПАСНЫЕ ЗНАЧЕНИЯ
# ═══════════════════════════════════════════════════════════════

FALLBACK_VALUES = {
    'string': "",
    'int': 0,
    'float': 0.0,
    'bool': False,
    'list': [],
    'dict': {},
    'set': set(),
    'tuple': (),
    'none': None,
    'function': lambda *args, **kwargs: None,
    'class': type('FallbackClass', (), {}),
}

# Дефолтные ответы API
DEFAULT_RESPONSES = {
    'success': {'status': 'ok', 'message': 'Всё работает на костылях'},
    'error': {'status': 'error', 'message': 'Всё сломалось, но мы держимся'},
    'not_found': {'status': 'error', 'message': 'Не найдено, поищите ещё'},
}

# ═══════════════════════════════════════════════════════════════
# СИСТЕМНАЯ ИНФОРМАЦИЯ
# ═══════════════════════════════════════════════════════════════

SYSTEM_INFO = {
    'python_version': sys.version,
    'python_implementation': platform.python_implementation(),
    'platform': platform.platform(),
    'system': platform.system(),
    'machine': platform.machine(),
    'processor': platform.processor(),
    'hostname': platform.node(),
    'kostylpy_version': KOSTYLPY_VERSION,
}

# ═══════════════════════════════════════════════════════════════
# ПРЕДЕЛЫ И ОГРАНИЧЕНИЯ
# ═══════════════════════════════════════════════════════════════

class Limits:
    """Пределы допустимого."""
    MAX_INT = sys.maxsize
    MIN_INT = -sys.maxsize - 1
    MAX_FLOAT = float('inf')
    MIN_FLOAT = float('-inf')
    MAX_STRING = 1_000_000_000  # Гигабайт строки?
    MAX_RECURSION = sys.getrecursionlimit()
    MAX_THREADS = 1000
    MAX_OPEN_FILES = 1024
    MAX_CONNECTIONS = 1000
    
    @classmethod
    def check_int(cls, value: int) -> bool:
        return cls.MIN_INT <= value <= cls.MAX_INT
    
    @classmethod
    def check_float(cls, value: float) -> bool:
        return cls.MIN_FLOAT <= value <= cls.MAX_FLOAT

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ-КОНСТАНТЫ (ЗВУЧИТ КАК ОКСЮМОРОН)
# ═══════════════════════════════════════════════════════════════

def get_kostylpy_banner() -> str:
    """Возвращает баннер kostylpy."""
    return f"""
    ╔══════════════════════════════════════════╗
    ║  🦿 KOSTYLPY v{KOSTYLPY_VERSION}              ║
    ║  "{KOSTYLPY_SLOGAN}"           ║
    ║  {KOSTYLPY_MOTTO}  ║
    ╚══════════════════════════════════════════╝
    """

def get_kostylpy_help() -> str:
    """Возвращает справку."""
    return f"""
    {Emoji.KOSTYL} Kostylpy — библиотека костылей для Python
    Версия: {KOSTYLPY_VERSION}
    
    Использование:
        import kostylpy  # Всё, теперь ваш код под защитой
        
    Основные возможности:
        - Безопасный print (никогда не падает)
        - Безопасный open (создаёт файлы при отсутствии)
        - Безопасный import (заменяет модули заглушками)
        - Декораторы (safe, retry, fallback)
        - Валидаторы (проверка всего)
        - Фабрики (создание костылей)
        - Перехватчики (шпионаж за кодом)
        
    Документация: нет (читайте исходники)
    Поддержка: {KOSTYLPY_EMAIL}
    """

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Версии
    'KOSTYLPY_VERSION', 'KOSTYLPY_CODENAME', 'KOSTYLPY_BUILD',
    
    # Пороги
    'PANIC_THRESHOLD', 'DEFAULT_RETRY_COUNT', 'DEFAULT_TIMEOUT',
    
    # Классы
    'ExitCodes', 'StatusCodes', 'Emoji', 'Colors', 'Limits',
    
    # Маппинги
    'FALLBACK_MODULES', 'HTTP_STATUS_KOSTYL', 'ERROR_SEVERITY_MAP',
    
    # Конфиги
    'DEFAULT_CONFIG',
    
    # Шаблоны
    'DATE_FORMAT', 'TIME_FORMAT', 'DATETIME_FORMAT',
    
    # Магические числа
    'MAGIC_NUMBER', 'BYTES_IN_MB',
    
    # Запасные значения
    'FALLBACK_VALUES',
    
    # Системная информация
    'SYSTEM_INFO',
    
    # Функции
    'get_kostylpy_banner', 'get_kostylpy_help',
]

print(f"📋 kostylpy.constants: загружено {len(__all__)} констант и классов")
print(f"   Версия: {KOSTYLPY_VERSION}")
print(f"   Код: {KOSTYLPY_BUILD}")