"""
Фабрики kostylpy.
Потому что создавать объекты напрямую — это слишком просто.
Нужны фабрики, которые создают фабрики, которые создают фабрики...

Содержит:
- KostylFactory — базовая фабрика костылей
- ExceptionFactory — фабрика исключений (уже в exceptions.py, но здесь расширенная)
- DecoratorFactory — фабрика декораторов
- ResourceFactory — фабрика виртуальных ресурсов
- ConfigFactory — фабрика конфигураций
- StubFactory — фабрика заглушек
- RandomKostylFactory — фабрика случайных костылей
- MetaFactory — фабрика фабрик
"""

import sys
import time
import random
import threading
import inspect
import functools
import hashlib
import json
import uuid
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем состояние с защитой
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
        FACTORY = "factory"
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

class FactoryStatus(Enum):
    """Статус фабрики."""
    IDLE = "простаивает"
    WORKING = "работает"
    OVERLOADED = "перегружена"
    BROKEN = "сломана"
    FIXING_ITSELF = "чинит себя"
    PRODUCING_GARBAGE = "производит мусор"
    ON_STRIKE = "бастует"
    MYSTERY = "загадочный статус"

class ProductQuality(Enum):
    """Качество продукта фабрики."""
    PERFECT = ("ИДЕАЛЬНЫЙ", 100)
    GOOD = ("ХОРОШИЙ", 80)
    ACCEPTABLE = ("ПРИЕМЛЕМЫЙ", 60)
    KOSTYL = ("КОСТЫЛЬНЫЙ", 40)
    BARELY_WORKING = ("ЕЛЕ РАБОТАЕТ", 20)
    BROKEN = ("СЛОМАН", 0)
    DANGEROUS = ("ОПАСНЫЙ", -10)
    
    def __str__(self):
        return self.value[0]
    
    @property
    def score(self) -> int:
        return self.value[1]

@dataclass
class FactoryStats:
    """Статистика фабрики."""
    total_produced: int = 0
    total_failed: int = 0
    total_repaired: int = 0
    quality_scores: List[int] = field(default_factory=list)
    production_times: List[float] = field(default_factory=list)
    last_production_time: float = 0.0
    status_history: List[Tuple[float, FactoryStatus]] = field(default_factory=list)
    
    @property
    def average_quality(self) -> float:
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores) / len(self.quality_scores)
    
    @property
    def average_time(self) -> float:
        if not self.production_times:
            return 0.0
        return sum(self.production_times) / len(self.production_times)
    
    @property
    def success_rate(self) -> float:
        total = self.total_produced + self.total_failed
        if total == 0:
            return 100.0
        return (self.total_produced / total) * 100
    
    def summary(self) -> str:
        return (
            f"Произведено: {self.total_produced}, "
            f"Провалов: {self.total_failed}, "
            f"Успешность: {self.success_rate:.1f}%, "
            f"Среднее качество: {self.average_quality:.1f}/100, "
            f"Среднее время: {self.average_time:.4f}с"
        )

@dataclass
class FactoryProduct:
    """Продукт, произведённый фабрикой."""
    id: str
    type: str
    quality: ProductQuality
    created_at: float
    factory_name: str
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"<{self.type} #{self.id[:8]} [{self.quality}]>"
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'quality': self.quality.name,
            'created_at': self.created_at,
            'factory_name': self.factory_name,
            'metadata': self.metadata,
        }

# ═══════════════════════════════════════════════════════════════
# АБСТРАКТНАЯ ФАБРИКА
# ═══════════════════════════════════════════════════════════════

