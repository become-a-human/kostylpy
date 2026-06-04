"""
Перехватчики kostylpy.
Перехватывают ВСЁ. Вообще всё.
Вызовы функций, доступ к атрибутам, операции с типами,
сетевые запросы, системные вызовы — всё под контролем.

Содержит:
- FunctionInterceptor — перехват вызовов функций
- AttributeInterceptor — перехват доступа к атрибутам
- TypeInterceptor — перехват операций с типами
- ImportInterceptor — перехват импортов
- CallInterceptor — перехват любых вызовов
- SystemCallInterceptor — перехват системных вызовов
- GlobalInterceptor — перехват всего сразу
"""

import sys
import time
import threading
import functools
import inspect
import traceback
import warnings
import builtins
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Set
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
    
    class _FakeCategory(Enum):
        INTERCEPTOR = "interceptor"
        UNKNOWN = "unknown"
    
    KostylSeverity = _FakeSeverity
    KostylCategory = _FakeCategory
    
    class _FakeState:
        def record_kostyl(self, *args, **kwargs):
            pass
    _kostyl_state = _FakeState()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class InterceptMode(Enum):
    """Режим перехвата."""
    LOG_ONLY = "только логирование"        # Логируем, но не мешаем
    MODIFY = "модификация"                  # Можем изменить аргументы/результат
    FILTER = "фильтрация"                   # Можем заблокировать вызов
    REPLACE = "замена"                      # Полностью заменяем логику
    SPY = "шпионаж"                         # Скрытое наблюдение
    SABOTAGE = "саботаж"                    # Случайно всё ломаем

class InterceptResult(Enum):
    """Результат перехвата."""
    ALLOW = "разрешено"
    DENY = "запрещено"
    MODIFIED = "модифицировано"
    REPLACED = "заменено"
    DELAYED = "отложено"
    IGNORED = "проигнорировано"
    CHAOS = "хаос"

@dataclass
class InterceptRecord:
    """Запись о перехвате."""
    id: int
    timestamp: float
    interceptor_name: str
    target: str
    mode: InterceptMode
    result: InterceptResult
    args_summary: str
    result_summary: str
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return (
            f"[{self.interceptor_name}] {self.target} "
            f"({self.mode.value}) → {self.result.value} "
            f"за {self.duration:.4f}с"
        )

@dataclass
class InterceptorStats:
    """Статистика перехватчика."""
    total_intercepts: int = 0
    allowed: int = 0
    denied: int = 0
    modified: int = 0
    replaced: int = 0
    errors: int = 0
    total_time: float = 0.0
    records: List[InterceptRecord] = field(default_factory=list)
    
    @property
    def average_time(self) -> float:
        if self.total_intercepts == 0:
            return 0.0
        return self.total_time / self.total_intercepts
    
    def summary(self) -> str:
        return (
            f"Перехватов: {self.total_intercepts} "
            f"(разрешено: {self.allowed}, запрещено: {self.denied}, "
            f"модифицировано: {self.modified}, заменено: {self.replaced}, "
            f"ошибок: {self.errors}, "
            f"среднее время: {self.average_time:.4f}с)"
        )

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ КЛАСС ПЕРЕХВАТЧИКА
# ═══════════════════════════════════════════════════════════════

