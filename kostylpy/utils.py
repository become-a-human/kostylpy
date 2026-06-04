"""
Утилиты kostylpy.
Всякая всячина, которая не влезла в другие модули.
Здесь собраны самые бесполезные и одновременно необходимые функции.

Содержит:
- Строковые утилиты (костыльный парсинг, нормализация)
- Числовые утилиты (безопасная математика)
- Утилиты для коллекций (словари, списки с костылями)
- Временные утилиты (костыльное время)
- Сетевые утилиты (пинг до луны)
- Файловые утилиты (поиск, хеширование)
- Утилиты для отладки (костыльный дебаггер)
- Случайные утилиты (генераторы всего)
- Мета-утилиты (утилиты для утилит)
- Функции-помощники (которые никто не просил)
"""

import sys
import os
import re
import time
import json
import random
import hashlib
import base64
import string
import math
import threading
import functools
import inspect
import traceback
import tempfile
import pathlib
import platform
import socket
import uuid
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Set, Iterator
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict, Counter
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем состояние
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    class _FakeSeverity(Enum):
        COSMETIC = "COSMETIC"
        MINOR = "MINOR"
        MODERATE = "MODERATE"
        MAJOR = "MAJOR"
        CRITICAL = "CRITICAL"
    
    class _FakeCategory(Enum):
        UTILS = "utils"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# СТРОКОВЫЕ УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def safe_str(obj: Any, max_length: int = 1000, default: str = "<неизвестно>") -> str:
    """
    Преобразует ЛЮБОЙ объект в строку. Никогда не падает.
    Даже если объект — это сингулярность.
    """
    try:
        if obj is None:
            return "None"
        
        if isinstance(obj, (str, int, float, bool)):
            result = str(obj)
        elif isinstance(obj, bytes):
            try:
                result = obj.decode('utf-8')
            except:
                result = obj.hex()[:max_length]
        elif isinstance(obj, (list, tuple, set)):
            items = [safe_str(i, max_length // max(1, len(obj))) for i in obj]
            result = f"[{', '.join(items[:10])}]"
            if len(items) > 10:
                result += f"... (+{len(items) - 10})"
        elif isinstance(obj, dict):
            items = [
                f"{safe_str(k, 50)}: {safe_str(v, 50)}"
                for k, v in list(obj.items())[:5]
            ]
            result = f"{{{', '.join(items)}}}"
            if len(obj) > 5:
                result += f"... (+{len(obj) - 5})"
        elif hasattr(obj, '__str__'):
            result = str(obj)
        else:
            result = repr(obj)
        
        if len(result) > max_length:
            result = result[:max_length - 3] + "..."
        
        return result
    
    except Exception as e:
        return f"{default} (ошибка: {e})"

def truncate(text: str, length: int = 80, suffix: str = "...", word_boundary: bool = True) -> str:
    """
    Обрезает строку до заданной длины.
    С уважением к словам (если нужно).
    """
    if not text or len(text) <= length:
        return text
    
    truncated = text[:length - len(suffix)]
    
    if word_boundary:
        # Ищем последний пробел
        last_space = truncated.rfind(' ')
        if last_space > length // 2:
            truncated = truncated[:last_space]
    
    return truncated + suffix

def slugify(text: str, separator: str = "-", max_length: int = 100) -> str:
    """
    Преобразует строку в URL-совместимый slug.
    "Привет, Мир!" → "privet-mir"
    """
    if not text:
        return ""
    
    # Транслитерация (очень примерная)
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    
    text = text.lower()
    for cyr, lat in translit.items():
        text = text.replace(cyr, lat)
    
    # Убираем всё лишнее
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', separator, text)
    text = re.sub(f'{separator}+', separator, text)
    text = text.strip(separator)
    
    return text[:max_length]

def extract_numbers(text: str) -> List[float]:
    """Извлекает все числа из строки."""
    pattern = r'[-+]?\d*\.?\d+'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]

def extract_emails(text: str) -> List[str]:
    """Извлекает email адреса из строки."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def extract_urls(text: str) -> List[str]:
    """Извлекает URL из строки."""
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(pattern, text)

def obfuscate(text: str, visible_chars: int = 4, char: str = "*") -> str:
    """
    Скрывает часть строки.
    "password123" → "pass********"
    """
    if len(text) <= visible_chars:
        return char * len(text)
    return text[:visible_chars] + char * (len(text) - visible_chars)

def random_string(length: int = 10, chars: str = string.ascii_letters + string.digits) -> str:
    """Генерирует случайную строку."""
    return ''.join(random.choice(chars) for _ in range(length))

def is_palindrome(text: str) -> bool:
    """Проверяет, является ли строка палиндромом."""
    cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9]', '', text.lower())
    return cleaned == cleaned[::-1]

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Расстояние Левенштейна между двумя строками.
    Сколько символов нужно изменить, чтобы из s1 получить s2.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# ═══════════════════════════════════════════════════════════════
# ЧИСЛОВЫЕ УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def safe_int(value: Any, default: int = 0) -> int:
    """Безопасное преобразование в int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Безопасное преобразование в float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Ограничивает значение диапазоном."""
    return max(min_val, min(max_val, value))

def safe_divide(a: Union[int, float], b: Union[int, float], default: Union[int, float] = 0.0) -> Union[int, float]:
    """
    Безопасное деление.
    При делении на ноль возвращает default.
    """
    try:
        return a / b
    except ZeroDivisionError:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Деление на ноль: {a} / {b}, возвращён {default}"
        )
        return default

def safe_percentage(part: Union[int, float], total: Union[int, float], default: float = 0.0) -> float:
    """Безопасное вычисление процента."""
    if total == 0:
        return default
    return (part / total) * 100

def round_to(value: float, decimals: int = 2, strategy: str = "round") -> float:
    """
    Округление с разными стратегиями.
    Стратегии: round, floor, ceil, trunc.
    """
    strategies = {
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'trunc': math.trunc,
    }
    func = strategies.get(strategy, round)
    
    if strategy == 'round':
        return round(value, decimals)
    else:
        multiplier = 10 ** decimals
        return func(value * multiplier) / multiplier

def human_readable_size(bytes_count: int, suffix: str = "Б") -> str:
    """
    Преобразует байты в человекочитаемый формат.
    1024 → "1.0 КБ"
    """
    for unit in ['', 'К', 'М', 'Г', 'Т', 'П', 'Э']:
        if abs(bytes_count) < 1024.0:
            return f"{bytes_count:.1f} {unit}{suffix}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} ??{suffix}"

def human_readable_number(num: Union[int, float]) -> str:
    """
    Преобразует число в человекочитаемый формат.
    1234567 → "1.23M"
    """
    if num < 1000:
        return str(num)
    
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000.0:
            return f"{num:.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}???"

def is_prime(n: int) -> bool:
    """Проверяет, является ли число простым."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n: int) -> int:
    """Возвращает n-е число Фибоначчи."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ ДЛЯ КОЛЛЕКЦИЙ
# ═══════════════════════════════════════════════════════════════

def safe_get(
    data: Union[Dict, List],
    key: Any,
    default: Any = None,
    separator: str = "."
) -> Any:
    """
    Безопасно получает значение из вложенной структуры.
    Поддерживает точечную нотацию: "user.address.city"
    """
    if not data:
        return default
    
    if isinstance(key, str) and separator in key:
        keys = key.split(separator)
    elif isinstance(key, (list, tuple)):
        keys = key
    else:
        keys = [key]
    
    current = data
    for k in keys:
        try:
            if isinstance(current, dict):
                current = current.get(k)
                if current is None:
                    return default
            elif isinstance(current, (list, tuple)):
                k = int(k)
                current = current[k]
            else:
                return default
        except (KeyError, IndexError, TypeError, ValueError):
            return default
    
    return current

def safe_set(
    data: Dict,
    key: Any,
    value: Any,
    separator: str = ".",
    create_missing: bool = True
) -> Dict:
    """
    Безопасно устанавливает значение во вложенной структуре.
    """
    if isinstance(key, str) and separator in key:
        keys = key.split(separator)
    elif isinstance(key, (list, tuple)):
        keys = key
    else:
        keys = [key]
    
    current = data
    for i, k in enumerate(keys[:-1]):
        if k not in current:
            if create_missing:
                current[k] = {}
            else:
                return data
        current = current[k]
    
    current[keys[-1]] = value
    return data

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Глубоко объединяет два словаря.
    Значения из dict2 перезаписывают dict1.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict, parent_key: str = "", separator: str = ".") -> Dict:
    """
    Преобразует вложенный словарь в плоский.
    {'a': {'b': 1}} → {'a.b': 1}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d: Dict, separator: str = ".") -> Dict:
    """
    Преобразует плоский словарь во вложенный.
    {'a.b': 1} → {'a': {'b': 1}}
    """
    result = {}
    for key, value in d.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Разбивает список на части заданного размера."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def unique_list(lst: List, preserve_order: bool = True) -> List:
    """
    Удаляет дубликаты из списка.
    Сохраняет порядок если preserve_order=True.
    """
    if preserve_order:
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    return list(set(lst))