class AbstractKostylFactory(ABC):
    """
    Абстрактная фабрика костылей.
    Все фабрики должны наследоваться от неё.
    Но некоторые не будут, потому что это костыли.
    """
    
    _factory_registry: Dict[str, 'AbstractKostylFactory'] = {}
    _registry_lock = threading.Lock()
    
    def __init__(
        self,
        name: str = "безымянная фабрика",
        max_products: int = 1000,
        quality_threshold: ProductQuality = ProductQuality.ACCEPTABLE,
        auto_repair: bool = True,
        log_production: bool = True,
    ):
        self.name = name
        self.max_products = max_products
        self.quality_threshold = quality_threshold
        self.auto_repair = auto_repair
        self.log_production = log_production
        
        self.status = FactoryStatus.IDLE
        self.stats = FactoryStats()
        self._products: List[FactoryProduct] = []
        self._lock = threading.Lock()
        self._created_at = time.time()
        self._id = str(uuid.uuid4())[:8]
        self._broken = False
        
        # Регистрируем фабрику
        with self._registry_lock:
            self._factory_registry[name] = self
        
        self._update_status(FactoryStatus.IDLE)
    
    def _update_status(self, new_status: FactoryStatus):
        """Обновляет статус фабрики."""
        self.status = new_status
        self.stats.status_history.append((time.time(), new_status))
    
    def _check_broken(self):
        """Проверяет, не сломана ли фабрика."""
        if self._broken:
            if self.auto_repair:
                self._repair()
            else:
                raise RuntimeError(f"Фабрика '{self.name}' сломана и не чинится!")
    
    def _repair(self):
        """Чинит фабрику."""
        self._update_status(FactoryStatus.FIXING_ITSELF)
        time.sleep(random.uniform(0.01, 0.1))
        self._broken = False
        self.stats.total_repaired += 1
        self._update_status(FactoryStatus.IDLE)
        _kostyl_state.record_kostyl(
            KostylSeverity.MINOR,
            KostylCategory.FACTORY,
            f"Фабрика '{self.name}' починена (попытка #{self.stats.total_repaired})"
        )
    
    def _maybe_break(self):
        """Случайно ломает фабрику (для реализма)."""
        if random.random() < 0.01:  # 1% шанс поломки
            self._broken = True
            self._update_status(FactoryStatus.BROKEN)
            _kostyl_state.record_kostyl(
                KostylSeverity.MAJOR,
                KostylCategory.FACTORY,
                f"Фабрика '{self.name}' СЛОМАЛАСЬ!"
            )
    
    @abstractmethod
    def produce(self, *args, **kwargs) -> FactoryProduct:
        """Производит продукт. Должен быть переопределён."""
        pass
    
    def get_product(self, product_id: str) -> Optional[FactoryProduct]:
        """Находит продукт по ID."""
        for product in self._products:
            if product.id == product_id:
                return product
        return None
    
    def get_all_products(self) -> List[FactoryProduct]:
        """Возвращает все продукты."""
        return self._products.copy()
    
    def get_products_by_quality(self, min_quality: ProductQuality) -> List[FactoryProduct]:
        """Возвращает продукты с качеством не ниже указанного."""
        return [p for p in self._products if p.quality.score >= min_quality.score]
    
    def clear_products(self):
        """Очищает все продукты."""
        self._products.clear()
        _kostyl_state.record_kostyl(
            KostylSeverity.COSMETIC,
            KostylCategory.FACTORY,
            f"Фабрика '{self.name}': продукты очищены"
        )
    
    def report(self) -> str:
        """Генерирует отчёт о работе фабрики."""
        return (
            f"🏭 Фабрика '{self.name}' (#{self._id})\n"
            f"   Статус: {self.status.value}\n"
            f"   Продуктов: {len(self._products)}\n"
            f"   {self.stats.summary()}\n"
            f"   Возраст: {time.time() - self._created_at:.1f}с"
        )
    
    @classmethod
    def get_factory(cls, name: str) -> Optional['AbstractKostylFactory']:
        """Находит фабрику по имени."""
        return cls._factory_registry.get(name)
    
    @classmethod
    def list_factories(cls) -> List[str]:
        """Возвращает список всех фабрик."""
        return list(cls._factory_registry.keys())
    
    @classmethod
    def global_report(cls) -> str:
        """Генерирует отчёт обо всех фабриках."""
        report = "=" * 60 + "\n"
        report += "🏭 ОТЧЁТ О ВСЕХ ФАБРИКАХ KOSTYLPY\n"
        report += "=" * 60 + "\n"
        for name, factory in cls._factory_registry.items():
            report += f"\n{factory.report()}\n"
        report += "=" * 60
        return report

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА ИСКЛЮЧЕНИЙ
# ═══════════════════════════════════════════════════════════════

