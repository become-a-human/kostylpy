"""
Валидаторы kostylpy.
Проверяют всё что можно и нельзя.
Находят проблемы там, где их нет, и создают их там, где не нашли.

Содержит:
- TypeValidator — проверка типов (строгая и не очень)
- RangeValidator — проверка диапазонов
- StringValidator — проверка строк
- FileValidator — проверка файлов
- URLValidator — проверка URL
- EmailValidator — проверка email
- PasswordValidator — проверка паролей (очень строгая)
- DataValidator — проверка структур данных
- NullValidator — проверка на None/пустоту
- CustomValidator — создание своих валидаторов
- ValidationPipeline — цепочка валидаторов
- Всевозможные исключения валидации
"""

import re
import os
import sys
import json
import time
import random
import string
import hashlib
import pathlib
import functools
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Set, Pattern
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod

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
        VALIDATOR = "validator"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ИСКЛЮЧЕНИЯ ВАЛИДАЦИИ
# ═══════════════════════════════════════════════════════════════

class ValidationError(Exception):
    """Базовое исключение валидации."""
    
    def __init__(
        self,
        message: str,
        validator_name: str = "",
        value: Any = None,
        field: str = "",
        code: str = "VALIDATION_ERROR",
        severity: str = "ERROR",
        suggestions: Optional[List[str]] = None
    ):
        self.message = message
        self.validator_name = validator_name
        self.value = value
        self.field = field
        self.code = code
        self.severity = severity
        self.suggestions = suggestions or []
        self.timestamp = time.time()
        
        # Строим полное сообщение
        full_msg = f"[{code}]"
        if validator_name:
            full_msg += f" [{validator_name}]"
        if field:
            full_msg += f" {field}:"
        full_msg += f" {message}"
        
        if self.suggestions:
            full_msg += "\n  💡 " + "\n  💡 ".join(self.suggestions)
        
        super().__init__(full_msg)

class TypeValidationError(ValidationError):
    """Ошибка валидации типа."""
    def __init__(self, expected: str, got: str, **kwargs):
        super().__init__(
            message=f"Ожидался тип '{expected}', получен '{got}'",
            code="TYPE_ERROR",
            suggestions=[f"Преобразуйте значение в {expected}", f"Проверьте источник данных"],
            **kwargs
        )
        self.expected = expected
        self.got = got

class RangeValidationError(ValidationError):
    """Ошибка валидации диапазона."""
    def __init__(self, value: Any, min_val: Any, max_val: Any, **kwargs):
        super().__init__(
            message=f"Значение {value} вне диапазона [{min_val}, {max_val}]",
            code="RANGE_ERROR",
            suggestions=[
                f"Выберите значение между {min_val} и {max_val}",
                "Проверьте границы диапазона"
            ],
            **kwargs
        )

class StringValidationError(ValidationError):
    """Ошибка валидации строки."""
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=reason,
            code="STRING_ERROR",
            suggestions=["Проверьте формат строки", "Убедитесь в отсутствии запрещённых символов"],
            **kwargs
        )

class FormatValidationError(ValidationError):
    """Ошибка формата данных."""
    def __init__(self, expected_format: str, **kwargs):
        super().__init__(
            message=f"Неверный формат, ожидается: {expected_format}",
            code="FORMAT_ERROR",
            suggestions=[f"Приведите данные к формату: {expected_format}"],
            **kwargs
        )

class NullValidationError(ValidationError):
    """Ошибка: значение None там, где не должно быть."""
    def __init__(self, **kwargs):
        super().__init__(
            message="Значение не должно быть None/пустым",
            code="NULL_ERROR",
            suggestions=["Укажите значение", "Проверьте, что данные инициализированы"],
            **kwargs
        )

class SecurityValidationError(ValidationError):
    """Ошибка безопасности."""
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=f"Нарушение безопасности: {reason}",
            code="SECURITY_ERROR",
            severity="CRITICAL",
            suggestions=["НЕ ИГНОРИРУЙТЕ ЭТУ ОШИБКУ", "Проверьте входные данные на атаки"],
            **kwargs
        )