def group_by(lst: List, key_func: Callable) -> Dict:
    """Группирует элементы списка по ключу."""
    result = defaultdict(list)
    for item in lst:
        key = key_func(item)
        result[key].append(item)
    return dict(result)

def sort_by_multiple_keys(lst: List, keys: List[Tuple[str, bool]]) -> List:
    """
    Сортирует список словарей по нескольким ключам.
    keys: [('name', True), ('age', False)] — True = asc, False = desc
    """
    def sort_func(item):
        result = []
        for key, ascending in keys:
            value = item.get(key, "")
            # Инвертируем для desc
            if not ascending:
                if isinstance(value, str):
                    value = tuple(-ord(c) for c in value)
                elif isinstance(value, (int, float)):
                    value = -value
            result.append(value)
        return tuple(result)
    
    return sorted(lst, key=sort_func)

class DotDict(dict):
    """
    Словарь с доступом через точку.
    d = DotDict({'a': 1})
    d.a  # 1
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict) and not isinstance(value, DotDict):
                self[key] = DotDict(value)
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'DotDict' не имеет атрибута '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'DotDict' не имеет атрибута '{key}'")

class SafeList(list):
    """
    Список, который никогда не падает при доступе по индексу.
    При выходе за границы возвращает None или default.
    """
    def __init__(self, *args, default: Any = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default
    
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            return self.default
    
    def __setitem__(self, index, value):
        # Расширяем список если нужно
        if index >= len(self):
            self.extend([self.default] * (index - len(self) + 1))
        super().__setitem__(index, value)

# ═══════════════════════════════════════════════════════════════
# ВРЕМЕННЫЕ УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def timestamp_ms() -> int:
    """Текущее время в миллисекундах."""
    return int(time.time() * 1000)

def timestamp_iso() -> str:
    """Текущее время в ISO формате."""
    return datetime.now().isoformat()

def time_ago(seconds: float) -> str:
    """
    Преобразует количество секунд в человекочитаемый формат.
    3661 → "1 час 1 минута 1 секунда назад"
    """
    if seconds < 0:
        return "в будущем (костыль времени?)"
    
    intervals = [
        ("год", 31536000),
        ("месяц", 2592000),
        ("неделя", 604800),
        ("день", 86400),
        ("час", 3600),
        ("минута", 60),
        ("секунда", 1),
    ]
    
    for name, count in intervals:
        value = seconds // count
        if value >= 1:
            # Склоняем
            if name == "месяц":
                if 2 <= value <= 4:
                    name = "месяца"
                elif value >= 5:
                    name = "месяцев"
            elif name in ("час", "день", "год"):
                if 2 <= value <= 4:
                    name += "а"
                elif value >= 5:
                    name += "ов"
            elif name in ("минута", "секунда", "неделя"):
                if 2 <= value <= 4:
                    name = name[:-1] + "ы" if name[-1] == "а" else name + "и"
                elif value >= 5:
                    name = name[:-1] + "" if name[-1] == "а" else name
            
            return f"{int(value)} {name} назад"
    
    return "только что"

def sleep_random(min_sec: float = 0.1, max_sec: float = 1.0):
    """Спит случайное время."""
    time.sleep(random.uniform(min_sec, max_sec))

def measure_time(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.UTILS,
            f"⏱️ {func.__name__}: {elapsed:.4f}с"
        )
        
        return result
    return wrapper

# ═══════════════════════════════════════════════════════════════
# ФАЙЛОВЫЕ УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def safe_read_file(filepath: str, default: str = "", encoding: str = "utf-8") -> str:
    """Безопасно читает файл. При ошибке возвращает default."""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Не удалось прочитать файл '{filepath}': {e}"
        )
        return default

def safe_write_file(filepath: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> bool:
    """Безопасно записывает файл. При ошибке возвращает False."""
    try:
        if create_dirs:
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.UTILS,
            f"Не удалось записать файл '{filepath}': {e}"
        )
        return False

def file_hash(filepath: str, algorithm: str = "sha256") -> Optional[str]:
    """Вычисляет хеш файла."""
    try:
        h = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Не удалось вычислить хеш '{filepath}': {e}"
        )
        return None

def find_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = True,
    max_depth: int = 10
) -> List[str]:
    """
    Ищет файлы по паттерну.
    """
    import fnmatch
    results = []
    
    try:
        for root, dirs, files in os.walk(directory):
            depth = root[len(directory):].count(os.sep)
            if depth > max_depth:
                del dirs[:]
                continue
            
            for filename in fnmatch.filter(files, pattern):
                results.append(os.path.join(root, filename))
            
            if not recursive:
                break
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Ошибка поиска файлов в '{directory}': {e}"
        )
    
    return results

def temp_file(suffix: str = ".tmp", content: str = "") -> str:
    """Создаёт временный файл и возвращает путь."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path

