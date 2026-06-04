"""
Monkey Patcher kostylpy.
Патчит всё что движется, и всё что не движется — тоже патчит.
Потому что нормальный inheritance и dependency injection — это скучно.

Содержит:
- MonkeyPatcher — основной класс для патчинга
- PatchTarget — цель для патчинга
- PatchRegistry — реестр всех патчей
- HotFix — горячее исправление на лету
- PatchValidator — проверка что патч не всё сломал
- RollbackManager — откат патчей (если повезёт)
- Встроенные патчи для популярных библиотек
- Автоматический патчер всего подряд
"""

import sys
import os
import time
import types
import inspect
import functools
import threading
import warnings
import builtins
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Set, Type
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
        NUCLEAR = "NUCLEAR"
        APOCALYPTIC = "APOCALYPTIC"
    
    class _FakeCategory(Enum):
        MONKEY = "monkey_patch"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class PatchStatus(Enum):
    """Статус патча."""
    PLANNED = "запланирован"
    APPLIED = "применён"
    FAILED = "провален"
    ROLLED_BACK = "откачен"
    CONFLICT = "конфликт"
    ZOMBIE = "зомби (не должно существовать)"

class PatchType(Enum):
    """Тип патча."""
    REPLACE = "замена функции"
    EXTEND = "расширение функции"
    WRAP = "обёртка функции"
    ADD_METHOD = "добавление метода"
    ADD_ATTRIBUTE = "добавление атрибута"
    REMOVE = "удаление"
    REDIRECT = "перенаправление"
    FIX = "исправление бага"
    KOSTYL = "костыль"
    DANGEROUS = "опасный патч"

@dataclass
class PatchRecord:
    """Запись о применённом патче."""
    id: str
    target: str
    patch_type: PatchType
    status: PatchStatus
    applied_at: float
    applied_by: str
    description: str
    original: Any = None
    patched: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'target': self.target,
            'type': self.patch_type.value,
            'status': self.status.value,
            'applied_at': self.applied_at,
            'description': self.description,
            'error': self.error,
        }

@dataclass
class PatchTarget:
    """Цель для патчинга."""
    module: str
    attribute: str
    is_method: bool = False
    is_class: bool = False
    is_property: bool = False
    
    @property
    def full_path(self) -> str:
        return f"{self.module}.{self.attribute}"
    
    def resolve(self) -> Tuple[Any, str]:
        """
        Разрешает цель патчинга.
        Возвращает (объект, имя_атрибута).
        """
        parts = self.module.split('.')
        current = sys.modules.get(parts[0])
        
        if current is None:
            # Пробуем импортировать
            try:
                current = __import__(self.module)
            except ImportError:
                raise ValueError(f"Не удалось импортировать модуль: {self.module}")
        
        # Проходим по пути модуля
        for part in parts[1:]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise ValueError(f"Не найден атрибут '{part}' в модуле")
        
        # Получаем целевой атрибут
        if hasattr(current, self.attribute):
            target = getattr(current, self.attribute)
        else:
            target = current
        
        return current, self.attribute

# ═══════════════════════════════════════════════════════════════
# ОСНОВНОЙ КЛАСС MONKEY PATCHER
# ═══════════════════════════════════════════════════════════════