class ExceptionFactory(AbstractKostylFactory):
    """
    Фабрика для создания исключений.
    Может создавать исключения по коду, по типу, случайные,
    и даже исключения для исключений.
    """
    
    def __init__(
        self,
        name: str = "фабрика исключений",
        default_severity: Any = KostylSeverity.MODERATE,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.default_severity = default_severity
        self._exception_classes: Dict[str, Type[Exception]] = {}
        self._register_builtin_exceptions()
    
    def _register_builtin_exceptions(self):
        """Регистрирует встроенные типы исключений."""
        builtins = [
            'Exception', 'ValueError', 'TypeError', 'KeyError',
            'IndexError', 'AttributeError', 'RuntimeError',
            'ImportError', 'FileNotFoundError', 'ZeroDivisionError',
            'OverflowError', 'MemoryError', 'RecursionError',
            'AssertionError', 'NotImplementedError', 'StopIteration',
        ]
        for name in builtins:
            exc_type = getattr(__builtins__, name, None)
            if exc_type:
                self._exception_classes[name] = exc_type
    
    def register_exception(self, name: str, exc_class: Type[Exception]):
        """Регистрирует новый тип исключения."""
        self._exception_classes[name] = exc_class
    
    def produce(
        self,
        exception_type: Union[str, Type[Exception]] = "Exception",
        message: str = "",
        severity: Optional[Any] = None,
        **kwargs
    ) -> FactoryProduct:
        """Производит исключение."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            # Определяем класс исключения
            if isinstance(exception_type, str):
                exc_class = self._exception_classes.get(
                    exception_type, Exception
                )
            elif isinstance(exception_type, type):
                exc_class = exception_type
            else:
                exc_class = Exception
            
            # Создаём сообщение если не указано
            if not message:
                message = self._generate_message(exc_class)
            
            # Создаём исключение
            exception = exc_class(message, **kwargs)
            
            # Определяем качество
            quality = self._assess_quality(exc_class, message)
            
            product = FactoryProduct(
                id=str(uuid.uuid4()),
                type=f"Exception:{exc_class.__name__}",
                quality=quality,
                created_at=time.time(),
                factory_name=self.name,
                data=exception,
                metadata={
                    'exception_type': exc_class.__name__,
                    'message': message,
                    'severity': str(severity or self.default_severity),
                }
            )
            
            with self._lock:
                self._products.append(product)
                if len(self._products) > self.max_products:
                    self._products = self._products[-self.max_products:]
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(quality.score)
            production_time = time.time() - start_time
            self.stats.production_times.append(production_time)
            self.stats.last_production_time = production_time
            
            if self.log_production:
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.FACTORY,
                    f"Фабрика '{self.name}': создано исключение {exc_class.__name__} [{quality}]"
                )
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            # Создаём исключение о том что не смогли создать исключение
            raise RuntimeError(
                f"Фабрика '{self.name}' не смогла создать исключение: {e}"
            )
    
    def _generate_message(self, exc_class: Type[Exception]) -> str:
        """Генерирует сообщение для исключения."""
        messages = [
            f"Что-то пошло не так в {exc_class.__name__}",
            f"Ошибка типа {exc_class.__name__}",
            f"Костыль не выдержал: {exc_class.__name__}",
            f"Неожиданное исключение: {exc_class.__name__}",
            f"Всё сломалось: {exc_class.__name__}",
        ]
        return random.choice(messages)
    
    def _assess_quality(
        self, exc_class: Type[Exception], message: str
    ) -> ProductQuality:
        """Оценивает качество созданного исключения."""
        score = 50
        
        # Хорошие имена классов
        good_names = ['Error', 'Exception']
        for name in good_names:
            if name in exc_class.__name__:
                score += 10
        
        # Длинные сообщения — лучше
        if len(message) > 20:
            score += 10
        if len(message) > 50:
            score += 10
        
        # Случайный фактор
        score += random.randint(-20, 20)
        
        # Определяем качество
        for quality in ProductQuality:
            if score >= quality.score:
                return quality
        return ProductQuality.BROKEN
    
    def produce_random(self) -> FactoryProduct:
        """Создаёт случайное исключение."""
        exc_name = random.choice(list(self._exception_classes.keys()))
        return self.produce(exception_type=exc_name)
    
    def produce_chain(self, count: int = 3) -> List[FactoryProduct]:
        """Создаёт цепочку исключений (причина → следствие)."""
        products = []
        for i in range(count):
            message = f"Исключение #{i+1} в цепочке"
            if products:
                message += f" (из-за: {products[-1].type})"
            product = self.produce(message=message)
            products.append(product)
        return products

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА ДЕКОРАТОРОВ
# ═══════════════════════════════════════════════════════════════

class DecoratorFactory(AbstractKostylFactory):
    """
    Фабрика для создания декораторов.
    Создаёт декораторы на лету с разными параметрами.
    """
    
    def __init__(self, name: str = "фабрика декораторов", **kwargs):
        super().__init__(name=name, **kwargs)
        self._decorator_templates: Dict[str, Callable] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Регистрирует стандартные шаблоны декораторов."""
        
        # Простой декоратор-заглушка
        def stub_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        self._decorator_templates['stub'] = stub_decorator
        
        # Декоратор логирования
        def log_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.FACTORY,
                    f"Вызвана функция '{func.__name__}'"
                )
                return result
            return wrapper
        self._decorator_templates['log'] = log_decorator
        
        # Декоратор замера времени
        def timer_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.FACTORY,
                    f"Функция '{func.__name__}' выполнена за {elapsed:.4f}с"
                )
                return result
            return wrapper
        self._decorator_templates['timer'] = timer_decorator
    
    def register_template(self, name: str, template: Callable):
        """Регистрирует новый шаблон декоратора."""
        self._decorator_templates[name] = template
    
    def produce(
        self,
        template_name: str = "stub",
        name: Optional[str] = None,
        **kwargs
    ) -> FactoryProduct:
        """Производит декоратор."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            template = self._decorator_templates.get(
                template_name,
                self._decorator_templates['stub']
            )
            
            # Оборачиваем в дополнительную логику если нужно
            decorator = template
            
            if kwargs.get('safe', False):
                original = decorator
                def safe_version(func):
                    decorated = original(func)
                    @functools.wraps(func)
                    def wrapper(*a, **kw):
                        try:
                            return decorated(*a, **kw)
                        except Exception as e:
                            _kostyl_state.record_kostyl(
                                KostylSeverity.MINOR,
                                KostylCategory.FACTORY,
                                f"Декоратор поймал ошибку в '{func.__name__}': {e}"
                            )
                            return kwargs.get('fallback')
                    return wrapper
                decorator = safe_version
            
            quality = ProductQuality.GOOD if template_name != 'stub' else ProductQuality.ACCEPTABLE
            
            product = FactoryProduct(
                id=str(uuid.uuid4()),
                type=f"Decorator:{template_name}",
                quality=quality,
                created_at=time.time(),
                factory_name=self.name,
                data=decorator,
                metadata={
                    'template': template_name,
                    'name': name or f"decorator_{template_name}",
                }
            )
            
            with self._lock:
                self._products.append(product)
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(quality.score)
            production_time = time.time() - start_time
            self.stats.production_times.append(production_time)
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            raise RuntimeError(f"Фабрика '{self.name}' не смогла создать декоратор: {e}")
    
    def produce_chain(
        self, template_names: List[str]
    ) -> FactoryProduct:
        """Создаёт цепочку декораторов."""
        decorators = []
        for name in template_names:
            product = self.produce(template_name=name)
            decorators.append(product.data)
        
        # Комбинируем декораторы
        def combined_decorator(func):
            for dec in reversed(decorators):
                func = dec(func)
            return func
        
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type=f"DecoratorChain:{'+'.join(template_names)}",
            quality=ProductQuality.GOOD,
            created_at=time.time(),
            factory_name=self.name,
            data=combined_decorator,
            metadata={'chain': template_names}
        )

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА ЗАГЛУШЕК
# ═══════════════════════════════════════════════════════════════

class StubFactory(AbstractKostylFactory):
    """
    Фабрика для создания заглушек.
    Создаёт объекты-заглушки для чего угодно.
    """
    
    def __init__(self, name: str = "фабрика заглушек", **kwargs):
        super().__init__(name=name, **kwargs)
    
    def produce(
        self,
        stub_type: str = "object",
        name: str = "",
        methods: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        return_value: Any = None,
        raise_error: Optional[type] = None,
    ) -> FactoryProduct:
        """Производит заглушку."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            stub_name = name or f"Stub_{stub_type}_{random.randint(1000, 9999)}"
            
            if stub_type == "function":
                stub = self._create_function_stub(stub_name, return_value, raise_error)
            elif stub_type == "class":
                stub = self._create_class_stub(stub_name, methods, attributes)
            elif stub_type == "module":
                stub = self._create_module_stub(stub_name, methods, attributes)
            elif stub_type == "object":
                stub = self._create_object_stub(stub_name, methods, attributes)
            else:
                stub = self._create_generic_stub(stub_name)
            
            # Применяем атрибуты
            if attributes:
                for key, value in attributes.items():
                    setattr(stub, key, value)
            
            quality = ProductQuality.ACCEPTABLE
            if methods and len(methods) > 5:
                quality = ProductQuality.GOOD
            
            product = FactoryProduct(
                id=str(uuid.uuid4()),
                type=f"Stub:{stub_type}",
                quality=quality,
                created_at=time.time(),
                factory_name=self.name,
                data=stub,
                metadata={
                    'stub_type': stub_type,
                    'name': stub_name,
                    'methods': methods or [],
                    'has_attributes': attributes is not None,
                }
            )
            
            with self._lock:
                self._products.append(product)
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(quality.score)
            self.stats.production_times.append(time.time() - start_time)
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            raise RuntimeError(f"Фабрика '{self.name}' не смогла создать заглушку: {e}")
    
    def _create_function_stub(
        self, name: str, return_value: Any, raise_error: Optional[type]
    ) -> Callable:
        """Создаёт функцию-заглушку."""
        def stub_function(*args, **kwargs):
            if raise_error:
                raise raise_error(f"Заглушка '{name}' вызвала ошибку")
            return return_value
        
        stub_function.__name__ = name
        stub_function.__doc__ = f"Заглушка, созданная kostylpy StubFactory"
        stub_function._is_stub = True
        return stub_function
    
    def _create_class_stub(
        self, name: str, methods: Optional[List[str]], attributes: Optional[Dict]
    ) -> type:
        """Создаёт класс-заглушку."""
        class StubClass:
            _is_stub = True
            
            def __init__(self, *args, **kwargs):
                pass
            
            def __getattr__(self, item):
                return lambda *args, **kwargs: None
            
            def __str__(self):
                return f"<Stub:{name}>"
            
            def __repr__(self):
                return f"<Stub:{name}>"
            
            def __bool__(self):
                return False
            
            def __len__(self):
                return 0
        
        StubClass.__name__ = name
        StubClass.__doc__ = f"Класс-заглушка, созданный kostylpy"
        
        # Добавляем методы
        if methods:
            for method_name in methods:
                setattr(StubClass, method_name, lambda *a, **kw: None)
        
        return StubClass
    
    def _create_module_stub(
        self, name: str, methods: Optional[List[str]], attributes: Optional[Dict]
    ):
        """Создаёт модуль-заглушку."""
        import types
        
        module = types.ModuleType(name)
        module.__doc__ = f"Модуль-заглушка, созданный kostylpy"
        module._is_stub = True
        
        # Добавляем базовые атрибуты
        module.__version__ = "0.0.1-stub"
        module.__author__ = "kostylpy StubFactory"
        
        # Добавляем указанные методы как функции
        if methods:
            for method_name in methods:
                setattr(module, method_name, lambda *a, **kw: None)
        
        return module
    
    def _create_object_stub(
        self, name: str, methods: Optional[List[str]], attributes: Optional[Dict]
    ):
        """Создаёт объект-заглушку."""
        class GenericStub:
            _is_stub = True
            
            def __getattr__(self, item):
                return lambda *args, **kwargs: None
            
            def __str__(self):
                return f"<StubObject:{name}>"
        
        stub = GenericStub()
        
        if methods:
            for method_name in methods:
                setattr(stub, method_name, lambda *a, **kw: None)
        
        return stub
    
    def _create_generic_stub(self, name: str):
        """Создаёт универсальную заглушку."""
        return self._create_object_stub(name, [], {})

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА КОНФИГУРАЦИЙ
# ═══════════════════════════════════════════════════════════════