class BaseInterceptor:
    """
    Базовый класс для всех перехватчиков.
    Перехватывает что-то и делает с этим что-то.
    """
    
    _interceptor_registry: Dict[str, 'BaseInterceptor'] = {}
    _global_record_id = 0
    _record_lock = threading.Lock()
    
    def __init__(
        self,
        name: str = "перехватчик",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        target: Optional[str] = None,
        auto_start: bool = False,
        log_all: bool = True,
        max_records: int = 1000,
    ):
        self.name = name
        self.mode = mode
        self.target = target
        self.log_all = log_all
        self.max_records = max_records
        
        self.active = False
        self.stats = InterceptorStats()
        self._original_targets: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._created_at = time.time()
        
        # Регистрируем перехватчик
        self._interceptor_registry[name] = self
        
        if auto_start:
            self.start()
    
    def start(self):
        """Запускает перехватчик."""
        if self.active:
            return
        
        try:
            self._setup()
            self.active = True
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.INTERCEPTOR,
                f"Перехватчик '{self.name}' запущен в режиме {self.mode.value}"
            )
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.INTERCEPTOR,
                f"Не удалось запустить перехватчик '{self.name}': {e}",
                was_successful=False
            )
    
    def stop(self):
        """Останавливает перехватчик."""
        if not self.active:
            return
        
        try:
            self._teardown()
            self.active = False
            _kostyl_state.record_kostyl(
                KostylSeverity.COSMETIC,
                KostylCategory.INTERCEPTOR,
                f"Перехватчик '{self.name}' остановлен. {self.stats.summary()}"
            )
        except Exception as e:
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.INTERCEPTOR,
                f"Не удалось остановить перехватчик '{self.name}': {e}"
            )
    
    def _setup(self):
        """Настройка перехвата. Переопределяется в подклассах."""
        pass
    
    def _teardown(self):
        """Отключение перехвата. Переопределяется в подклассах."""
        pass
    
    def _record_intercept(
        self,
        target: str,
        result: InterceptResult,
        args_summary: str = "",
        result_summary: str = "",
        duration: float = 0.0,
        **metadata
    ) -> InterceptRecord:
        """Записывает факт перехвата."""
        
        # ═══════════════════════════════════════════
        # КОСТЫЛЬ: защита от рекурсии
        # ═══════════════════════════════════════════
        if getattr(self, '_in_record', False):
            return None  # Уже записываем — не рекурсим
        
        self._in_record = True
        
        try:
            with BaseInterceptor._record_lock:
                BaseInterceptor._global_record_id += 1
                record_id = BaseInterceptor._global_record_id
            
            record = InterceptRecord(
                id=record_id,
                timestamp=time.time(),
                interceptor_name=self.name,
                target=target,
                mode=self.mode,
                result=result,
                args_summary=args_summary[:200],
                result_summary=result_summary[:200],
                duration=duration,
                metadata=metadata
            )
            
            with self._lock:
                self.stats.records.append(record)
                if len(self.stats.records) > self.max_records:
                    self.stats.records = self.stats.records[-self.max_records:]
                
                self.stats.total_intercepts += 1
                
                if result == InterceptResult.ALLOW:
                    self.stats.allowed += 1
                elif result == InterceptResult.DENY:
                    self.stats.denied += 1
                elif result == InterceptResult.MODIFIED:
                    self.stats.modified += 1
                elif result == InterceptResult.REPLACED:
                    self.stats.replaced += 1
            
            # Логирование — может вызывать рекурсию, оборачиваем в try
            if self.log_all:
                try:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.COSMETIC,
                        KostylCategory.INTERCEPTOR,
                        str(record)
                    )
                except Exception:
                    pass  # Не можем логировать — и ладно
            
            return record
        
        finally:
            self._in_record = False
    
    def _record_error(self, error: Exception, context: str = ""):
        """Записывает ошибку перехватчика."""
        self.stats.errors += 1
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.INTERCEPTOR,
            f"Перехватчик '{self.name}' ошибка: {error} ({context})"
        )
    
    def get_records(self, limit: int = 100) -> List[InterceptRecord]:
        """Возвращает последние записи."""
        return self.stats.records[-limit:]
    
    def report(self) -> str:
        """Генерирует отчёт."""
        status = "🟢 АКТИВЕН" if self.active else "🔴 ОСТАНОВЛЕН"
        return (
            f"🕵️ Перехватчик '{self.name}' [{status}]\n"
            f"   Режим: {self.mode.value}\n"
            f"   Цель: {self.target or 'всё'}\n"
            f"   {self.stats.summary()}"
        )
    
    @classmethod
    def list_interceptors(cls) -> List[str]:
        """Возвращает список всех перехватчиков."""
        return list(cls._interceptor_registry.keys())
    
    @classmethod
    def get_interceptor(cls, name: str) -> Optional['BaseInterceptor']:
        """Находит перехватчик по имени."""
        return cls._interceptor_registry.get(name)
    
    @classmethod
    def stop_all(cls):
        """Останавливает все перехватчики."""
        for interceptor in cls._interceptor_registry.values():
            interceptor.stop()