def ensure_dir(dirpath: str) -> bool:
    """Создаёт директорию если её нет."""
    try:
        os.makedirs(dirpath, exist_ok=True)
        return True
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Не удалось создать директорию '{dirpath}': {e}"
        )
        return False

# ═══════════════════════════════════════════════════════════════
# СЕТЕВЫЕ УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Проверяет, открыт ли порт."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_local_ip() -> str:
    """Получает локальный IP адрес."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def simple_http_get(url: str, timeout: float = 5.0) -> Optional[str]:
    """Простой HTTP GET запрос (без requests)."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"HTTP GET не удался для '{url}': {e}"
        )
        return None

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ ДЛЯ ОТЛАДКИ
# ═══════════════════════════════════════════════════════════════

def debug_print(*args, **kwargs):
    """
    Отладочный print с информацией о месте вызова.
    """
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    func_name = frame.f_code.co_name
    
    prefix = f"[DEBUG] {os.path.basename(filename)}:{lineno} {func_name}() →"
    print(prefix, *args, **kwargs)

def dump_var(var: Any, name: str = "переменная", max_depth: int = 3) -> str:
    """
    Дамп переменной с информацией о типе и значении.
    """
    def _dump(v, depth=0, prefix=""):
        if depth > max_depth:
            return f"{prefix}... (макс глубина)\n"
        
        result = ""
        vtype = type(v).__name__
        
        if isinstance(v, dict):
            result += f"{prefix}{name}: <{vtype}> ({len(v)} элементов)\n"
            for k, val in list(v.items())[:5]:
                result += _dump(val, depth + 1, prefix + f"  [{repr(k)}] ")
        elif isinstance(v, (list, tuple, set)):
            result += f"{prefix}{name}: <{vtype}> ({len(v)} элементов)\n"
            for i, val in enumerate(list(v)[:5]):
                result += _dump(val, depth + 1, prefix + f"  [{i}] ")
        else:
            result += f"{prefix}{name}: <{vtype}> = {repr(v)[:200]}\n"
        
        return result
    
    return _dump(var)