class ConfigFactory(AbstractKostylFactory):
    """
    Фабрика для создания конфигураций.
    Создаёт конфиги с разумными (нет) значениями по умолчанию.
    """
    
    def __init__(self, name: str = "фабрика конфигураций", **kwargs):
        super().__init__(name=name, **kwargs)
        self._config_templates: Dict[str, Dict] = {}
        self._register_default_configs()
    
    def _register_default_configs(self):
        """Регистрирует стандартные шаблоны конфигов."""
        
        self._config_templates['default'] = {
            'debug': False,
            'verbose': False,
            'log_level': 'INFO',
            'max_retries': 3,
            'timeout': 30.0,
        }
        
        self._config_templates['web_server'] = {
            'host': '0.0.0.0',
            'port': 8080,
            'workers': 1,
            'timeout': 60,
            'max_connections': 100,
            'enable_ssl': False,
        }
        
        self._config_templates['database'] = {
            'host': 'localhost',
            'port': 5432,
            'user': 'admin',
            'password': 'admin',  # Безопасность на уровне костыля
            'database': 'kostyl_db',
            'pool_size': 5,
        }
        
        self._config_templates['kostylpy'] = {
            'version': '3.0.0',
            'panic_threshold': 42,
            'coffee_required': True,
            'auto_fix': True,
            'log_all': True,
            'monkey_patch_everything': True,
        }
    
    def register_template(self, name: str, template: Dict):
        """Регистрирует шаблон конфига."""
        self._config_templates[name] = template
    
    def produce(
        self,
        template_name: str = "default",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> FactoryProduct:
        """Производит конфигурацию."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            template = self._config_templates.get(
                template_name,
                self._config_templates['default']
            )
            
            # Создаём конфиг на основе шаблона
            config = template.copy()
            
            # Применяем переопределения
            if overrides:
                config.update(overrides)
            
            # Добавляем метаданные
            config['_created_by'] = 'kostylpy ConfigFactory'
            config['_template'] = template_name
            config['_created_at'] = time.time()
            
            quality = ProductQuality.GOOD
            if 'password' in config and config.get('password') == 'admin':
                quality = ProductQuality.DANGEROUS
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.FACTORY,
                    f"Конфиг '{template_name}' содержит небезопасный пароль!"
                )
            
            product = FactoryProduct(
                id=str(uuid.uuid4()),
                type=f"Config:{template_name}",
                quality=quality,
                created_at=time.time(),
                factory_name=self.name,
                data=config,
                metadata={
                    'template': template_name,
                    'keys': list(config.keys()),
                    'overrides': list(overrides.keys()) if overrides else [],
                }
            )
            
            with self._lock:
                self._products.append(product)
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(quality.score)
            self.stats.production_times.append(time.time() - start_time)
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            raise RuntimeError(f"Фабрика '{self.name}' не смогла создать конфиг: {e}")
    
    def produce_from_file(self, filepath: str) -> FactoryProduct:
        """Создаёт конфиг из JSON файла (с костылями)."""
        config = {}
        try:
            import json
            with open(filepath, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {'_warning': f'Файл {filepath} не найден, использован default'}
            _kostyl_state.record_kostyl(
                KostylSeverity.MODERATE,
                KostylCategory.FACTORY,
                f"Файл конфига не найден: {filepath}"
            )
        except json.JSONDecodeError:
            config = {'_warning': f'Файл {filepath} повреждён, использован default'}
        
        return self.produce(
            template_name="default",
            overrides=config
        )

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА СЛУЧАЙНЫХ КОСТЫЛЕЙ
# ═══════════════════════════════════════════════════════════════

class RandomKostylFactory(AbstractKostylFactory):
    """
    Фабрика, которая создаёт случайные костыли.
    Никто не знает, что она произведёт в следующий раз.
    """
    
    def __init__(self, name: str = "фабрика случайных костылей", **kwargs):
        super().__init__(name=name, **kwargs)
        self._chaos_level = 5
        self._production_history: List[str] = []
    
    @property
    def chaos_level(self) -> int:
        return self._chaos_level
    
    @chaos_level.setter
    def chaos_level(self, value: int):
        self._chaos_level = max(1, min(10, value))
    
    def produce(self, *args, **kwargs) -> FactoryProduct:
        """Производит СЛУЧАЙНЫЙ костыль."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            # Выбираем случайный тип продукта
            product_types = [
                self._produce_random_string,
                self._produce_random_number,
                self._produce_random_boolean,
                self._produce_random_list,
                self._produce_random_dict,
                self._produce_random_none,
                self._produce_random_error,
                self._produce_random_stub,
                self._produce_random_uuid,
                self._produce_random_hash,
            ]
            
            # Чем выше хаос, тем больше странных продуктов
            if self._chaos_level > 7:
                product_types.extend([
                    self._produce_random_nonsense,
                    self._produce_random_recursion,
                ])
            
            producer = random.choice(product_types)
            product = producer()
            
            # Добавляем хаос
            if random.random() < self._chaos_level / 100:
                product.quality = random.choice(list(ProductQuality))
                product.metadata['chaos'] = True
                product.metadata['chaos_level'] = self._chaos_level
            
            self._production_history.append(product.type)
            
            with self._lock:
                self._products.append(product)
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(product.quality.score)
            self.stats.production_times.append(time.time() - start_time)
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            # Даже ошибка создания случайного костыля — это случайный костыль
            return FactoryProduct(
                id=str(uuid.uuid4()),
                type="Chaos:Error",
                quality=ProductQuality.BROKEN,
                created_at=time.time(),
                factory_name=self.name,
                data=e,
                metadata={'error': str(e)}
            )
    
    def _produce_random_string(self) -> FactoryProduct:
        strings = ["Hello Kostyl!", "42", "undefined", "null", "Все сломано"]
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="RandomString",
            quality=ProductQuality.ACCEPTABLE,
            created_at=time.time(),
            factory_name=self.name,
            data=random.choice(strings)
        )
    
    def _produce_random_number(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="RandomNumber",
            quality=ProductQuality.GOOD,
            created_at=time.time(),
            factory_name=self.name,
            data=random.randint(-999999, 999999)
        )
    
    def _produce_random_boolean(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="RandomBoolean",
            quality=ProductQuality.GOOD,
            created_at=time.time(),
            factory_name=self.name,
            data=random.choice([True, False])
        )
    
    def _produce_random_list(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="RandomList",
            quality=ProductQuality.ACCEPTABLE,
            created_at=time.time(),
            factory_name=self.name,
            data=[random.randint(0, 100) for _ in range(random.randint(0, 10))]
        )
    
    def _produce_random_dict(self) -> FactoryProduct:
        keys = ['key', 'value', 'data', 'result', 'error', 'kostyl']
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="RandomDict",
            quality=ProductQuality.ACCEPTABLE,
            created_at=time.time(),
            factory_name=self.name,
            data={k: random.randint(0, 100) for k in random.sample(keys, 3)}
        )
    
    def _produce_random_none(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="None",
            quality=ProductQuality.BARELY_WORKING,
            created_at=time.time(),
            factory_name=self.name,
            data=None,
            metadata={'warning': 'Это None. Зачем вы это создали?'}
        )
    
    def _produce_random_error(self) -> FactoryProduct:
        errors = [ValueError("случайная ошибка"), TypeError("не тот тип"), 
                  RuntimeError("всё сломалось"), KeyError("нет ключа")]
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="Error",
            quality=ProductQuality.DANGEROUS,
            created_at=time.time(),
            factory_name=self.name,
            data=random.choice(errors),
            metadata={'warning': 'Это исключение!'}
        )
    
    def _produce_random_stub(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="Stub",
            quality=ProductQuality.KOSTYL,
            created_at=time.time(),
            factory_name=self.name,
            data=type('Stub', (), {'__str__': lambda s: '<RandomStub>'})()
        )
    
    def _produce_random_uuid(self) -> FactoryProduct:
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="UUID",
            quality=ProductQuality.GOOD,
            created_at=time.time(),
            factory_name=self.name,
            data=str(uuid.uuid4())
        )
    
    def _produce_random_hash(self) -> FactoryProduct:
        data = str(random.random()).encode()
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="Hash",
            quality=ProductQuality.GOOD,
            created_at=time.time(),
            factory_name=self.name,
            data=hashlib.sha256(data).hexdigest()[:16]
        )
    
    def _produce_random_nonsense(self) -> FactoryProduct:
        nonsense = type('Nonsense', (), {
            '__str__': lambda s: 'Бессмысленный объект',
            '__bool__': lambda s: random.choice([True, False]),
            '__len__': lambda s: random.randint(-10, 100),
        })()
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="Nonsense",
            quality=ProductQuality.BROKEN,
            created_at=time.time(),
            factory_name=self.name,
            data=nonsense,
            metadata={'warning': 'Этот объект не имеет смысла'}
        )
    
    def _produce_random_recursion(self) -> FactoryProduct:
        recursive = []
        recursive.append(recursive)
        return FactoryProduct(
            id=str(uuid.uuid4()),
            type="Recursion",
            quality=ProductQuality.DANGEROUS,
            created_at=time.time(),
            factory_name=self.name,
            data=recursive,
            metadata={'warning': 'Бесконечная рекурсия!'}
        )

