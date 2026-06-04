"""
Интеграционные тесты kostylpy.
Проверяют совместную работу всех модулей.
Не дублирует модульные тесты.
"""

import sys
import os
import time
import unittest
import tempfile
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import kostylpy
    from kostylpy import (
        safe, retry, fallback,
        KostylContext, kostyl_block,
        safe_get, safe_set, safe_divide,
        DotDict, SafeList,
    )
    from kostylpy.core import KostylPy, CoreStatus
    from kostylpy.constants import Emoji, KOSTYLPY_VERSION
    KOSTYLPY_LOADED = True
except ImportError as e:
    print(f"⚠️ kostylpy не загружен в интеграционных тестах: {e}")
    KOSTYLPY_LOADED = False


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestFullPipeline(unittest.TestCase):
    """Полный сквозной тест: все модули вместе."""
    
    def test_decorator_validator_utils_together(self):
        """Декоратор + валидатор + утилиты — всё вместе."""
        from kostylpy.validators import TypeValidator, RangeValidator
        
        # Создаём валидатор
        validator = TypeValidator(int)
        
        # Создаём функцию с декоратором
        @safe(fallback=0)
        def process_value(x):
            result = validator.validate(x)
            if not result.is_valid:
                raise ValueError(f"Невалидное значение: {x}")
            return x * 2
        
        # Нормальная работа
        self.assertEqual(process_value(50), 100)
        
        # С ошибкой — fallback
        self.assertEqual(process_value("не число"), 0)
    
    def test_safe_operations_chain(self):
        """Цепочка безопасных операций."""
        data = DotDict({'a': {'b': 10}, 'c': {'d': 0}})
        
        # Безопасно получаем значения
        numerator = safe_get(data, 'a.b', default=0)
        denominator = safe_get(data, 'c.d', default=1)
        
        # Безопасно делим
        result = safe_divide(numerator, denominator, default=-1)
        
        self.assertEqual(result, -1)  # Деление на ноль → default
    
    def test_kostyl_context_with_nested_operations(self):
        """Контекст + вложенные операции."""
        
        results = []
        
        with KostylContext("интеграционный тест"):
            # Внутри контекста делаем что-то опасное
            data = DotDict({'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25},
            ]})
            
            # Безопасный доступ
            name1 = safe_get(data, 'users.0.name', 'unknown')
            name2 = safe_get(data, 'users.1.name', 'unknown')
            name3 = safe_get(data, 'users.99.name', 'unknown')
            
            results = [name1, name2, name3]
        
        self.assertEqual(results[0], 'Alice')
        self.assertEqual(results[1], 'Bob')
        self.assertEqual(results[2], 'unknown')
    
    def test_multiple_kostyl_contexts(self):
        """Несколько вложенных контекстов."""
        
        with KostylContext("внешний"):
            with KostylContext("внутренний"):
                raise ValueError("Ошибка!")
            
            # После внутреннего контекста мы должны быть живы
            self.assertTrue(True)
        
        # После внешнего тоже
        self.assertTrue(True)
    
    def test_retry_with_context(self):
        """retry + контекстный менеджер."""
        attempts = []
        
        @retry(max_attempts=3, delay=0.01, fallback="fallback_value")
        def flaky_operation():
            attempts.append(1)
            with KostylContext("внутри flaky"):
                if len(attempts) < 2:
                    raise ValueError("Ещё нет")
                return "готово"
        
        result = flaky_operation()
        self.assertEqual(result, "готово")
        self.assertEqual(len(attempts), 2)


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestCoreIntegration(unittest.TestCase):
    """Интеграция с ядром."""
    
    def test_core_has_all_modules(self):
        """Ядро должно содержать все основные модули."""
        core = KostylPy()
        modules = core.loaded_modules()
        
        expected = ['config', 'logger', 'metrics', 'utils', 'decorators',
                    'context_managers', 'exceptions', 'factories',
                    'validators', 'interceptors']
        
        for module in expected:
            self.assertIn(module, modules, f"Модуль {module} не загружен")
    
    def test_core_health_all_green(self):
        """Все компоненты должны быть здоровы."""
        core = KostylPy()
        health = core.health_check()
        
        for component, status in health.items():
            self.assertTrue(status, f"Компонент {component} нездоров")
    
    def test_core_global_access(self):
        """Глобальные объекты должны быть доступны."""
        import kostylpy
        
        # config
        self.assertIsNotNone(kostylpy.kostylpy.config)
        
        # metrics
        self.assertIsNotNone(kostylpy.kostylpy.metrics)
    
    def test_version_consistency(self):
        """Версия должна быть одинакова везде."""
        from kostylpy.constants import KOSTYLPY_VERSION as VER1
        
        self.assertEqual(KOSTYLPY_VERSION, VER1)


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestFileSystemIntegration(unittest.TestCase):
    """Интеграция с файловой системой."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_safe_file_operations(self):
        """Безопасные операции с файлами."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        # Запись через safe утилиту
        from kostylpy.utils import safe_write_file
        self.assertTrue(safe_write_file(test_file, "Hello Kostyl!"))
        
        # Чтение через safe утилиту
        from kostylpy.utils import safe_read_file
        content = safe_read_file(test_file)
        self.assertEqual(content, "Hello Kostyl!")
        
        # Чтение несуществующего файла
        content = safe_read_file("/nonexistent/file.txt", default="DEFAULT")
        self.assertEqual(content, "DEFAULT")
    
    def test_patcher_with_file(self):
        """Патчер + работа с файлами."""
        from kostylpy.patcher import patch_string, SAFETY_FUNCTIONS
        
        source = "result = 100 / divisor"
        result = patch_string(source, add_safety=True)
        
        # Сохраняем патченный код
        test_file = os.path.join(self.temp_dir, "patched_test.py")
        with open(test_file, 'w') as f:
            f.write(SAFETY_FUNCTIONS + '\n' + result.patched_source)
        
        # Проверяем что файл создался
        self.assertTrue(os.path.exists(test_file))
        
        # Проверяем что компилируется
        with open(test_file, 'r') as f:
            code = f.read()
        
        try:
            compile(code, test_file, 'exec')
        except SyntaxError as e:
            self.fail(f"Сохранённый код не компилируется: {e}")


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestExceptionIntegration(unittest.TestCase):
    """Интеграция с исключениями."""
    
    def test_exception_in_safe_decorator(self):
        """Исключение внутри safe декоратора."""
        from kostylpy.exceptions import KostylException
        
        @safe(fallback=None)
        def raise_kostyl():
            raise KostylException("Костыльное исключение!")
        
        result = raise_kostyl()
        self.assertIsNone(result)
    
    def test_validation_error_in_context(self):
        """Ошибка валидации внутри контекста."""
        from kostylpy.validators import TypeValidator
        from kostylpy.exceptions import ValidationError
        
        validator = TypeValidator(int)
        
        with KostylContext("валидация"):
            result = validator.validate("не число")
            self.assertFalse(result.is_valid)
    
    def test_custom_exception_hierarchy(self):
        """Иерархия исключений."""
        from kostylpy.exceptions import (
            KostylException, ValidationError, 
            TypeValidationError, NullValidationError
        )
        
        # TypeValidationError — наследник ValidationError
        exc = TypeValidationError(expected="int", got="str")
        self.assertIsInstance(exc, ValidationError)
        self.assertIsInstance(exc, KostylException)
        
        # NullValidationError — тоже
        exc2 = NullValidationError()
        self.assertIsInstance(exc2, ValidationError)
        self.assertIsInstance(exc2, KostylException)


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestMetricsIntegration(unittest.TestCase):
    """Интеграция с метриками."""
    
    def test_metrics_record_operations(self):
        """Метрики должны записывать операции."""
        from kostylpy.metrics import metrics
        
        before = metrics.total_operations.get()
        
        # Имитируем операции
        metrics.record_operation(success=True, duration=0.1)
        metrics.record_operation(success=True, duration=0.2)
        metrics.record_operation(success=False, duration=0.3)
        
        after = metrics.total_operations.get()
        self.assertEqual(after - before, 3)
    
    def test_coffee_metrics(self):
        """Метрики кофе."""
        from kostylpy.metrics import metrics
        
        before = metrics.coffee.total_coffees
        
        metrics.coffee.drink(duration=300.0)
        
        after = metrics.coffee.total_coffees
        self.assertEqual(after - before, 1)
    
    def test_metrics_snapshot(self):
        """Снимок метрик."""
        from kostylpy.metrics import metrics
        
        snapshot = metrics.snapshot()
        
        self.assertIn('timestamp', snapshot)
        self.assertIn('uptime', snapshot)
        self.assertIn('metrics', snapshot)
        self.assertIn('summary', snapshot)


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestPrintOutput(unittest.TestCase):
    """Тесты вывода (интеграция с print)."""
    
    def test_safe_print_in_context(self):
        """Безопасный print в контексте."""
        f = io.StringIO()
        
        with redirect_stdout(f):
            with KostylContext("тест вывода"):
                print("Hello World!")
                print("Это тест")
        
        output = f.getvalue()
        self.assertIn("Hello World", output)
        self.assertIn("Это тест", output)
    
    def test_print_never_fails(self):
        """Print не должен падать никогда."""
        f = io.StringIO()
        
        with redirect_stdout(f):
            # Пробуем напечатать всё подряд
            print(None)
            print([])
            print({})
            print(lambda x: x)
            print(object())
        
        output = f.getvalue()
        self.assertGreater(len(output), 0)


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestAsyncIntegration(unittest.TestCase):
    """Интеграция с асинхронностью."""
    
    def test_async_module_loaded(self):
        """Асинхронный модуль должен быть загружен."""
        try:
            from kostylpy import async_kostyl
            self.assertTrue(True)
        except ImportError:
            self.fail("async_kostyl не загружен")
    
    def test_async_decorators_exist(self):
        """Асинхронные декораторы должны существовать."""
        from kostylpy.async_kostyl import (
            async_safe, async_retry, async_timeout
        )
        
        self.assertTrue(callable(async_safe))
        self.assertTrue(callable(async_retry))
        self.assertTrue(callable(async_timeout))