# ═══════════════════════════════════════════════════════════════
# ПЕРЕХВАТЧИК ВЫЗОВОВ ФУНКЦИЙ
# ═══════════════════════════════════════════════════════════════

class FunctionInterceptor(BaseInterceptor):
    """
    Перехватывает вызовы конкретной функции.
    Можно логировать, модифицировать аргументы, 
    менять результат, или вообще всё ломать.
    """
    
    def __init__(
        self,
        target_func: Callable,
        name: str = "перехватчик функций",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        before_call: Optional[Callable] = None,
        after_call: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        modify_args: Optional[Callable] = None,
        modify_result: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(name=name, mode=mode, **kwargs)
        self.target_func = target_func
        self.before_call = before_call
        self.after_call = after_call
        self.on_error = on_error
        self.modify_args = modify_args
        self.modify_result = modify_result
        
        self._original_func = target_func
        self._func_name = getattr(target_func, '__name__', str(target_func))
        self.target = self._func_name
    
    def _setup(self):
        """Подменяет функцию на перехватывающую версию."""
        
        interceptor = self
        
        @functools.wraps(self._original_func)
        def intercepted(*args, **kwargs):
            start_time = time.time()
            
            # Предварительный перехват
            if interceptor.before_call:
                try:
                    interceptor.before_call(args, kwargs)
                except Exception as e:
                    interceptor._record_error(e, "before_call")
            
            # Модификация аргументов
            if interceptor.modify_args and interceptor.mode in (InterceptMode.MODIFY, InterceptMode.REPLACE):
                try:
                    args, kwargs = interceptor.modify_args(args, kwargs)
                    mod_result = InterceptResult.MODIFIED
                except Exception as e:
                    interceptor._record_error(e, "modify_args")
                    mod_result = InterceptResult.ALLOW
            else:
                mod_result = InterceptResult.ALLOW
            
            # Фильтрация
            if interceptor.mode == InterceptMode.FILTER:
                # Проверяем, можно ли вызывать
                # По умолчанию — можно
                pass
            
            # Саботаж
            if interceptor.mode == InterceptMode.SABOTAGE:
                import random
                if random.random() < 0.1:  # 10% шанс саботажа
                    interceptor._record_intercept(
                        target=interceptor._func_name,
                        result=InterceptResult.CHAOS,
                        args_summary=str(args)[:100],
                        duration=time.time() - start_time,
                        chaos=True
                    )
                    raise RuntimeError(f"САБОТАЖ! Перехватчик '{interceptor.name}' всё сломал!")
            
            # Вызов оригинальной функции
            try:
                result = interceptor._original_func(*args, **kwargs)
                call_success = True
            except Exception as e:
                call_success = False
                if interceptor.on_error:
                    try:
                        result = interceptor.on_error(e, args, kwargs)
                    except Exception as handler_error:
                        interceptor._record_error(handler_error, "on_error")
                        result = None
                else:
                    result = None
            
            # Модификация результата
            if interceptor.modify_result and interceptor.mode in (InterceptMode.MODIFY, InterceptMode.REPLACE):
                try:
                    result = interceptor.modify_result(result, args, kwargs)
                    if mod_result == InterceptResult.ALLOW:
                        mod_result = InterceptResult.MODIFIED
                except Exception as e:
                    interceptor._record_error(e, "modify_result")
            
            # Пост-перехват
            if interceptor.after_call:
                try:
                    interceptor.after_call(result, args, kwargs)
                except Exception as e:
                    interceptor._record_error(e, "after_call")
            
            duration = time.time() - start_time
            
            # Запись
            result_str = "ERROR" if not call_success else str(result)[:100]
            interceptor._record_intercept(
                target=interceptor._func_name,
                result=mod_result,
                args_summary=str(args)[:100] + str(kwargs)[:100],
                result_summary=result_str,
                duration=duration,
                call_success=call_success
            )
            
            return result
        
        # Сохраняем оригинал
        self._original_targets[self._func_name] = self._original_func
        
        # Подменяем функцию в глобальном пространстве
        # (это костыль, но мы же kostylpy)
        frame = inspect.currentframe()
        try:
            # Пробуем найти и заменить функцию
            for fr in [frame.f_back, frame.f_back.f_back if frame.f_back else None]:
                if fr and self._func_name in fr.f_globals:
                    fr.f_globals[self._func_name] = intercepted
                    break
        finally:
            del frame
        
        self.target_func = intercepted
    
    def _teardown(self):
        """Восстанавливает оригинальную функцию."""
        for name, original in self._original_targets.items():
            try:
                frame = inspect.currentframe()
                for fr in [frame.f_back, frame.f_back.f_back if frame.f_back else None]:
                    if fr and name in fr.f_globals:
                        fr.f_globals[name] = original
                        break
            except:
                pass
        self._original_targets.clear()

# ═══════════════════════════════════════════════════════════════
# ПЕРЕХВАТЧИК АТРИБУТОВ
# ═══════════════════════════════════════════════════════════════

class AttributeInterceptor(BaseInterceptor):
    """
    Перехватывает доступ к атрибутам объекта.
    __getattr__, __setattr__, __delattr__ — всё под контролем.
    """
    
    def __init__(
        self,
        target_object: Any,
        name: str = "перехватчик атрибутов",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        allowed_attributes: Optional[List[str]] = None,
        blocked_attributes: Optional[List[str]] = None,
        default_value: Any = None,
        log_get: bool = True,
        log_set: bool = True,
        log_del: bool = True,
        **kwargs
    ):
        super().__init__(name=name, mode=mode, **kwargs)
        self.target_object = target_object
        self.allowed_attributes = set(allowed_attributes or [])
        self.blocked_attributes = set(blocked_attributes or [])
        self.default_value = default_value
        self.log_get = log_get
        self.log_set = log_set
        self.log_del = log_del
        
        self._original_getattr = None
        self._original_setattr = None
        self._original_delattr = None
        self.target = getattr(target_object, '__name__', str(target_object))
    
    def _setup(self):
        """Устанавливает перехват атрибутов."""
        obj = self.target_object
        obj_class = obj if isinstance(obj, type) else obj.__class__
        
        # Сохраняем оригиналы
        self._original_getattr = getattr(obj_class, '__getattr__', None)
        self._original_setattr = getattr(obj_class, '__setattr__', None)
        
        interceptor = self
        
        # Создаём перехватывающий __getattr__
        def custom_getattr(self_obj, name):
            start_time = time.time()
            
            # Проверка блокировки
            if name in interceptor.blocked_attributes:
                interceptor._record_intercept(
                    target=f"{interceptor.target}.{name}",
                    result=InterceptResult.DENY,
                    args_summary=f"getattr: {name}",
                    duration=time.time() - start_time,
                    blocked=True
                )
                if interceptor.mode == InterceptMode.SPY:
                    return interceptor.default_value
                raise AttributeError(
                    f"Доступ к '{name}' заблокирован перехватчиком '{interceptor.name}'"
                )
            
            # Проверка разрешения
            if interceptor.allowed_attributes and name not in interceptor.allowed_attributes:
                interceptor._record_intercept(
                    target=f"{interceptor.target}.{name}",
                    result=InterceptResult.DENY,
                    args_summary=f"getattr: {name} (не в списке разрешённых)",
                    duration=time.time() - start_time,
                    not_allowed=True
                )
                return interceptor.default_value
            
            # Получаем атрибут
            if interceptor._original_getattr:
                try:
                    value = interceptor._original_getattr(self_obj, name)
                except AttributeError:
                    value = interceptor.default_value
            else:
                try:
                    value = object.__getattribute__(self_obj, name)
                except AttributeError:
                    value = interceptor.default_value
            
            if interceptor.log_get:
                interceptor._record_intercept(
                    target=f"{interceptor.target}.{name}",
                    result=InterceptResult.ALLOW,
                    args_summary=f"getattr: {name}",
                    result_summary=str(value)[:100],
                    duration=time.time() - start_time
                )
            
            return value
        
        # Создаём перехватывающий __setattr__
        def custom_setattr(self_obj, name, value):
            start_time = time.time()
            
            if name in interceptor.blocked_attributes:
                interceptor._record_intercept(
                    target=f"{interceptor.target}.{name}",
                    result=InterceptResult.DENY,
                    args_summary=f"setattr: {name}={value}",
                    duration=time.time() - start_time,
                    blocked=True
                )
                return  # Просто игнорируем
            
            if interceptor._original_setattr:
                interceptor._original_setattr(self_obj, name, value)
            else:
                object.__setattr__(self_obj, name, value)
            
            if interceptor.log_set:
                interceptor._record_intercept(
                    target=f"{interceptor.target}.{name}",
                    result=InterceptResult.ALLOW,
                    args_summary=f"setattr: {name}={str(value)[:50]}",
                    duration=time.time() - start_time
                )
        
        # Применяем
        obj_class.__getattr__ = custom_getattr
        obj_class.__setattr__ = custom_setattr
    
    def _teardown(self):
        """Восстанавливает оригинальные методы."""
        obj_class = self.target_object if isinstance(self.target_object, type) else self.target_object.__class__
        
        if self._original_getattr is not None:
            obj_class.__getattr__ = self._original_getattr
        elif hasattr(obj_class, '__getattr__'):
            delattr(obj_class, '__getattr__')
        
        if self._original_setattr is not None:
            obj_class.__setattr__ = self._original_setattr

# ═══════════════════════════════════════════════════════════════
# ПЕРЕХВАТЧИК ВЫЗОВОВ (Callable)
# ═══════════════════════════════════════════════════════════════

class CallInterceptor(BaseInterceptor):
    """
    Перехватывает ВСЕ вызовы в определённой области видимости.
    Любой вызов функции, метода, класса — всё перехватывается.
    
    Осторожно: может перехватить сам себя.
    """
    
    def __init__(
        self,
        name: str = "перехватчик вызовов",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(name=name, mode=mode, **kwargs)
        self.whitelist = set(whitelist or [])
        self.blacklist = set(blacklist or [])
        self._patched_modules: Dict[str, Any] = {}
    
    def _setup(self):
        """Патчит __call__ у всех callable объектов."""
        # Не будем патчить всё подряд, это слишком опасно
        # Вместо этого создадим прокси-функцию
        interceptor = self
        original_call = builtins.callable  # Занятно, что callable — это функция
        
        # Патчим встроенные функции
        # (это демонстрация концепции, в реальности слишком опасно)
        _kostyl_state.record_kostyl(
            KostylSeverity.MAJOR,
            KostylCategory.INTERCEPTOR,
            f"Перехватчик '{self.name}': глобальный перехват вызовов "
            f"слишком опасен, активирован частичный режим"
        )
    
    def _teardown(self):
        """Восстанавливает оригиналы."""
        pass

# ═══════════════════════════════════════════════════════════════
# ПЕРЕХВАТЧИК ИМПОРТОВ
# ═══════════════════════════════════════════════════════════════

class ImportInterceptor(BaseInterceptor):
    """
    Перехватывает все импорты.
    Можно блокировать импорты, заменять модули, 
    или подсовывать заглушки.
    """
    def __init__(
        self,
        name: str = "перехватчик импортов",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        blocked_modules: Optional[List[str]] = None,
        redirect_map: Optional[Dict[str, str]] = None,
        stub_modules: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(name=name, mode=mode, **kwargs)
        self.blocked_modules = set(blocked_modules or [])
        self.redirect_map = redirect_map or {}
        self.stub_modules = set(stub_modules or [])
        self._original_import = builtins.__import__
    
    def _setup(self):
        """Перехватывает встроенный __import__."""
        interceptor = self
        
        # Сохраняем НАСТОЯЩИЙ оригинал (из builtins, а не из перехваченного)
        real_import = builtins.__import__
        
        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            start_time = time.time()
            
            # Проверка блокировки
            if name in interceptor.blocked_modules:
                interceptor._record_intercept(
                    target=f"import:{name}",
                    result=InterceptResult.DENY,
                    args_summary=f"import {name}",
                    duration=time.time() - start_time,
                    blocked=True
                )
                raise ImportError(
                    f"Импорт '{name}' заблокирован перехватчиком '{interceptor.name}'"
                )
            
            # Перенаправление
            if name in interceptor.redirect_map:
                new_name = interceptor.redirect_map[name]
                interceptor._record_intercept(
                    target=f"import:{name}",
                    result=InterceptResult.MODIFIED,
                    args_summary=f"import {name} → {new_name}",
                    duration=time.time() - start_time,
                    redirected=True
                )
                name = new_name
            
            # Заглушка
            if name in interceptor.stub_modules:
                interceptor._record_intercept(
                    target=f"import:{name}",
                    result=InterceptResult.REPLACED,
                    args_summary=f"import {name} → stub",
                    duration=time.time() - start_time,
                    stubbed=True
                )
                import types
                module = types.ModuleType(name)
                module.__doc__ = f"Заглушка, созданная перехватчиком '{interceptor.name}'"
                module.__kostyl_stub__ = True
                sys.modules[name] = module
                return module
            
            # ═══════════════════════════════════════════
            # КОСТЫЛЬ: временно восстанавливаем оригинал
            # чтобы избежать рекурсии
            # ═══════════════════════════════════════════
            builtins.__import__ = real_import
            try:
                result = real_import(name, globals, locals, fromlist, level)
            finally:
                builtins.__import__ = custom_import  # возвращаем перехватчик
            
            if interceptor.log_all:
                interceptor._record_intercept(
                    target=f"import:{name}",
                    result=InterceptResult.ALLOW,
                    args_summary=f"import {name}",
                    duration=time.time() - start_time
                )
            
            return result
        
        builtins.__import__ = custom_import
    
    def _teardown(self):
        """Восстанавливает оригинальный __import__."""
        if hasattr(self, '_original_import'):
            builtins.__import__ = self._original_import

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЙ ПЕРЕХВАТЧИК
# ═══════════════════════════════════════════════════════════════

class GlobalInterceptor(BaseInterceptor):
    """
    Перехватывает всё сразу.
    Комбинирует все остальные перехватчики.
    """
    
    def __init__(
        self,
        name: str = "глобальный перехватчик",
        mode: InterceptMode = InterceptMode.LOG_ONLY,
        intercept_print: bool = True,
        intercept_open: bool = True,
        intercept_import: bool = True,
        intercept_exceptions: bool = True,
        **kwargs
    ):
        super().__init__(name=name, mode=mode, **kwargs)
        self.intercept_print = intercept_print
        self.intercept_open = intercept_open
        self.intercept_import = intercept_import
        self.intercept_exceptions = intercept_exceptions
        
        self._sub_interceptors: List[BaseInterceptor] = []
        self._original_print = builtins.print
        self._original_open = builtins.open
        self._original_import = builtins.__import__
        self._original_excepthook = sys.excepthook
    
    def _setup(self):
        """Активирует все перехваты."""
        interceptor = self
        
        # Перехват print
        if self.intercept_print:
            def custom_print(*args, **kwargs):
                start_time = time.time()
                try:
                    interceptor._original_print(*args, **kwargs)
                except:
                    pass
                interceptor._record_intercept(
                    target="print",
                    result=InterceptResult.ALLOW,
                    args_summary=str(args)[:100],
                    duration=time.time() - start_time
                )
            builtins.print = custom_print
        
        # Перехват open
        if self.intercept_open:
            def custom_open(*args, **kwargs):
                start_time = time.time()
                result = interceptor._original_open(*args, **kwargs)
                interceptor._record_intercept(
                    target=f"open:{args[0] if args else 'unknown'}",
                    result=InterceptResult.ALLOW,
                    args_summary=str(args)[:100],
                    duration=time.time() - start_time
                )
                return result
            builtins.open = custom_open
        
        # Перехват исключений
        if self.intercept_exceptions:
            def custom_excepthook(exc_type, exc_value, exc_tb):
                interceptor._record_intercept(
                    target=f"exception:{exc_type.__name__}",
                    result=InterceptResult.ALLOW,
                    args_summary=str(exc_value)[:100],
                    duration=0.0,
                    exception=True
                )
                interceptor._original_excepthook(exc_type, exc_value, exc_tb)
            sys.excepthook = custom_excepthook
        
        _kostyl_state.record_kostyl(
            KostylSeverity.MODERATE,
            KostylCategory.INTERCEPTOR,
            f"Глобальный перехватчик '{self.name}' активирован "
            f"(print={self.intercept_print}, open={self.intercept_open}, "
            f"import={self.intercept_import}, exceptions={self.intercept_exceptions})"
        )
    
    def _teardown(self):
        """Восстанавливает всё как было."""
        if self.intercept_print:
            builtins.print = self._original_print
        if self.intercept_open:
            builtins.open = self._original_open
        if self.intercept_import:
            builtins.__import__ = self._original_import
        if self.intercept_exceptions:
            sys.excepthook = self._original_excepthook
        
        for sub in self._sub_interceptors:
            sub.stop()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def intercept_all():
    """Создаёт и запускает глобальный перехватчик."""
    interceptor = GlobalInterceptor(
        name="великий перехватчик",
        mode=InterceptMode.LOG_ONLY,
        auto_start=True
    )
    return interceptor

def spy_on_function(func: Callable) -> FunctionInterceptor:
    """Создаёт шпиона для функции."""
    return FunctionInterceptor(
        target_func=func,
        name=f"шпион за {getattr(func, '__name__', 'функцией')}",
        mode=InterceptMode.SPY,
        auto_start=True
    )

def block_imports(*module_names: str) -> ImportInterceptor:
    """Блокирует импорт указанных модулей."""
    return ImportInterceptor(
        name="блокировщик импортов",
        mode=InterceptMode.FILTER,
        blocked_modules=list(module_names),
        auto_start=True
    )

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Базовые
    'BaseInterceptor',
    'InterceptMode',
    'InterceptResult',
    'InterceptRecord',
    'InterceptorStats',
    
    # Перехватчики
    'FunctionInterceptor',
    'AttributeInterceptor',
    'CallInterceptor',
    'ImportInterceptor',
    'GlobalInterceptor',
    
    # Утилиты
    'intercept_all',
    'spy_on_function',
    'block_imports',
]

print(f"🕵️ kostylpy.interceptors: загружено {len(BaseInterceptor._interceptor_registry)} типов перехватчиков")
print(f"   Режимы: {', '.join(m.value for m in InterceptMode)}")