class MonkeyPatcher:
    """
    Главный класс для monkey patching'а.
    Патчит всё что попросят, и даже то, что не просят.
    """
    
    _instance = None
    _lock = threading.Lock()
    
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
        
        self.registry: Dict[str, PatchRecord] = {}
        self.history: List[PatchRecord] = []
        self._rollback_stack: List[PatchRecord] = []
        self._active_patches: Set[str] = set()
        self._conflicts: List[str] = []
        self._total_patches = 0
        self._total_rollbacks = 0
        self._total_failures = 0
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.MONKEY,
            "🙈 MonkeyPatcher инициализирован. Готов патчить всё подряд."
        )
    
    def patch(
        self,
        target: Union[str, PatchTarget, Tuple[Any, str]],
        new_value: Any,
        patch_type: PatchType = PatchType.REPLACE,
        description: str = "Патч без описания",
        auto_rollback: bool = True,
        safe_mode: bool = True,
    ) -> PatchRecord:
        """
        Применяет патч к цели.
        
        Args:
            target: Что патчим (строка "module.attr", PatchTarget, или кортеж (объект, атрибут))
            new_value: Новое значение
            patch_type: Тип патча
            description: Описание
            auto_rollback: Сохранять ли оригинал для отката
            safe_mode: Проверять ли совместимость
        
        Returns:
            PatchRecord с информацией о патче
        """
        
        patch_id = f"patch_{int(time.time())}_{random.randint(1000, 9999)}"
        start_time = time.time()
        
        try:
            # Разрешаем цель
            if isinstance(target, str):
                parts = target.rsplit('.', 1)
                if len(parts) == 2:
                    target_obj, attr_name = self._resolve_string(parts[0], parts[1])
                else:
                    raise ValueError(f"Неверный формат цели: {target}")
            elif isinstance(target, PatchTarget):
                target_obj, attr_name = target.resolve()
            elif isinstance(target, tuple) and len(target) == 2:
                target_obj, attr_name = target
            else:
                raise ValueError(f"Неверный тип цели: {type(target)}")
            
            # Сохраняем оригинал
            original = None
            if hasattr(target_obj, attr_name):
                original = getattr(target_obj, attr_name)
            
            # Проверяем конфликты
            if safe_mode and original is not None:
                if not callable(original) and callable(new_value):
                    _kostyl_state.record_kostyl(
                        KostylSeverity.MODERATE,
                        KostylCategory.MONKEY,
                        f"Предупреждение: замена не-callable на callable в '{attr_name}'"
                    )
            
            # Применяем патч
            setattr(target_obj, attr_name, new_value)
            
            # Создаём запись
            record = PatchRecord(
                id=patch_id,
                target=f"{getattr(target_obj, '__name__', str(target_obj))}.{attr_name}",
                patch_type=patch_type,
                status=PatchStatus.APPLIED,
                applied_at=time.time(),
                applied_by=inspect.currentframe().f_back.f_code.co_name if inspect.currentframe().f_back else "unknown",
                description=description,
                original=original if auto_rollback else None,
                patched=new_value,
                metadata={
                    'target_module': getattr(target_obj, '__module__', 'unknown'),
                    'target_type': type(target_obj).__name__,
                    'attr_name': attr_name,
                    'safe_mode': safe_mode,
                }
            )
            
            # Регистрируем
            self.registry[patch_id] = record
            self.history.append(record)
            self._active_patches.add(patch_id)
            self._total_patches += 1
            
            if auto_rollback:
                self._rollback_stack.append(record)
            
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.MONKEY,
                f"🙈 Патч #{self._total_patches} применён: {record.target} "
                f"[{patch_type.value}] - {description}"
            )
            
            return record
            
        except Exception as e:
            self._total_failures += 1
            
            record = PatchRecord(
                id=patch_id,
                target=str(target),
                patch_type=patch_type,
                status=PatchStatus.FAILED,
                applied_at=time.time(),
                applied_by="unknown",
                description=description,
                error=str(e)
            )
            
            self.registry[patch_id] = record
            self.history.append(record)
            
            _kostyl_state.record_kostyl(
                KostylSeverity.CRITICAL,
                KostylCategory.MONKEY,
                f"Патч провален: {target} - {e}",
                was_successful=False
            )
            
            return record
    
    def _resolve_string(self, module_path: str, attr_name: str) -> Tuple[Any, str]:
        """Разрешает строковое представление цели."""
        # Пробуем найти модуль
        module = sys.modules.get(module_path)
        if module is None:
            try:
                module = __import__(module_path)
            except ImportError:
                # Может это встроенный объект?
                if module_path == 'builtins':
                    module = builtins
                else:
                    raise ValueError(f"Модуль не найден: {module_path}")
        
        # Ищем атрибут
        if hasattr(module, attr_name):
            return module, attr_name
        
        # Может быть атрибут вложен в модуль
        parts = module_path.split('.')
        current = module
        for part in parts[1:]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                break
        
        if hasattr(current, attr_name):
            return current, attr_name
        
        raise ValueError(f"Атрибут '{attr_name}' не найден в '{module_path}'")
    
    def rollback(self, patch_id: Optional[str] = None, count: int = 1) -> int:
        """
        Откатывает патчи.
        Если patch_id указан — откатывает конкретный патч.
        Иначе откатывает последние count патчей.
        """
        rolled_back = 0
        
        if patch_id:
            if patch_id in self.registry:
                record = self.registry[patch_id]
                if self._rollback_single(record):
                    rolled_back = 1
        else:
            for _ in range(min(count, len(self._rollback_stack))):
                if self._rollback_stack:
                    record = self._rollback_stack.pop()
                    if self._rollback_single(record):
                        rolled_back += 1
        
        self._total_rollbacks += rolled_back
        return rolled_back
    
    def _rollback_single(self, record: PatchRecord) -> bool:
        """Откатывает один патч."""
        if record.status != PatchStatus.APPLIED:
            return False
        
        try:
            target = record.target.rsplit('.', 1)
            if len(target) == 2:
                module_path, attr_name = target
                module = sys.modules.get(module_path)
                if module is None:
                    module = __import__(module_path)
                
                if record.original is not None:
                    setattr(module, attr_name, record.original)
                elif hasattr(module, attr_name):
                    delattr(module, attr_name)
                
                record.status = PatchStatus.ROLLED_BACK
                self._active_patches.discard(record.id)
                
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.MONKEY,
                    f"🙉 Патч откачен: {record.target}"
                )
                
                return True
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.CRITICAL,
                KostylCategory.MONKEY,
                f"Не удалось откатить патч {record.id}: {e}",
                was_successful=False
            )
        
        return False
    
    def rollback_all(self) -> int:
        """Откатывает ВСЕ патчи."""
        return self.rollback(count=len(self._rollback_stack))
    
    def get_patch(self, patch_id: str) -> Optional[PatchRecord]:
        """Возвращает информацию о патче."""
        return self.registry.get(patch_id)
    
    def list_patches(self, status: Optional[PatchStatus] = None) -> List[PatchRecord]:
        """Возвращает список патчей с фильтром по статусу."""
        if status:
            return [r for r in self.history if r.status == status]
        return self.history.copy()
    
    def report(self) -> str:
        """Генерирует отчёт о всех патчах."""
        active = len(self._active_patches)
        failed = self._total_failures
        rolled_back = self._total_rollbacks
        
        report = "=" * 60 + "\n"
        report += "🙈 MONKEY PATCHER — ОТЧЁТ\n"
        report += "=" * 60 + "\n"
        report += f"  Всего патчей: {self._total_patches}\n"
        report += f"  Активных: {active}\n"
        report += f"  Откачено: {rolled_back}\n"
        report += f"  Провалено: {failed}\n"
        report += "=" * 60 + "\n"
        
        if active > 0:
            report += "\nАктивные патчи:\n"
            for patch_id in list(self._active_patches)[-10:]:
                record = self.registry.get(patch_id)
                if record:
                    report += f"  • {record.id}: {record.target} [{record.patch_type.value}]\n"
        
        return report