def get_caller_info() -> Dict[str, Any]:
    """
    Получает информацию о том, кто вызвал функцию.
    """
    frame = inspect.currentframe()
    # Пропускаем текущий фрейм и фрейм вызывающей функции
    caller = frame.f_back.f_back if frame.f_back else frame
    
    return {
        'file': caller.f_code.co_filename,
        'line': caller.f_lineno,
        'function': caller.f_code.co_name,
        'code': inspect.getframeinfo(caller).code_context,
    }

# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАТОРЫ СЛУЧАЙНЫХ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def random_name(gender: str = "random") -> str:
    """Генерирует случайное имя."""
    male_names = ["Александр", "Михаил", "Дмитрий", "Сергей", "Андрей",
                  "Костыль", "Баг", "Фикс", "Хотфикс", "Деплой"]
    female_names = ["Анна", "Мария", "Елена", "Ольга", "Наталья",
                    "Библиотека", "Функция", "Переменная", "Константа", "Зависимость"]
    
    if gender == "male":
        return random.choice(male_names)
    elif gender == "female":
        return random.choice(female_names)
    else:
        return random.choice(male_names + female_names)

def random_email(domain: str = "kostylpy.dev") -> str:
    """Генерирует случайный email."""
    name = random_string(random.randint(5, 10), string.ascii_lowercase)
    return f"{name}@{domain}"