@unittest.skipUnless(KOSTYLPY_LOADED, "kostylpy не загружен")
class TestFinalBoss(unittest.TestCase):
    """Финальный босс: всё вместе и сразу."""
    
    def test_everything_together(self):
        """ВСЁ ВМЕСТЕ."""
        
        # Конфиг
        from kostylpy.config import config
        self.assertIsNotNone(config)
        
        # Логгер
        from kostylpy.logging_kostyl import logger
        self.assertIsNotNone(logger)
        
        # Метрики
        from kostylpy.metrics import metrics
        self.assertIsNotNone(metrics)
        
        # Декораторы
        @safe(fallback="всё ок")
        @retry(max_attempts=2, delay=0.01)
        def mega_function(x):
            if x < 0:
                raise ValueError("Отрицательное!")
            return x * 2
        
        self.assertEqual(mega_function(21), 42)
        self.assertEqual(mega_function(-1), "всё ок")
        
        # Контекст
        with KostylContext("мега тест"):
            data = DotDict({'deep': {'nested': {'value': 42}}})
            
            @safe(fallback=0)
            def get_deep(data, path):
                return safe_get(data, path, default=0)
            
            result = get_deep(data, 'deep.nested.value')
            self.assertEqual(result, 42)
        
        # Валидация
        from kostylpy.validators import StringValidator, RangeValidator
        
        str_val = StringValidator(min_length=3, max_length=10)
        range_val = RangeValidator(min_value=0, max_value=150)
        
        self.assertTrue(str_val.validate("hello").is_valid)
        self.assertTrue(range_val.validate(42).is_valid)
        
        # Утилиты
        from kostylpy.utils import DotDict, SafeList, chunk_list
        
        dd = DotDict({'a': 1, 'b': 2})
        sl = SafeList([1, 2, 3], default=0)
        chunks = chunk_list([1, 2, 3, 4, 5], 2)
        
        self.assertEqual(dd.a, 1)
        self.assertEqual(sl[100], 0)
        self.assertEqual(len(chunks), 3)
        
        # Всё работает!
        self.assertTrue(True)


if __name__ == '__main__':
    print(f"{Emoji.KOSTYL if KOSTYLPY_LOADED else '⚠️'} Запуск интеграционных тестов kostylpy...")
    print(f"Версия: {KOSTYLPY_VERSION if KOSTYLPY_LOADED else 'N/A'}")
    print(f"{'='*50}")
    unittest.main(verbosity=2)