# ═══════════════════════════════════════════════════════════════
# ГОРЯЧИЕ ИСПРАВЛЕНИЯ (HOT FIXES)
# ═══════════════════════════════════════════════════════════════

class HotFix:
    """
    Горячее исправление.
    Применяется немедленно, без тестов, без код-ревью.
    """
    
    def __init__(self, name: str = "hotfix"):
        self.name = name
        self._fixes: List[Callable] = []
        self._applied = False
    
    def add_fix(self, fix_func: Callable):
        """Добавляет исправление."""
        self._fixes.append(fix_func)
    
    def apply(self):
        """Применяет все исправления."""
        if self._applied:
            return
        
        for i, fix in enumerate(self._fixes):
            try:
                fix()
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.MONKEY,
                    f"🔥 HotFix '{self.name}': исправление #{i+1} применено"
                )
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.CRITICAL,
                    KostylCategory.MONKEY,
                    f"🔥 HotFix '{self.name}': исправление #{i+1} провалено: {e}",
                    was_successful=False
                )
        
        self._applied = True

# ═══════════════════════════════════════════════════════════════
# ВСТРОЕННЫЕ ПАТЧИ
# ═══════════════════════════════════════════════════════════════

class BuiltinPatches:
    """Набор встроенных патчей для популярных библиотек."""
    
    @staticmethod
    def patch_requests():
        """Патчит библиотеку requests для автоматических ретраев."""
        try:
            import requests
            
            original_get = requests.get
            original_post = requests.post
            
            def patched_get(*args, **kwargs):
                kwargs.setdefault('timeout', 30)
                for attempt in range(3):
                    try:
                        return original_get(*args, **kwargs)
                    except requests.RequestException as e:
                        if attempt == 2:
                            raise
                        time.sleep(0.5 * (attempt + 1))
                return None
            
            def patched_post(*args, **kwargs):
                kwargs.setdefault('timeout', 30)
                for attempt in range(3):
                    try:
                        return original_post(*args, **kwargs)
                    except requests.RequestException as e:
                        if attempt == 2:
                            raise
                        time.sleep(0.5 * (attempt + 1))
                return None
            
            requests.get = patched_get
            requests.post = patched_post
            
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.MONKEY,
                "🐒 requests: добавлены автоматические ретраи"
            )
            return True
        except ImportError:
            return False
    
    @staticmethod
    def patch_json():
        """Патчит json для безопасного парсинга."""
        import json
        
        original_loads = json.loads
        
        def safe_loads(s, *args, **kwargs):
            try:
                return original_loads(s, *args, **kwargs)
            except json.JSONDecodeError:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MINOR,
                    KostylCategory.MONKEY,
                    "🐒 json.loads: невалидный JSON, возвращён пустой словарь"
                )
                return {}
        
        json.loads = safe_loads
        return True
    
    @staticmethod
    def patch_datetime():
        """Патчит datetime.now() чтобы всегда возвращать одно и то же время (для тестов)."""
        import datetime
        
        original_now = datetime.datetime.now
        frozen_time = original_now()
        
        def frozen_now(*args, **kwargs):
            return frozen_time
        
        datetime.datetime.now = frozen_now
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.MONKEY,
            "🐒 datetime.now(): время заморожено"
        )
        return True
    
    @staticmethod
    def patch_random():
        """Делает random детерминированным."""
        import random as random_module
        
        original_random = random_module.random
        original_choice = random_module.choice
        
        def deterministic_random():
            return 0.42  # Ответ на всё
        
        def deterministic_choice(seq):
            return seq[0] if seq else None
        
        random_module.random = deterministic_random
        random_module.choice = deterministic_choice
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.MONKEY,
            "🐒 random: сделан детерминированным"
        )
        return True
    
    @staticmethod
    def patch_os_system():
        """Блокирует опасные системные вызовы."""
        import os
        
        original_system = os.system
        
        def safe_system(command):
            dangerous = ['rm -rf', 'del /f', 'format', 'shutdown', 'reboot', ':(){ :|:& };:']
            for d in dangerous:
                if d in command.lower():
                    _kostyl_state.record_kostyl(
                        KostylSeverity.NUCLEAR,
                        KostylCategory.MONKEY,
                        f"🐒 ЗАБЛОКИРОВАН опасный вызов: {command}"
                    )
                    return -1
            return original_system(command)
        
        os.system = safe_system
        return True
    
    @staticmethod
    def patch_all():
        """Применяет все встроенные патчи."""
        patches = [
            ('requests', BuiltinPatches.patch_requests),
            ('json', BuiltinPatches.patch_json),
            ('random', BuiltinPatches.patch_random),
            ('os', BuiltinPatches.patch_os_system),
        ]
        
        applied = []
        for name, patch_func in patches:
            try:
                if patch_func():
                    applied.append(name)
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MODERATE,
                    KostylCategory.MONKEY,
                    f"Не удалось применить патч для '{name}': {e}"
                )
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.MONKEY,
            f"🐒 Применены встроенные патчи: {', '.join(applied)}"
        )
        
        return applied

