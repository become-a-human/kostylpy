"""
Конфигурация kostylpy.
Управляет всеми настройками, параметрами и костыльными режимами.
Может загружать конфиги из файлов, переменных окружения, 
и даже угадывать что вы хотите (нет, не может).

Содержит:
- KostylConfig — основной класс конфигурации
- ConfigLoader — загрузчик конфигов из разных источников
- ConfigValidator — проверка конфигурации
- ConfigMerger — слияние конфигов
- EnvironmentConfig — конфиг из переменных окружения
- Глобальный экземпляр конфигурации
"""

import os
import sys
import json
import yaml  # Может не быть
from typing import Any, Optional, Dict, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем константы
try:
    from .constants import (
        DEFAULT_CONFIG, PANIC_THRESHOLD, DEFAULT_TIMEOUT,
        DEFAULT_RETRY_COUNT, Emoji, Colors
    )
except ImportError:
    DEFAULT_CONFIG = {}
    PANIC_THRESHOLD = 42
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRY_COUNT = 3
    class Emoji:
        KOSTYL = "🦿"
        WARNING = "⚠️"
        ERROR = "❌"
        SUCCESS = "✅"
    class Colors:
        @staticmethod
        def yellow(t): return t
        @staticmethod
        def red(t): return t
        @staticmethod
        def green(t): return t

# Импортируем состояние
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    _kostyl_state = None

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class ConfigSource(Enum):
    """Источник конфигурации."""
    DEFAULT = "значения по умолчанию"
    FILE = "файл конфигурации"
    ENV = "переменные окружения"
    DICT = "словарь"
    CLI = "командная строка"
    MAGIC = "магия (угадали)"
    KOSTYL = "костыльный источник"

class ConfigFormat(Enum):
    """Формат файла конфигурации."""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    PYTHON = "py"
    AUTO = "auto"  # Угадать

@dataclass
class ConfigChange:
    """Запись об изменении конфигурации."""
    key: str
    old_value: Any
    new_value: Any
    source: ConfigSource
    timestamp: float
    reason: str = ""

# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗЧИК КОНФИГОВ
# ═══════════════════════════════════════════════════════════════