def random_phone() -> str:
    """Генерирует случайный номер телефона."""
    return f"+7 ({random.randint(900, 999)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"

def random_date(start_year: int = 2000, end_year: int = 2025) -> str:
    """Генерирует случайную дату."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def random_ip() -> str:
    """Генерирует случайный IP адрес."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def random_user_agent() -> str:
    """Генерирует случайный User-Agent."""
    browsers = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/16.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0",
        "KostylBrowser/3.0 (Костыльная ОС; Костыльный Процессор) KostylEngine/42.0",
    ]
    return random.choice(browsers)

def random_color() -> str:
    """Генерирует случайный HEX цвет."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def random_emoji() -> str:
    """Возвращает случайный эмодзи."""
    emojis = "😀😂🤣😊😍🤔😎🙄😴🤯🥳🤡👻🎉💩🔥❤️⭐🌈🍕🎸🚀"
    return random.choice(emojis)

# ═══════════════════════════════════════════════════════════════
# МЕТА-УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def is_kostylpy_loaded() -> bool:
    """Проверяет, загружен ли kostylpy."""
    return 'kostylpy' in sys.modules

def get_kostylpy_version() -> str:
    """Возвращает версию kostylpy."""
    try:
        import kostylpy
        return getattr(kostylpy, '__version__', 'неизвестно')
    except ImportError:
        return 'не загружен'

def system_info() -> Dict[str, str]:
    """Собирает информацию о системе."""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': socket.gethostname(),
        'kostylpy_version': get_kostylpy_version(),
    }

def memory_usage() -> Dict[str, float]:
    """Примерное использование памяти."""
    import psutil
    
    try:
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        return {
            'rss_mb': mem.rss / 1024 / 1024,
            'vms_mb': mem.vms / 1024 / 1024,
            'percent': process.memory_percent(),
        }
    except ImportError:
        return {'error': 'psutil не установлен'}
    except Exception as e:
        return {'error': str(e)}

def retry_on_failure(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 0.1,
    exceptions: Tuple[type, ...] = (Exception,),
    fallback: Any = None,
) -> Any:
    """
    Утилита для повторных попыток (не декоратор, а прямой вызов).
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.UTILS,
                    f"retry_on_failure: не удалось после {max_attempts} попыток: {e}"
                )
                return fallback
            time.sleep(delay * (attempt + 1))