# ═══════════════════════════════════════════════════════════════
# ДЕКОРАТОР ДЛЯ ПАТЧЕЙ
# ═══════════════════════════════════════════════════════════════

def monkey_patch(
    target: Union[str, Any],
    attribute: Optional[str] = None,
    description: str = "Патч декоратором",
):
    """
    Декоратор для monkey patching'а.
    
    Использование:
        @monkey_patch('module.Class.method')
        def new_method(self, *args, **kwargs):
            # Новая логика
            pass
    """
    def decorator(func):
        patcher = MonkeyPatcher()
        
        if isinstance(target, str):
            patcher.patch(
                target=target,
                new_value=func,
                patch_type=PatchType.REPLACE,
                description=description
            )
        elif attribute:
            setattr(target, attribute, func)
        
        return func
    
    return decorator

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ ДЛЯ МАССОВОГО ПАТЧИНГА
# ═══════════════════════════════════════════════════════════════

def patch_all_the_things():
    """
    Патчит ВСЁ.
    Серьёзно, всё что можно.
    """
    patcher = MonkeyPatcher()
    
    # Патчим builtins
    patches_to_apply = [
        (builtins, 'print', 'patched by kostylpy'),
        (builtins, 'open', 'patched by kostylpy'),
        (builtins, '__import__', 'patched by kostylpy'),
    ]
    
    applied = []
    for obj, attr, desc in patches_to_apply:
        try:
            if hasattr(obj, attr):
                original = getattr(obj, attr)
                
                @functools.wraps(original)
                def wrapper(*args, _original=original, _attr=attr, **kwargs):
                    try:
                        return _original(*args, **kwargs)
                    except Exception as e:
                        _kostyl_state.record_kostyl(
                            KostylSeverity.MINOR,
                            KostylCategory.MONKEY,
                            f"🐒 patched {_attr}: ошибка перехвачена: {e}"
                        )
                        return None
                
                patcher.patch(
                    target=(obj, attr),
                    new_value=wrapper,
                    patch_type=PatchType.WRAP,
                    description=desc
                )
                applied.append(attr)
        except:
            pass
    
    # Применяем встроенные патчи
    builtin_applied = BuiltinPatches.patch_all()
    
    return applied + builtin_applied