# ═══════════════════════════════════════════════════════════════
# РЕЗУЛЬТАТ ВАЛИДАЦИИ
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Результат валидации."""
    is_valid: bool
    value: Any
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validated_at: float = field(default_factory=time.time)
    validator_name: str = ""
    duration: float = 0.0
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        return len(self.warnings)
    
    def add_error(self, error: ValidationError):
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def to_dict(self) -> dict:
        return {
            'is_valid': self.is_valid,
            'value': str(self.value)[:200],
            'errors': [
                {
                    'code': e.code,
                    'message': e.message,
                    'field': e.field,
                    'severity': e.severity,
                }
                for e in self.errors
            ],
            'warnings': self.warnings,
            'metadata': self.metadata,
            'validator': self.validator_name,
            'duration': self.duration,
        }
    
    def __str__(self):
        status = "✅ ВАЛИДНО" if self.is_valid else "❌ НЕВАЛИДНО"
        parts = [f"{status} ({self.validator_name})"]
        
        if self.errors:
            parts.append(f"  Ошибок: {len(self.errors)}")
            for error in self.errors[:5]:
                parts.append(f"    • {error.message[:100]}")
            if len(self.errors) > 5:
                parts.append(f"    ... и ещё {len(self.errors) - 5}")
        
        if self.warnings:
            parts.append(f"  Предупреждений: {len(self.warnings)}")
            for warning in self.warnings[:3]:
                parts.append(f"    ⚠️ {warning[:100]}")
        
        return "\n".join(parts)
    
    def raise_if_invalid(self):
        """Выбрасывает исключение если невалидно."""
        if not self.is_valid and self.errors:
            raise self.errors[0]
    
    def get_or_default(self, default: Any) -> Any:
        """Возвращает значение или default если невалидно."""
        return self.value if self.is_valid else default
    
    def __bool__(self):
        return self.is_valid

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ ВАЛИДАТОР
# ═══════════════════════════════════════════════════════════════

class BaseValidator(ABC):
    """Абстрактный базовый валидатор."""
    
    _validator_registry: Dict[str, 'BaseValidator'] = {}
    
    def __init__(
        self,
        name: str = "валидатор",
        required: bool = True,
        nullable: bool = False,
        coerce: bool = False,
        default: Any = None,
        strict: bool = False,
        max_errors: int = 100,
    ):
        self.name = name
        self.required = required
        self.nullable = nullable
        self.coerce = coerce
        self.default = default
        self.strict = strict
        self.max_errors = max_errors
        
        self._call_count = 0
        self._error_count = 0
        self._last_result: Optional[ValidationResult] = None
        
        self._validator_registry[name] = self
    
    @abstractmethod
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        """Внутренняя логика валидации. Должна быть переопределена."""
        pass
    
    def validate(self, value: Any, field: str = "") -> ValidationResult:
        """Публичный метод валидации с пред- и пост-обработкой."""
        start_time = time.time()
        self._call_count += 1
        
        result = ValidationResult(
            is_valid=True,
            value=value,
            validator_name=self.name,
        )
        
        # Проверка на None
        if value is None:
            if self.nullable:
                result.metadata['was_none'] = True
                result.duration = time.time() - start_time
                return result
            elif not self.required:
                result.value = self.default
                result.metadata['used_default'] = True
                result.duration = time.time() - start_time
                return result
            else:
                result.add_error(NullValidationError(
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
                result.duration = time.time() - start_time
                self._last_result = result
                return result
        
        # Приведение типов если нужно
        if self.coerce:
            try:
                value = self._coerce(value)
                result.value = value
            except Exception as e:
                result.add_error(TypeValidationError(
                    expected="совместимый тип",
                    got=type(value).__name__,
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
                result.duration = time.time() - start_time
                self._last_result = result
                return result
        
        # Основная валидация
        try:
            inner_result = self._validate(value, field)
            result.errors.extend(inner_result.errors)
            result.warnings.extend(inner_result.warnings)
            result.metadata.update(inner_result.metadata)
            result.value = inner_result.value
            
            if result.errors:
                result.is_valid = False
                self._error_count += len(result.errors)
        except Exception as e:
            if not isinstance(e, ValidationError):
                e = ValidationError(
                    message=f"Ошибка валидации: {str(e)}",
                    validator_name=self.name,
                    value=value,
                    field=field,
                    code="VALIDATOR_CRASH"
                )
            result.add_error(e)
        
        result.duration = time.time() - start_time
        self._last_result = result
        
        # Логируем если есть ошибки
        if not result.is_valid:
            _kostyl_state.record_kostyl(
                KostylSeverity.MINOR,
                KostylCategory.VALIDATOR,
                f"Валидатор '{self.name}': {result.error_count} ошибок "
                f"для поля '{field}' (значение: {str(value)[:50]})"
            )
        
        return result
    
    def _coerce(self, value: Any) -> Any:
        """Приводит значение к нужному типу. По умолчанию — не трогает."""
        return value
    
    def __call__(self, value: Any, field: str = "") -> ValidationResult:
        """Позволяет использовать валидатор как функцию."""
        return self.validate(value, field)
    
    def get_last_result(self) -> Optional[ValidationResult]:
        return self._last_result
    
    def reset_stats(self):
        self._call_count = 0
        self._error_count = 0
    
    @property
    def stats(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'calls': self._call_count,
            'errors': self._error_count,
            'error_rate': self._error_count / max(1, self._call_count),
        }
    
    @classmethod
    def get_validator(cls, name: str) -> Optional['BaseValidator']:
        return cls._validator_registry.get(name)

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР ТИПОВ
# ═══════════════════════════════════════════════════════════════

class TypeValidator(BaseValidator):
    """
    Проверяет тип значения.
    Может принимать несколько допустимых типов.
    """
    
    def __init__(
        self,
        expected_type: Union[type, Tuple[type, ...]],
        name: str = "валидатор типов",
        allow_subclasses: bool = True,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.expected_types = expected_type if isinstance(expected_type, tuple) else (expected_type,)
        self.allow_subclasses = allow_subclasses
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        type_names = [t.__name__ for t in self.expected_types]
        
        if self.allow_subclasses:
            if not isinstance(value, self.expected_types):
                result.add_error(TypeValidationError(
                    expected=" | ".join(type_names),
                    got=type(value).__name__,
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
        else:
            if type(value) not in self.expected_types:
                result.add_error(TypeValidationError(
                    expected=" | ".join(type_names),
                    got=type(value).__name__,
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
        
        return result
    
    def _coerce(self, value: Any) -> Any:
        """Пытается привести значение к нужному типу."""
        for t in self.expected_types:
            try:
                if t == bool:
                    if isinstance(value, str):
                        return value.lower() in ('true', '1', 'yes', 'да')
                    return bool(value)
                elif t == int:
                    return int(value)
                elif t == float:
                    return float(value)
                elif t == str:
                    return str(value)
                elif t == list:
                    if isinstance(value, str):
                        try:
                            return json.loads(value)
                        except:
                            return [value]
                    return list(value) if hasattr(value, '__iter__') else [value]
                elif t == dict:
                    if isinstance(value, str):
                        try:
                            return json.loads(value)
                        except:
                            pass
                    return dict(value) if hasattr(value, 'items') else {'value': value}
            except (ValueError, TypeError):
                continue
        
        raise ValueError(f"Не удалось привести {type(value).__name__} к нужному типу")

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР ДИАПАЗОНА
# ═══════════════════════════════════════════════════════════════

class RangeValidator(BaseValidator):
    """
    Проверяет, что значение находится в заданном диапазоне.
    """
    
    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        include_min: bool = True,
        include_max: bool = True,
        name: str = "валидатор диапазона",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.include_min = include_min
        self.include_max = include_max
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, (int, float)):
            result.add_error(TypeValidationError(
                expected="int или float",
                got=type(value).__name__,
                validator_name=self.name,
                value=value,
                field=field
            ))
            return result
        
        if self.min_value is not None:
            if self.include_min:
                if value < self.min_value:
                    result.add_error(RangeValidationError(
                        value=value,
                        min_val=self.min_value,
                        max_val=self.max_value or "∞",
                        validator_name=self.name,
                        field=field
                    ))
            else:
                if value <= self.min_value:
                    result.add_error(RangeValidationError(
                        value=value,
                        min_val=self.min_value,
                        max_val=self.max_value or "∞",
                        validator_name=self.name,
                        field=field
                    ))
        
        if self.max_value is not None:
            if self.include_max:
                if value > self.max_value:
                    result.add_error(RangeValidationError(
                        value=value,
                        min_val=self.min_value or "-∞",
                        max_val=self.max_value,
                        validator_name=self.name,
                        field=field
                    ))
            else:
                if value >= self.max_value:
                    result.add_error(RangeValidationError(
                        value=value,
                        min_val=self.min_value or "-∞",
                        max_val=self.max_value,
                        validator_name=self.name,
                        field=field
                    ))
        
        # Авто-фикс: обрезаем значение если выходит за границы
        if not result.is_valid and not self.strict:
            if self.min_value is not None and value < self.min_value:
                result.value = self.min_value
                result.add_warning(
                    f"Значение {value} скорректировано до минимума: {self.min_value}"
                )
                result.is_valid = True
                result.errors.clear()
            elif self.max_value is not None and value > self.max_value:
                result.value = self.max_value
                result.add_warning(
                    f"Значение {value} скорректировано до максимума: {self.max_value}"
                )
                result.is_valid = True
                result.errors.clear()
        
        return result

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР СТРОК
# ═══════════════════════════════════════════════════════════════

class StringValidator(BaseValidator):
    """
    Мега-валидатор строк.
    Проверяет длину, паттерны, символы, и кучу всего ещё.
    """
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_chars: Optional[str] = None,
        forbidden_chars: Optional[str] = None,
        starts_with: Optional[str] = None,
        ends_with: Optional[str] = None,
        contains: Optional[str] = None,
        not_contains: Optional[str] = None,
        strip: bool = True,
        normalize: bool = True,
        name: str = "валидатор строк",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_chars = set(allowed_chars) if allowed_chars else None
        self.forbidden_chars = set(forbidden_chars) if forbidden_chars else None
        self.starts_with = starts_with
        self.ends_with = ends_with
        self.contains = contains
        self.not_contains = not_contains
        self.strip = strip
        self.normalize = normalize
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, str):
            result.add_error(TypeValidationError(
                expected="str",
                got=type(value).__name__,
                validator_name=self.name,
                value=value,
                field=field
            ))
            return result
        
        # Нормализация
        if self.strip:
            value = value.strip()
            result.value = value
        
        if self.normalize:
            # Убираем множественные пробелы
            value = re.sub(r'\s+', ' ', value)
            result.value = value
        
        # Проверка длины
        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(StringValidationError(
                reason=f"Строка слишком короткая (минимум {self.min_length} символов, получено {len(value)})",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        if self.max_length is not None and len(value) > self.max_length:
            if not self.strict:
                # Авто-обрезание
                result.value = value[:self.max_length]
                result.add_warning(
                    f"Строка обрезана до {self.max_length} символов (было {len(value)})"
                )
            else:
                result.add_error(StringValidationError(
                    reason=f"Строка слишком длинная (максимум {self.max_length} символов, получено {len(value)})",
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
        
        # Проверка паттерна
        if self.pattern and not self.pattern.match(value):
            result.add_error(FormatValidationError(
                expected_format=f"соответствие паттерну {self.pattern.pattern}",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        # Проверка разрешённых символов
        if self.allowed_chars:
            invalid_chars = set(value) - self.allowed_chars
            if invalid_chars:
                result.add_error(StringValidationError(
                    reason=f"Недопустимые символы: {', '.join(sorted(invalid_chars))}",
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
        
        # Проверка запрещённых символов
        if self.forbidden_chars:
            found_forbidden = set(value) & self.forbidden_chars
            if found_forbidden:
                result.add_error(StringValidationError(
                    reason=f"Запрещённые символы: {', '.join(sorted(found_forbidden))}",
                    validator_name=self.name,
                    value=value,
                    field=field
                ))
        
        # Проверка начала/конца
        if self.starts_with and not value.startswith(self.starts_with):
            result.add_error(FormatValidationError(
                expected_format=f"начинается с '{self.starts_with}'",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        if self.ends_with and not value.endswith(self.ends_with):
            result.add_error(FormatValidationError(
                expected_format=f"заканчивается на '{self.ends_with}'",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        # Проверка содержимого
        if self.contains and self.contains not in value:
            result.add_error(StringValidationError(
                reason=f"Строка должна содержать '{self.contains}'",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        if self.not_contains and self.not_contains in value:
            result.add_error(StringValidationError(
                reason=f"Строка не должна содержать '{self.not_contains}'",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        return result
    
    def _coerce(self, value: Any) -> str:
        return str(value)

# ═══════════════════════════════════════════════════════════════
# СПЕЦИАЛИЗИРОВАННЫЕ ВАЛИДАТОРЫ
# ═══════════════════════════════════════════════════════════════

class EmailValidator(BaseValidator):
    """Проверяет email адреса. Очень строго (или нет)."""
    
    # Простая регулярка для email
    _EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Список популярных доменов для опечаток
    _COMMON_TYPOS = {
        'gmial.com': 'gmail.com',
        'gmail.con': 'gmail.com',
        'gmai.com': 'gmail.com',
        'yaho.com': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
        'outlook.con': 'outlook.com',
    }
    
    def __init__(
        self,
        name: str = "валидатор email",
        check_mx: bool = False,
        suggest_fixes: bool = True,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.check_mx = check_mx
        self.suggest_fixes = suggest_fixes
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, str):
            result.add_error(TypeValidationError(
                expected="str",
                got=type(value).__name__,
                validator_name=self.name,
                value=value,
                field=field
            ))
            return result
        
        value = value.strip().lower()
        result.value = value
        
        if not self._EMAIL_PATTERN.match(value):
            suggestion = ""
            if self.suggest_fixes:
                # Ищем опечатки
                for typo, fix in self._COMMON_TYPOS.items():
                    if typo in value:
                        suggestion = f" Возможно, вы имели в виду: {value.replace(typo, fix)}?"
                        break
            
            result.add_error(FormatValidationError(
                expected_format="email (user@example.com)",
                validator_name=self.name,
                value=value,
                field=field,
                suggestions=[f"Проверьте формат email{suggestion}"]
            ))
        
        # Проверка на подозрительные email
        suspicious_domains = ['test.com', 'example.com', 'mailinator.com', 'tempmail.com']
        domain = value.split('@')[-1] if '@' in value else ''
        if domain in suspicious_domains:
            result.add_warning(f"Подозрительный домен: {domain}")
        
        return result

class URLValidator(BaseValidator):
    """Проверяет URL."""
    
    _URL_PATTERN = re.compile(
        r'^https?://'
        r'[a-zA-Z0-9]+'
        r'[a-zA-Z0-9.-]*'
        r'\.[a-zA-Z]{2,}'
        r'[^\s]*$'
    )
    
    def __init__(self, name: str = "валидатор URL", require_https: bool = False, **kwargs):
        super().__init__(name=name, **kwargs)
        self.require_https = require_https
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, str):
            result.add_error(TypeValidationError(
                expected="str",
                got=type(value).__name__,
                validator_name=self.name,
                value=value,
                field=field
            ))
            return result
        
        value = value.strip()
        result.value = value
        
        if not self._URL_PATTERN.match(value):
            result.add_error(FormatValidationError(
                expected_format="URL (http:// или https://)",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        if self.require_https and not value.startswith('https://'):
            result.add_error(SecurityValidationError(
                reason="URL должен использовать HTTPS",
                validator_name=self.name,
                value=value,
                field=field
            ))
        
        return result

class PasswordValidator(BaseValidator):
    """
    Очень строгий валидатор паролей.
    Требует всё сразу: цифры, буквы, спецсимволы, эмодзи, руны...
    """
    
    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 128,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        require_emoji: bool = False,
        require_rune: bool = False,
        forbid_common: bool = True,
        name: str = "валидатор паролей",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.require_emoji = require_emoji
        self.require_rune = require_rune
        self.forbid_common = forbid_common
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, str):
            result.add_error(TypeValidationError(
                expected="str",
                got=type(value).__name__,
                validator_name=self.name,
                value="***",
                field=field
            ))
            return result
        
        # Никогда не логируем пароль!
        masked = "*" * min(len(value), 4) + "..." if len(value) > 4 else "***"
        
        if len(value) < self.min_length:
            result.add_error(ValidationError(
                message=f"Пароль слишком короткий (минимум {self.min_length} символов)",
                code="PASSWORD_TOO_SHORT",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if len(value) > self.max_length:
            result.add_error(ValidationError(
                message=f"Пароль слишком длинный (максимум {self.max_length} символов)",
                code="PASSWORD_TOO_LONG",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if self.require_uppercase and not re.search(r'[A-ZА-ЯЁ]', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать заглавные буквы",
                code="PASSWORD_NO_UPPERCASE",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if self.require_lowercase and not re.search(r'[a-zа-яё]', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать строчные буквы",
                code="PASSWORD_NO_LOWERCASE",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if self.require_digits and not re.search(r'\d', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать цифры",
                code="PASSWORD_NO_DIGITS",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\/`~]', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать специальные символы",
                code="PASSWORD_NO_SPECIAL",
                validator_name=self.name,
                value=masked,
                field=field
            ))
        
        if self.require_emoji and not re.search(r'[\U0001F300-\U0001F9FF]', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать хотя бы один эмодзи 🎉",
                code="PASSWORD_NO_EMOJI",
                validator_name=self.name,
                value=masked,
                field=field,
                suggestions=["Добавьте эмодзи для надёжности: 🔒🔑🛡️"]
            ))
        
        if self.require_rune and not re.search(r'[\u16A0-\u16FF]', value):
            result.add_error(ValidationError(
                message="Пароль должен содержать хотя бы одну руну ᚠ",
                code="PASSWORD_NO_RUNE",
                validator_name=self.name,
                value=masked,
                field=field,
                suggestions=["Древние руны защитят ваш пароль: ᚠᚢᚦᚨᚱ"]
            ))
        
        if self.forbid_common:
            common_passwords = [
                'password', '12345678', 'qwerty', 'admin',
                'password123', 'letmein', 'monkey', 'dragon',
            ]
            if value.lower() in common_passwords:
                result.add_error(SecurityValidationError(
                    reason="Пароль слишком распространённый",
                    validator_name=self.name,
                    value=masked,
                    field=field,
                    suggestions=["Используйте более уникальный пароль"]
                ))
        
        return result

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

class FileValidator(BaseValidator):
    """Проверяет файлы на существование, размер, тип."""
    
    def __init__(
        self,
        must_exist: bool = True,
        max_size_mb: Optional[float] = None,
        allowed_extensions: Optional[List[str]] = None,
        allowed_mime_types: Optional[List[str]] = None,
        name: str = "валидатор файлов",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.must_exist = must_exist
        self.max_size_mb = max_size_mb
        self.allowed_extensions = set(allowed_extensions or [])
        self.allowed_mime_types = set(allowed_mime_types or [])
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        path = str(value) if not isinstance(value, (str, pathlib.Path)) else value
        result.value = str(path)
        
        path_obj = pathlib.Path(path)
        
        if self.must_exist and not path_obj.exists():
            result.add_error(ValidationError(
                message=f"Файл не существует: {path}",
                code="FILE_NOT_FOUND",
                validator_name=self.name,
                value=str(path),
                field=field,
                suggestions=["Проверьте путь к файлу", "Создайте файл перед использованием"]
            ))
            return result
        
        if path_obj.exists() and path_obj.is_file():
            # Проверка размера
            if self.max_size_mb:
                size_mb = path_obj.stat().st_size / (1024 * 1024)
                if size_mb > self.max_size_mb:
                    result.add_error(ValidationError(
                        message=f"Файл слишком большой: {size_mb:.1f} МБ (максимум {self.max_size_mb} МБ)",
                        code="FILE_TOO_LARGE",
                        validator_name=self.name,
                        value=str(path),
                        field=field,
                        suggestions=["Сожмите файл", "Используйте файл меньшего размера"]
                    ))
            
            # Проверка расширения
            if self.allowed_extensions:
                ext = path_obj.suffix.lower()
                if ext not in self.allowed_extensions:
                    result.add_error(ValidationError(
                        message=f"Недопустимое расширение: {ext}",
                        code="FILE_BAD_EXTENSION",
                        validator_name=self.name,
                        value=str(path),
                        field=field,
                        suggestions=[f"Допустимые расширения: {', '.join(self.allowed_extensions)}"]
                    ))
        
        return result

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР NULL/ПУСТОТЫ
# ═══════════════════════════════════════════════════════════════

class NullValidator(BaseValidator):
    """
    Проверяет, что значение не None и не пустое.
    """
    
    def __init__(
        self,
        name: str = "валидатор на None",
        check_empty_string: bool = True,
        check_empty_list: bool = True,
        check_empty_dict: bool = True,
        check_zero: bool = False,
        check_false: bool = False,
        **kwargs
    ):
        super().__init__(name=name, required=True, nullable=False, **kwargs)
        self.check_empty_string = check_empty_string
        self.check_empty_list = check_empty_list
        self.check_empty_dict = check_empty_dict
        self.check_zero = check_zero
        self.check_false = check_false
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        reasons = []
        
        if value is None:
            reasons.append("None")
        elif self.check_empty_string and isinstance(value, str) and value.strip() == "":
            reasons.append("пустая строка")
        elif self.check_empty_list and isinstance(value, (list, tuple, set)) and len(value) == 0:
            reasons.append("пустая коллекция")
        elif self.check_empty_dict and isinstance(value, dict) and len(value) == 0:
            reasons.append("пустой словарь")
        elif self.check_zero and isinstance(value, (int, float)) and value == 0:
            reasons.append("ноль")
        elif self.check_false and isinstance(value, bool) and value is False:
            reasons.append("False")
        
        if reasons:
            result.add_error(NullValidationError(
                validator_name=self.name,
                value=value,
                field=field,
                suggestions=["Укажите непустое значение"]
            ))
            result.metadata['reasons'] = reasons
        
        return result

# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОР ДАННЫХ (СЛОВАРЬ/ОБЪЕКТ)
# ═══════════════════════════════════════════════════════════════

class DataValidator(BaseValidator):
    """
    Валидирует словари по схеме.
    Схема — это словарь, где ключи — имена полей,
    а значения — валидаторы.
    """
    
    def __init__(
        self,
        schema: Dict[str, BaseValidator],
        name: str = "валидатор данных",
        allow_unknown: bool = False,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.schema = schema
        self.allow_unknown = allow_unknown
    
    def _validate(self, value: Any, field: str = "") -> ValidationResult:
        result = ValidationResult(is_valid=True, value=value, validator_name=self.name)
        
        if not isinstance(value, dict):
            result.add_error(TypeValidationError(
                expected="dict",
                got=type(value).__name__,
                validator_name=self.name,
                value=value,
                field=field
            ))
            return result
        
        validated_data = {}
        
        # Проверяем известные поля
        for field_name, validator in self.schema.items():
            field_value = value.get(field_name)
            field_result = validator.validate(field_value, field_name)
            
            if not field_result.is_valid:
                result.errors.extend(field_result.errors)
                result.is_valid = False
            else:
                validated_data[field_name] = field_result.value
            
            result.warnings.extend(
                f"{field_name}: {w}" for w in field_result.warnings
            )
        
        # Проверяем неизвестные поля
        if not self.allow_unknown:
            unknown = set(value.keys()) - set(self.schema.keys())
            if unknown:
                for unknown_field in unknown:
                    result.add_warning(f"Неизвестное поле: {unknown_field}")
                    if self.strict:
                        result.add_error(ValidationError(
                            message=f"Неизвестное поле: {unknown_field}",
                            code="UNKNOWN_FIELD",
                            validator_name=self.name,
                            value=str(value.get(unknown_field))[:50],
                            field=unknown_field,
                            suggestions=["Уберите неизвестное поле", "Добавьте его в схему"]
                        ))
        
        result.value = validated_data
        return result

# ═══════════════════════════════════════════════════════════════
# КОНВЕЙЕР ВАЛИДАЦИИ
# ═══════════════════════════════════════════════════════════════

class ValidationPipeline:
    """
    Цепочка валидаторов.
    Применяет валидаторы последовательно.
    Может останавливаться на первой ошибке или собирать все.
    """
    
    def __init__(
        self,
        name: str = "конвейер валидации",
        stop_on_first_error: bool = False,
        collect_all_errors: bool = True,
    ):
        self.name = name
        self.stop_on_first_error = stop_on_first_error
        self.collect_all_errors = collect_all_errors
        self._validators: List[BaseValidator] = []
    
    def add(self, validator: BaseValidator) -> 'ValidationPipeline':
        """Добавляет валидатор в цепочку."""
        self._validators.append(validator)
        return self
    
    def validate(self, value: Any, field: str = "") -> ValidationResult:
        """Прогоняет значение через все валидаторы."""
        result = ValidationResult(
            is_valid=True,
            value=value,
            validator_name=self.name,
        )
        
        current_value = value
        
        for validator in self._validators:
            try:
                step_result = validator.validate(current_value, field)
                
                if not step_result.is_valid:
                    result.errors.extend(step_result.errors)
                    result.is_valid = False
                    
                    if self.stop_on_first_error:
                        result.value = step_result.value
                        return result
                
                result.warnings.extend(step_result.warnings)
                current_value = step_result.value
                
            except Exception as e:
                result.add_error(ValidationError(
                    message=f"Валидатор '{validator.name}' упал: {str(e)}",
                    code="VALIDATOR_CRASH",
                    validator_name=validator.name,
                    value=current_value,
                    field=field
                ))
                if self.stop_on_first_error:
                    return result
        
        result.value = current_value
        return result
    
    def __call__(self, value: Any, field: str = "") -> ValidationResult:
        return self.validate(value, field)
    
    def __len__(self):
        return len(self._validators)
    
    def __repr__(self):
        return f"<ValidationPipeline '{self.name}' ({len(self._validators)} валидаторов)>"

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР ДЛЯ ВАЛИДАЦИИ
# ═══════════════════════════════════════════════════════════════

def validate_args(**validators: BaseValidator):
    """
    Декоратор для валидации аргументов функции.
    
    Пример:
        @validate_args(
            name=StringValidator(min_length=2),
            age=RangeValidator(min_value=0, max_value=150)
        )
        def greet(name, age):
            print(f"Привет, {name}! Тебе {age} лет.")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем имена аргументов функции
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            errors = []
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    result = validator.validate(value, param_name)
                    if not result.is_valid:
                        errors.extend(result.errors)
            
            if errors:
                error_messages = "\n".join(f"  • {e}" for e in errors)
                raise ValidationError(
                    message=f"Валидация аргументов функции '{func.__name__}' провалена:\n{error_messages}",
                    code="FUNCTION_ARGS_INVALID",
                    validator_name="validate_args"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════
# ПРЕДОПРЕДЕЛЁННЫЕ ВАЛИДАТОРЫ
# ═══════════════════════════════════════════════════════════════

# Валидаторы, готовые к использованию
NotEmptyString = StringValidator(min_length=1, name="непустая строка")
PositiveInt = TypeValidator(int, name="положительное целое")
PositiveFloat = TypeValidator(float, name="положительное число")
StrictBool = TypeValidator(bool, name="строгий boolean")
ValidEmail = EmailValidator(name="email")
ValidURL = URLValidator(name="url")
StrongPassword = PasswordValidator(name="надёжный пароль")
NotNull = NullValidator(name="не None")

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Исключения
    'ValidationError',
    'TypeValidationError',
    'RangeValidationError',
    'StringValidationError',
    'FormatValidationError',
    'NullValidationError',
    'SecurityValidationError',
    
    # Результат
    'ValidationResult',
    
    # Базовые
    'BaseValidator',
    
    # Валидаторы
    'TypeValidator',
    'RangeValidator',
    'StringValidator',
    'EmailValidator',
    'URLValidator',
    'PasswordValidator',
    'FileValidator',
    'NullValidator',
    'DataValidator',
    
    # Конвейер
    'ValidationPipeline',
    
    # Декоратор
    'validate_args',
    
    # Предопределённые
    'NotEmptyString',
    'PositiveInt',
    'PositiveFloat',
    'StrictBool',
    'ValidEmail',
    'ValidURL',
    'StrongPassword',
    'NotNull',
]

print(f"✅ kostylpy.validators: загружено {len(BaseValidator._validator_registry)} валидаторов")
print(f"   Типы: Type, Range, String, Email, URL, Password, File, Null, Data")
print(f"   Конвейер: ValidationPipeline")
print(f"   Декоратор: validate_args")