def memoize(func: Callable) -> Callable:
    """
    Мемоизация (кеширование результатов функции).
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.clear_cache = cache.clear
    return wrapper

def deprecated(message: str = "Эта функция устарела"):
    """
    Декоратор для пометки устаревших функций.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__} устарела: {message}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════
# КОНВЕРТЕРЫ
# ═══════════════════════════════════════════════════════════════

def to_json(obj: Any, indent: int = 2, default: Any = None) -> str:
    """Безопасное преобразование в JSON."""
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'type': type(obj).__name__})

def from_json(text: str, default: Any = None) -> Any:
    """Безопасное преобразование из JSON."""
    try:
        return json.loads(text)
    except Exception as e:
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.UTILS,
            f"Ошибка парсинга JSON: {e}"
        )
        return default

def to_base64(data: Union[str, bytes]) -> str:
    """Кодирует в base64."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')

def from_base64(data: str) -> bytes:
    """Декодирует из base64."""
    try:
        return base64.b64decode(data)
    except Exception:
        return b''

def to_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """Хеширует данные."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОРЫ-УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def singleton(cls):
    """
    Декоратор для создания синглтонов.
    """
    instances = {}
    lock = threading.Lock()
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

def synchronized(func):
    """
    Декоратор для синхронизации доступа к функции.
    """
    lock = threading.Lock()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    
    return wrapper

def log_calls(func):
    """
    Декоратор для логирования всех вызовов функции.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ", ".join(
            [repr(a)[:50] for a in args] +
            [f"{k}={repr(v)[:50]}" for k, v in kwargs.items()]
        )
        
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.UTILS,
            f"Вызов: {func.__name__}({args_str})"
        )
        
        return func(*args, **kwargs)
    
    return wrapper

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Строковые
    'safe_str', 'truncate', 'slugify', 'extract_numbers',
    'extract_emails', 'extract_urls', 'obfuscate', 'random_string',
    'is_palindrome', 'levenshtein_distance',
    
    # Числовые
    'safe_int', 'safe_float', 'clamp', 'safe_divide', 'safe_percentage',
    'round_to', 'human_readable_size', 'human_readable_number',
    'is_prime', 'fibonacci',
    
    # Коллекции
    'safe_get', 'safe_set', 'deep_merge', 'flatten_dict', 'unflatten_dict',
    'chunk_list', 'unique_list', 'group_by', 'sort_by_multiple_keys',
    'DotDict', 'SafeList',
    
    # Временные
    'timestamp_ms', 'timestamp_iso', 'time_ago', 'sleep_random', 'measure_time',
    
    # Файловые
    'safe_read_file', 'safe_write_file', 'file_hash', 'find_files',
    'temp_file', 'ensure_dir',
    
    # Сетевые
    'is_port_open', 'get_local_ip', 'simple_http_get',
    
    # Отладка
    'debug_print', 'dump_var', 'get_caller_info',
    
    # Генераторы
    'random_name', 'random_email', 'random_phone', 'random_date',
    'random_ip', 'random_user_agent', 'random_color', 'random_emoji',
    
    # Мета
    'is_kostylpy_loaded', 'get_kostylpy_version', 'system_info', 'memory_usage',
    'retry_on_failure', 'memoize', 'deprecated',
    
    # Конвертеры
    'to_json', 'from_json', 'to_base64', 'from_base64', 'to_hash',
    
    # Декораторы
    'singleton', 'synchronized', 'log_calls',
]

print(f"🔧 kostylpy.utils: загружено {len(__all__)} утилит")
print(f"   Категории: строки, числа, коллекции, время, файлы, сеть, отладка, генераторы, мета, конвертеры, декораторы")