class ConfigLoader:
    """Загружает конфигурацию из разных источников."""
    
    @staticmethod
    def from_dict(data: Dict, source_name: str = "dict") -> Dict:
        """Загружает конфиг из словаря."""
        return data.copy()
    
    @staticmethod
    def from_json(filepath: str) -> Dict:
        """Загружает конфиг из JSON файла."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.UNKNOWN,
                    f"Файл конфига не найден: {filepath}"
                )
            return {}
        except json.JSONDecodeError as e:
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.UNKNOWN,
                    f"Ошибка парсинга JSON в {filepath}: {e}"
                )
            return {}
    
    @staticmethod
    def from_yaml(filepath: str) -> Dict:
        """Загружает конфиг из YAML файла."""
        try:
            import yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            # Пробуем JSON как запасной вариант
            return ConfigLoader.from_json(filepath)
        except Exception as e:
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.UNKNOWN,
                    f"Ошибка загрузки YAML из {filepath}: {e}"
                )
            return {}
    
    @staticmethod
    def from_env(prefix: str = "KOSTYLPY_") -> Dict:
        """Загружает конфиг из переменных окружения."""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Пробуем преобразовать типы
                config[config_key] = ConfigLoader._parse_env_value(value)
        return config
    
    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Парсит значение из переменной окружения."""
        # Булевы значения
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        if value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Числа
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # JSON массивы/словари
        if value.startswith('[') or value.startswith('{'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Строка
        return value
    
    @staticmethod
    def from_file(filepath: str, format: ConfigFormat = ConfigFormat.AUTO) -> Dict:
        """Загружает конфиг из файла, автоматически определяя формат."""
        if format == ConfigFormat.AUTO:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in ('.yaml', '.yml'):
                format = ConfigFormat.YAML
            elif ext == '.json':
                format = ConfigFormat.JSON
            else:
                format = ConfigFormat.JSON  # По умолчанию JSON
        
        if format == ConfigFormat.JSON:
            return ConfigLoader.from_json(filepath)
        elif format == ConfigFormat.YAML:
            return ConfigLoader.from_yaml(filepath)
        else:
            return {}

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР КОНФИГУРАЦИИ
# ═══════════════════════════════════════════════════════════════

class ConfigValidator:
    """Проверяет корректность конфигурации."""
    
    @staticmethod
    def validate(config: Dict) -> List[str]:
        """Проверяет конфиг и возвращает список предупреждений."""
        warnings = []
        
        # Проверяем основные настройки
        if config.get('debug') and config.get('log_level') == 'ERROR':
            warnings.append(
                f"{Emoji.WARNING} debug=True но log_level=ERROR — "
                "вы не увидите отладочных сообщений"
            )
        
        if config.get('coffee_required', True) and not config.get('coffee_available', False):
            warnings.append(
                f"{Emoji.WARNING} Кофе требуется, но недоступен. "
                "Производительность может снизиться."
            )
        
        # Проверяем числовые значения
        panic = config.get('panic_threshold', PANIC_THRESHOLD)
        if panic < 10:
            warnings.append(f"{Emoji.WARNING} panic_threshold={panic} слишком низкий!")
        if panic > 1000:
            warnings.append(f"{Emoji.WARNING} panic_threshold={panic} слишком высокий!")
        
        # Проверяем таймауты
        timeout = config.get('network', {}).get('default_timeout', DEFAULT_TIMEOUT)
        if timeout < 1:
            warnings.append(f"{Emoji.WARNING} Таймаут {timeout}с очень маленький")
        if timeout > 3600:
            warnings.append(f"{Emoji.WARNING} Таймаут {timeout}с — это час!")
        
        # Проверяем модули
        modules = config.get('modules', {})
        if modules.get('monkey_patcher') and not modules.get('interceptors'):
            warnings.append(
                f"{Emoji.WARNING} monkey_patcher включён без interceptors — "
                "это как делать операцию без наркоза"
            )
        
        return warnings

# ═══════════════════════════════════════════════════════════════

class ConfigMerger:
    """Сливает несколько конфигов в один."""
    
    @staticmethod
    def merge(*configs: Dict, deep: bool = True) -> Dict:
        """Объединяет конфиги. Последние перезаписывают первые."""
        result = {}
        
        for config in configs:
            if deep:
                result = ConfigMerger._deep_merge(result, config)
            else:
                result.update(config)
        
        return result
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """Глубокое слияние словарей."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigMerger._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ КЛАСС КОНФИГУРАЦИИ
# ═══════════════════════════════════════════════════════════════

class KostylConfig:
    """
    Главный класс конфигурации kostylpy.
    Синглтон (потому что два разных конфига — это хаос).
    """
    
    _instance = None
    _lock = __import__('threading').Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._config: Dict = DEFAULT_CONFIG.copy()
        self._history: List[ConfigChange] = []
        self._sources: List[ConfigSource] = []
        self._loaded = False
        
        # Загружаем дефолтный конфиг
        self._add_source(ConfigSource.DEFAULT)
    
    # ═══════════════════════════════════════════
    # ЗАГРУЗКА КОНФИГА
    # ═══════════════════════════════════════════
    
    def load_defaults(self):
        """Загружает значения по умолчанию."""
        self._config = DEFAULT_CONFIG.copy()
        self._add_source(ConfigSource.DEFAULT)
        return self
    
    def load_dict(self, data: Dict, source_name: str = "dict"):
        """Загружает конфиг из словаря."""
        loaded = ConfigLoader.from_dict(data, source_name)
        self._update_config(loaded, ConfigSource.DICT, f"Загружено из {source_name}")
        return self
    
    def load_file(self, filepath: str, format: ConfigFormat = ConfigFormat.AUTO):
        """Загружает конфиг из файла."""
        loaded = ConfigLoader.from_file(filepath, format)
        self._update_config(loaded, ConfigSource.FILE, f"Загружено из {filepath}")
        return self
    
    def load_env(self, prefix: str = "KOSTYLPY_"):
        """Загружает конфиг из переменных окружения."""
        loaded = ConfigLoader.from_env(prefix)
        if loaded:
            self._update_config(loaded, ConfigSource.ENV, f"Загружено из env (префикс: {prefix})")
        return self
    
    def load_all(self, config_paths: List[str] = None):
        """Загружает конфиг из всех источников."""
        # 1. Значения по умолчанию
        self.load_defaults()
        
        # 2. Файлы конфигурации
        default_paths = [
            'kostylpy.json',
            'kostylpy.yaml',
            'kostylpy.yml',
            'config/kostylpy.json',
            '~/.kostylpy.json',
            '/etc/kostylpy.json',
        ]
        
        for path in (config_paths or default_paths):
            path = os.path.expanduser(path)
            if os.path.exists(path):
                self.load_file(path)
        
        # 3. Переменные окружения
        self.load_env()
        
        # 4. Валидация
        warnings = ConfigValidator.validate(self._config)
        for warning in warnings:
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.UNKNOWN,
                    warning
                )
        
        self._loaded = True
        return self
    
    def _update_config(self, new_data: Dict, source: ConfigSource, reason: str = ""):
        """Обновляет конфиг новыми данными."""
        for key, value in new_data.items():
            old_value = self._config.get(key)
            
            if isinstance(old_value, dict) and isinstance(value, dict):
                self._config[key] = ConfigMerger._deep_merge(old_value, value)
            else:
                self._config[key] = value
            
            change = ConfigChange(
                key=key,
                old_value=old_value,
                new_value=self._config[key],
                source=source,
                timestamp=__import__('time').time(),
                reason=reason
            )
            self._history.append(change)
        
        self._add_source(source)
    
    def _add_source(self, source: ConfigSource):
        if source not in self._sources:
            self._sources.append(source)
    
    # ═══════════════════════════════════════════
    # ДОСТУП К ЗНАЧЕНИЯМ
    # ═══════════════════════════════════════════
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение по ключу (поддерживает вложенные ключи через точку)."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, reason: str = ""):
        """Устанавливает значение."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        change = ConfigChange(
            key=key,
            old_value=old_value,
            new_value=value,
            source=ConfigSource.KOSTYL,
            timestamp=__import__('time').time(),
            reason=reason
        )
        self._history.append(change)
    
    def has(self, key: str) -> bool:
        """Проверяет существование ключа."""
        return self.get(key) is not None
    
    def all(self) -> Dict:
        """Возвращает всю конфигурацию."""
        return self._config.copy()
    
    # ═══════════════════════════════════════════
    # БЫСТРЫЙ ДОСТУП К ЧАСТЫМ НАСТРОЙКАМ
    # ═══════════════════════════════════════════
    
    @property
    def debug(self) -> bool:
        return self.get('debug', False)
    
    @debug.setter
    def debug(self, value: bool):
        self.set('debug', value, "Установлено через свойство")
    
    @property
    def verbose(self) -> bool:
        return self.get('verbose', False)
    
    @verbose.setter
    def verbose(self, value: bool):
        self.set('verbose', value)
    
    @property
    def log_level(self) -> str:
        return self.get('log_level', 'INFO')
    
    @property
    def panic_threshold(self) -> int:
        return self.get('panic_threshold', PANIC_THRESHOLD)
    
    @property
    def coffee_required(self) -> bool:
        return self.get('coffee_required', True)
    
    @property
    def default_timeout(self) -> float:
        return self.get('network.default_timeout', DEFAULT_TIMEOUT)
    
    @property
    def retry_count(self) -> int:
        return self.get('network.retry_count', DEFAULT_RETRY_COUNT)
    
    # ═══════════════════════════════════════════
    # ИНФОРМАЦИЯ
    # ═══════════════════════════════════════════
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_sources(self) -> List[ConfigSource]:
        return self._sources.copy()
    
    def get_history(self, limit: int = 100) -> List[ConfigChange]:
        return self._history[-limit:]
    
    def validate(self) -> List[str]:
        return ConfigValidator.validate(self._config)
    
    def report(self) -> str:
        """Генерирует отчёт о конфигурации."""
        sources = ", ".join(s.value for s in self._sources)
        warnings = self.validate()
        
        report = "=" * 60 + "\n"
        report += f"{Emoji.KOSTYL} KOSTYLPY КОНФИГУРАЦИЯ\n"
        report += "=" * 60 + "\n"
        report += f"  Источники: {sources}\n"
        report += f"  Debug: {self.debug}\n"
        report += f"  Уровень логирования: {self.log_level}\n"
        report += f"  Порог паники: {self.panic_threshold}\n"
        report += f"  Требуется кофе: {self.coffee_required}\n"
        report += f"  Таймаут: {self.default_timeout}с\n"
        report += f"  Повторных попыток: {self.retry_count}\n"
        
        if warnings:
            report += f"\n  {Emoji.WARNING} Предупреждения:\n"
            for w in warnings:
                report += f"    {w}\n"
        
        report += "=" * 60
        return report
    
    def save(self, filepath: str, format: ConfigFormat = ConfigFormat.JSON):
        """Сохраняет конфигурацию в файл."""
        try:
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            if format == ConfigFormat.JSON:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            elif format == ConfigFormat.YAML:
                try:
                    import yaml
                    with open(filepath, 'w', encoding='utf-8') as f:
                        yaml.dump(self._config, f, default_flow_style=False)
                except ImportError:
                    # Fallback to JSON
                    self.save(filepath, ConfigFormat.JSON)
            
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.UNKNOWN,
                    f"Конфигурация сохранена в {filepath}"
                )
            return True
        except Exception as e:
            if _kostyl_state:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.UNKNOWN,
                    f"Не удалось сохранить конфиг: {e}",
                    was_successful=False
                )
            return False

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ═══════════════════════════════════════════════════════════════