# ═══════════════════════════════════════════════════════════════
# ПРОВЕРКА ПАТЧЕЙ
# ═══════════════════════════════════════════════════════════════

class PatchValidator:
    """
    Проверяет, что патчи не всё сломали.
    (Спойлер: всё равно сломали, но мы попытаемся.)
    """
    
    @staticmethod
    def validate_signature(original: Callable, patched: Callable) -> bool:
        """Проверяет, что сигнатуры совпадают."""
        try:
            orig_sig = inspect.signature(original)
            patch_sig = inspect.signature(patched)
            
            orig_params = list(orig_sig.parameters.keys())
            patch_params = list(patch_sig.parameters.keys())
            
            # Проверяем обязательные параметры
            orig_required = [
                p for p in orig_sig.parameters.values()
                if p.default == inspect.Parameter.empty
            ]
            patch_required = [
                p for p in patch_sig.parameters.values()
                if p.default == inspect.Parameter.empty
            ]
            
            if len(orig_required) > len(patch_required):
                warnings.warn(
                    f"Патч имеет меньше обязательных параметров чем оригинал!"
                )
                return False
            
            return True
        except Exception:
            return True  # Если не можем проверить — считаем что ок
    
    @staticmethod
    def validate_return_type(original: Callable, patched: Callable) -> bool:
        """Примерно проверяет типы возврата."""
        try:
            orig_annotations = getattr(original, '__annotations__', {})
            patch_annotations = getattr(patched, '__annotations__', {})
            
            orig_return = orig_annotations.get('return')
            patch_return = patch_annotations.get('return')
            
            if orig_return and patch_return and orig_return != patch_return:
                warnings.warn(
                    f"Тип возврата патча ({patch_return}) "
                    f"отличается от оригинала ({orig_return})"
                )
                return False
            
            return True
        except Exception:
            return True
    
    @staticmethod
    def test_patch(original: Callable, patched: Callable, test_args: List = None) -> bool:
        """
        Пробует вызвать патч с тестовыми аргументами.
        """
        if test_args is None:
            test_args = []
        
        try:
            patched(*test_args)
            return True
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.MONKEY,
                f"Тест патча провален: {e}"
            )
            return False

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ═══════════════════════════════════════════════════════════════

# Создаём глобальный экземпляр MonkeyPatcher
monkey = MonkeyPatcher()

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основное
    'MonkeyPatcher',
    'monkey',  # Глобальный экземпляр
    
    # Классы
    'PatchRecord',
    'PatchTarget',
    'PatchStatus',
    'PatchType',
    
    # Утилиты
    'HotFix',
    'BuiltinPatches',
    'PatchValidator',
    
    # Декоратор
    'monkey_patch',
    
    # Функции
    'patch_all_the_things',
]

print(f"🙈 kostylpy.monkey_patcher: готов к патчингу")
print(f"   Глобальный экземпляр: monkey")
print(f"   Встроенные патчи: requests, json, datetime, random, os")
print(f"   Функция массового патчинга: patch_all_the_things()")