# ═══════════════════════════════════════════════════════════════
# МЕТА-ФАБРИКА (ФАБРИКА ФАБРИК)
# ═══════════════════════════════════════════════════════════════

class MetaFactory(AbstractKostylFactory):
    """
    Фабрика, которая создаёт другие фабрики.
    Потому что создавать фабрики вручную — недостаточно костыльно.
    """
    
    def __init__(self, name: str = "мета-фабрика", **kwargs):
        super().__init__(name=name, **kwargs)
        self._factory_types: Dict[str, Type[AbstractKostylFactory]] = {
            'exception': ExceptionFactory,
            'decorator': DecoratorFactory,
            'stub': StubFactory,
            'config': ConfigFactory,
            'random': RandomKostylFactory,
        }
    
    def register_factory_type(self, name: str, factory_class: Type[AbstractKostylFactory]):
        """Регистрирует новый тип фабрики."""
        self._factory_types[name] = factory_class
    
    def produce(
        self,
        factory_type: str = "exception",
        name: Optional[str] = None,
        **kwargs
    ) -> FactoryProduct:
        """Производит фабрику."""
        self._check_broken()
        self._update_status(FactoryStatus.WORKING)
        start_time = time.time()
        
        try:
            factory_class = self._factory_types.get(factory_type)
            if factory_class is None:
                factory_class = AbstractKostylFactory
            
            factory_name = name or f"{factory_type}_factory_{random.randint(100, 999)}"
            factory_instance = factory_class(name=factory_name, **kwargs)
            
            product = FactoryProduct(
                id=str(uuid.uuid4()),
                type=f"Factory:{factory_type}",
                quality=ProductQuality.PERFECT if factory_type != 'random' else ProductQuality.ACCEPTABLE,
                created_at=time.time(),
                factory_name=self.name,
                data=factory_instance,
                metadata={
                    'factory_type': factory_type,
                    'factory_name': factory_name,
                    'factory_class': factory_class.__name__,
                }
            )
            
            with self._lock:
                self._products.append(product)
            
            self.stats.total_produced += 1
            self.stats.quality_scores.append(product.quality.score)
            self.stats.production_times.append(time.time() - start_time)
            
            if self.log_production:
                _kostyl_state.record_kostyl(
                    KostylSeverity.COSMETIC,
                    KostylCategory.FACTORY,
                    f"Мета-фабрика создала фабрику: '{factory_name}' типа '{factory_type}'"
                )
            
            self._maybe_break()
            self._update_status(FactoryStatus.IDLE)
            return product
            
        except Exception as e:
            self.stats.total_failed += 1
            self._update_status(FactoryStatus.IDLE)
            raise RuntimeError(f"Мета-фабрика не смогла создать фабрику: {e}")
    
    def produce_all_types(self) -> List[FactoryProduct]:
        """Создаёт по одной фабрике каждого типа."""
        products = []
        for factory_type in self._factory_types:
            try:
                product = self.produce(factory_type=factory_type)
                products.append(product)
            except Exception as e:
                _kostyl_state.record_kostyl(
                    KostylSeverity.MAJOR,
                    KostylCategory.FACTORY,
                    f"Не удалось создать фабрику типа '{factory_type}': {e}"
                )
        return products
    
    def produce_meta_chain(self, depth: int = 3) -> List[FactoryProduct]:
        """
        Создаёт цепочку: мета-фабрика → фабрика → продукт.
        """
        chain = []
        
        # Создаём фабрику
        factory_product = self.produce(factory_type='random', name='chain_factory')
        chain.append(factory_product)
        
        # Фабрика создаёт продукты
        for i in range(depth - 1):
            try:
                sub_product = factory_product.data.produce()
                chain.append(sub_product)
            except Exception as e:
                break
        
        return chain

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def create_all_factories() -> Dict[str, AbstractKostylFactory]:
    """Создаёт все стандартные фабрики."""
    factories = {}
    
    factories['exception'] = ExceptionFactory(name="главная фабрика исключений")
    factories['decorator'] = DecoratorFactory(name="главная фабрика декораторов")
    factories['stub'] = StubFactory(name="главная фабрика заглушек")
    factories['config'] = ConfigFactory(name="главная фабрика конфигураций")
    factories['random'] = RandomKostylFactory(name="фабрика хаоса")
    factories['meta'] = MetaFactory(name="мета-фабрика")
    
    return factories

# Создаём глобальные фабрики при импорте
_global_factories = create_all_factories()

def get_factory(name: str) -> Optional[AbstractKostylFactory]:
    """Получает глобальную фабрику по имени."""
    return _global_factories.get(name)

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Базовые
    'AbstractKostylFactory',
    'FactoryProduct',
    'FactoryStats',
    'FactoryStatus',
    'ProductQuality',
    
    # Фабрики
    'ExceptionFactory',
    'DecoratorFactory',
    'StubFactory',
    'ConfigFactory',
    'RandomKostylFactory',
    'MetaFactory',
    
    # Утилиты
    'create_all_factories',
    'get_factory',
    '_global_factories',
]

print(f"🏭 kostylpy.factories: загружено {len(_global_factories)} фабрик")
for name, factory in _global_factories.items():
    print(f"   • {name}: {factory.__class__.__name__}")