# Создаём глобальный экземпляр конфигурации
config = KostylConfig()

# Автоматически загружаем конфиг из окружения
try:
    config.load_env()
except:
    pass

# ═══════════════════════════════════════════════════════════════
# УДОБНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def get_config() -> KostylConfig:
    """Возвращает глобальный экземпляр конфигурации."""
    return config

def get(key: str, default: Any = None) -> Any:
    """Быстрый доступ к значению конфигурации."""
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Быстрая установка значения."""
    config.set(key, value)

def reload_config(config_paths: List[str] = None):
    """Перезагружает конфигурацию."""
    config.load_all(config_paths)

def save_config(filepath: str = "kostylpy.json"):
    """Сохраняет конфигурацию."""
    config.save(filepath)

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основное
    'KostylConfig',
    'config',  # Глобальный экземпляр
    
    # Классы
    'ConfigLoader',
    'ConfigValidator',
    'ConfigMerger',
    'ConfigSource',
    'ConfigFormat',
    'ConfigChange',
    
    # Функции
    'get_config',
    'get',
    'set_config',
    'reload_config',
    'save_config',
]

print(f"{Emoji.KOSTYL} kostylpy.config: конфигурация загружена")
print(f"   Источники: {', '.join(s.value for s in config.get_sources())}")
print(f"   Debug: {config.debug}")
print(f"   Порог паники: {config.panic_threshold} костылей")