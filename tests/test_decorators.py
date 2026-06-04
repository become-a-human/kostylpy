"""
Тесты декораторов kostylpy.
Проверяют safe, retry, fallback, cached, deprecated_kostyl,
log_execution, kostyl_method, monkey_patch и все их фичи.
"""

import sys
import os
import time
import unittest
import warnings
import threading
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import kostylpy
    from kostylpy.decorators import (
        safe, retry, fallback, cached,
        deprecated_kostyl, log_execution,
        kostyl_method, monkey_patch,
        all_decorators, DecoratorStats
    )
    DECORATORS_LOADED = True
except ImportError as e:
    print(f"⚠️ decorators не загружены: {e}")
    DECORATORS_LOADED = False


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ safe
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestSafeDecorator(unittest.TestCase):
    """Тесты декоратора safe."""
    
    def test_safe_returns_result(self):
        """safe должен возвращать результат функции."""
        @safe(fallback=0)
        def add(a, b):
            return a + b
        
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_safe_catches_exception(self):
        """safe должен ловить исключения."""
        @safe(fallback="fallback_value")
        def failing():
            raise ValueError("Ошибка!")
        
        self.assertEqual(failing(), "fallback_value")
    
    def test_safe_without_args(self):
        """safe без аргументов должен работать как pass-through."""
        @safe
        def func():
            return 42
        
        self.assertEqual(func(), 42)
    
    def test_safe_without_args_catches(self):
        """safe без аргументов должен ловить ошибки (default=None)."""
        @safe
        def failing():
            raise RuntimeError("Ошибка")
        
        self.assertIsNone(failing())
    
    def test_safe_with_args(self):
        """safe с именованными аргументами."""
        @safe(default="DEFAULT", log_errors=False)
        def risky():
            raise ValueError("Риск!")
        
        self.assertEqual(risky(), "DEFAULT")
    
    def test_safe_preserves_name(self):
        """safe должен сохранять имя функции."""
        @safe(fallback=None)
        def my_function():
            pass
        
        self.assertEqual(my_function.__name__, "my_function")
    
    def test_safe_preserves_docstring(self):
        """safe должен сохранять документацию."""
        @safe(fallback=None)
        def documented():
            """Это документация."""
            pass
        
        self.assertEqual(documented.__doc__, "Это документация.")
    
    def test_safe_preserves_module(self):
        """safe должен сохранять модуль."""
        @safe(fallback=None)
        def func():
            pass
        
        self.assertEqual(func.__module__, __name__)
    
    def test_safe_with_reraise_true(self):
        """safe с reraise=True должен пробрасывать исключения."""
        @safe(fallback=None, reraise=True)
        def failing():
            raise ValueError("Пробрасываем")
        
        with self.assertRaises(ValueError):
            failing()
    
    def test_safe_with_reraise_specific(self):
        """safe с reraise=[TypeError] должен пробрасывать только TypeError."""
        @safe(fallback=None, reraise=[TypeError])
        def mixed_errors(x):
            if x == 1:
                raise TypeError("Type")
            elif x == 2:
                raise ValueError("Value")
            return x * 2
        
        # TypeError должен пробрасываться
        with self.assertRaises(TypeError):
            mixed_errors(1)
        
        # ValueError должен подавляться
        self.assertIsNone(mixed_errors(2))
        
        # Нормальный вызов
        self.assertEqual(mixed_errors(10), 20)
    
    def test_safe_with_on_error(self):
        """safe с on_error колбеком."""
        errors = []
        
        def error_handler(exc, args, kwargs, caller_info):
            errors.append((type(exc).__name__, str(exc)))
        
        @safe(fallback="ERROR", on_error=error_handler)
        def failing(x):
            raise ValueError(f"Ошибка с x={x}")
        
        result = failing(42)
        
        self.assertEqual(result, "ERROR")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "ValueError")
        self.assertIn("x=42", errors[0][1])
    
    def test_safe_with_max_failures(self):
        """safe с max_failures должен сдаваться после N ошибок."""
        failure_count = [0]
        
        @safe(fallback=None, max_failures=3)
        def always_fails():
            failure_count[0] += 1
            raise ValueError("Падаю!")
        
        # Первые 3 раза — fallback
        for _ in range(3):
            self.assertIsNone(always_fails())
        
        # 4-й раз — пробрасывает исключение
        with self.assertRaises(ValueError):
            always_fails()
    
    def test_safe_stats(self):
        """safe должен иметь статистику."""
        @safe(fallback=None)
        def func(x):
            if x < 0:
                raise ValueError()
            return x * 2
        
        func(10)
        func(-1)
        func(20)
        
        self.assertTrue(hasattr(func, '_kostyl_safe'))
        self.assertTrue(hasattr(func, '_kostyl_stats'))
        self.assertTrue(hasattr(func, 'get_stats'))
        
        stats_str = func.get_stats()
        self.assertIn("Вызовов", stats_str)
        self.assertIn("успешно", stats_str)
    
    def test_safe_reset_stats(self):
        """safe должен сбрасывать статистику."""
        @safe(fallback=None)
        def func(x):
            return x
        
        func(1)
        func(2)
        
        self.assertTrue(hasattr(func, 'reset_stats'))
        func.reset_stats()
        
        stats_str = func.get_stats()
        self.assertIn("Вызовов: 0", stats_str)
    
    def test_safe_thread_safety(self):
        """safe должен работать в многопоточной среде."""
        results = []
        
        @safe(fallback="thread_error")
        def thread_func(x):
            if x < 0:
                raise ValueError()
            return x * 2
        
        def run_thread():
            for i in range(10):
                results.append(thread_func(i - 5))
        
        threads = [threading.Thread(target=run_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(results), 50)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ retry
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestRetryDecorator(unittest.TestCase):
    """Тесты декоратора retry."""
    
    def test_retry_success_first_try(self):
        """retry должен вернуть результат с первой попытки."""
        @retry(max_attempts=3, delay=0.01)
        def works():
            return "ok"
        
        self.assertEqual(works(), "ok")
    
    def test_retry_after_failures(self):
        """retry должен повторять после ошибок."""
        attempts = []
        
        @retry(max_attempts=5, delay=0.01)
        def flaky():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Ещё нет")
            return "готово"
        
        result = flaky()
        self.assertEqual(result, "готово")
        self.assertEqual(len(attempts), 3)
    
    def test_retry_fallback(self):
        """retry должен возвращать fallback после всех попыток."""
        @retry(max_attempts=2, delay=0.01, fallback="запасное")
        def always_fails():
            raise RuntimeError("Всегда падает")
        
        self.assertEqual(always_fails(), "запасное")
    
    def test_retry_specific_exceptions(self):
        """retry должен ловить только указанные исключения."""
        @retry(max_attempts=3, delay=0.01, exceptions=ValueError, fallback="ok")
        def raises_type_error():
            raise TypeError("Не тот тип")
        
        with self.assertRaises(TypeError):
            raises_type_error()
    
    def test_retry_specific_exceptions_tuple(self):
        """retry с кортежем исключений."""
        @retry(max_attempts=3, delay=0.01, 
               exceptions=(ValueError, TypeError), fallback="caught")
        def raises_either(x):
            if x == 1:
                raise ValueError()
            elif x == 2:
                raise TypeError()
            return "success"
        
        self.assertEqual(raises_either(1), "caught")
        self.assertEqual(raises_either(2), "caught")
        self.assertEqual(raises_either(3), "success")
    
    def test_retry_with_delay(self):
        """retry должен иметь задержку между попытками."""
        start = time.time()
        
        @retry(max_attempts=3, delay=0.05, backoff=2.0, jitter=False, fallback="timeout")
        def fails():
            raise Exception()
        
        fails()
        elapsed = time.time() - start
        
        # Две задержки: 0.05 + 0.10 = 0.15 (без jitter)
        self.assertGreater(elapsed, 0.1)
    
    def test_retry_with_jitter(self):
        """retry с jitter должен добавлять случайность."""
        delays = []
        
        @retry(max_attempts=3, delay=0.05, jitter=True, fallback="ok")
        def fails():
            raise Exception()
        
        for _ in range(5):
            start = time.time()
            fails()
            delays.append(time.time() - start)
        
        # С jitter задержки должны немного различаться
        self.assertGreater(max(delays) - min(delays), 0.001)
    
    def test_retry_with_on_retry(self):
        """retry с on_retry колбеком."""
        retry_info = []
        
        def on_retry_handler(attempt, exception, delay):
            retry_info.append((attempt, type(exception).__name__, delay))
        
        @retry(max_attempts=3, delay=0.01, on_retry=on_retry_handler, fallback="ok")
        def fails():
            raise ValueError("Ошибка")
        
        fails()
        
        self.assertEqual(len(retry_info), 2)  # Два повтора
        self.assertEqual(retry_info[0][1], "ValueError")
        self.assertEqual(retry_info[1][0], 2)  # Вторая попытка
    
    def test_retry_stats(self):
        """retry должен иметь статистику."""
        @retry(max_attempts=3, delay=0.01)
        def works():
            return 42
        
        works()
        
        self.assertTrue(hasattr(works, '_kostyl_retry'))
        self.assertTrue(hasattr(works, '_kostyl_stats'))
        self.assertTrue(hasattr(works, 'get_stats'))
    
    def test_retry_preserves_name(self):
        """retry должен сохранять имя функции."""
        @retry(max_attempts=3)
        def my_retry_func():
            return True
        
        self.assertEqual(my_retry_func.__name__, "my_retry_func")
    
    def test_retry_zero_attempts(self):
        """retry с 0 попыток должен сразу вернуть fallback."""
        @retry(max_attempts=0, fallback="immediate")
        def never_called():
            raise Exception()
        
        # max_attempts=0 означает 0 попыток
        # но в реализации это минимум 1 попытка
        # тестируем что не падает
        result = never_called()
        self.assertEqual(result, "immediate")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ fallback
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestFallbackDecorator(unittest.TestCase):
    """Тесты декоратора fallback."""
    
    def test_fallback_returns_value(self):
        """fallback должен возвращать запасное значение."""
        @fallback(42)
        def failing():
            raise Exception()
        
        self.assertEqual(failing(), 42)
    
    def test_fallback_passes_result(self):
        """fallback должен возвращать результат при успехе."""
        @fallback(0)
        def works(x):
            return x * 2
        
        self.assertEqual(works(10), 20)
    
    def test_fallback_any_type(self):
        """fallback должен работать с любыми типами."""
        @fallback({"status": "error", "code": 500})
        def api_call():
            raise ConnectionError()
        
        result = api_call()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], 500)
    
    def test_fallback_none(self):
        """fallback с None."""
        @fallback(None)
        def failing():
            raise Exception()
        
        self.assertIsNone(failing())
    
    def test_fallback_complex_object(self):
        """fallback со сложным объектом."""
        default_list = [1, 2, 3, 4, 5]
        
        @fallback(default_list)
        def failing():
            raise Exception()
        
        result = failing()
        self.assertEqual(result, default_list)
        self.assertIs(result, default_list)  # Тот же объект
    
    def test_fallback_specific_exceptions(self):
        """fallback с указанием исключений."""
        @fallback("caught", exceptions=ValueError)
        def picky(x):
            if x == 1:
                raise ValueError("Поймано")
            elif x == 2:
                raise TypeError("Не поймано")
            return "ok"
        
        self.assertEqual(picky(1), "caught")
        
        with self.assertRaises(TypeError):
            picky(2)
        
        self.assertEqual(picky(3), "ok")
    
    def test_fallback_no_log(self):
        """fallback с log=False не должен логировать."""
        @fallback("silent", log=False)
        def failing():
            raise Exception()
        
        # Просто проверяем что не падает
        result = failing()
        self.assertEqual(result, "silent")
    
    def test_fallback_preserves_metadata(self):
        """fallback должен сохранять метаданные."""
        @fallback("test")
        def func():
            pass
        
        self.assertTrue(hasattr(func, '_kostyl_fallback'))
        self.assertTrue(hasattr(func, '_kostyl_fallback_value'))
        self.assertTrue(hasattr(func, '_kostyl_original'))


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ cached
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestCachedDecorator(unittest.TestCase):
    """Тесты декоратора cached."""
    
    def test_cached_caches_result(self):
        """cached должен кешировать результат."""
        call_count = [0]
        
        @cached()
        def expensive(x):
            call_count[0] += 1
            time.sleep(0.01)
            return x * 2
        
        self.assertEqual(expensive(5), 10)
        self.assertEqual(expensive(5), 10)
        self.assertEqual(call_count[0], 1)  # Вызвана только один раз
    
    def test_cached_different_args(self):
        """cached должен различать аргументы."""
        call_count = [0]
        
        @cached()
        def compute(x):
            call_count[0] += 1
            return x * x
        
        compute(2)
        compute(3)
        compute(2)
        
        self.assertEqual(call_count[0], 2)  # 2 и 3 — разные
    
    def test_cached_kwargs(self):
        """cached должен учитывать keyword аргументы."""
        call_count = [0]
        
        @cached()
        def func(a, b=10):
            call_count[0] += 1
            return a + b
        
        func(1)
        func(1, b=10)
        func(1, b=20)
        func(1, b=10)
        
        # (1, b=10) — дважды, (1, b=20) — один раз = 2 уникальных
        self.assertEqual(call_count[0], 2)
    
    def test_cached_clear(self):
        """cached должен поддерживать очистку кеша."""
        call_count = [0]
        
        @cached()
        def func(x):
            call_count[0] += 1
            return x
        
        func(1)
        func.clear_cache()
        func(1)
        
        self.assertEqual(call_count[0], 2)
    
    def test_cached_cache_info(self):
        """cached должен показывать информацию о кеше."""
        @cached(max_size=100)
        def func(x):
            return x
        
        func(1)
        func(2)
        func(3)
        
        self.assertTrue(hasattr(func, 'cache_info'))
        info = func.cache_info()
        self.assertIn("3/100", info)
    
    def test_cached_max_size(self):
        """cached должен очищаться при превышении размера."""
        call_count = [0]
        
        @cached(max_size=3)
        def func(x):
            call_count[0] += 1
            return x
        
        # Заполняем кеш
        for i in range(5):
            func(i)
        
        # Кеш должен был очиститься при превышении
        # Проверяем что функция всё ещё работает
        result = func(100)
        self.assertEqual(result, 100)
    
    def test_cached_ttl(self):
        """cached с TTL должен устаревать."""
        call_count = [0]
        
        @cached(ttl=0.1)  # 100ms TTL
        def func(x):
            call_count[0] += 1
            return x
        
        func(1)
        self.assertEqual(call_count[0], 1)
        
        # Сразу — из кеша
        func(1)
        self.assertEqual(call_count[0], 1)
        
        # Ждём истечения TTL
        time.sleep(0.15)
        
        func(1)
        self.assertEqual(call_count[0], 2)  # Промах кеша
    
    def test_cached_unhashable_args(self):
        """cached с нехешируемыми аргументами не должен падать."""
        call_count = [0]
        
        @cached()
        def func(x):
            call_count[0] += 1
            return str(x)
        
        # Списки не хешируются, но функция не должна падать
        result1 = func([1, 2, 3])
        result2 = func([1, 2, 3])
        
        self.assertEqual(result1, result2)
        # Не кешируется, но и не падает
        self.assertGreater(call_count[0], 0)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ deprecated_kostyl
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestDeprecatedDecorator(unittest.TestCase):
    """Тесты декоратора deprecated_kostyl."""
    
    def test_deprecated_warns(self):
        """deprecated_kostyl должен выводить предупреждение."""
        @deprecated_kostyl(reason="старое", alternative="новое")
        def old_func():
            return "old"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()
            
            self.assertEqual(result, "old")
            self.assertTrue(len(w) > 0)
            self.assertIn("устарела", str(w[0].message))
    
    def test_deprecated_still_works(self):
        """deprecated_kostyl не должен менять поведение."""
        @deprecated_kostyl(reason="старое", alternative="новое")
        def add(a, b):
            return a + b
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(add(2, 3), 5)
    
    def test_deprecated_warning_message(self):
        """Сообщение должно содержать причину и альтернативу."""
        @deprecated_kostyl(reason="устаревший API", alternative="new_api()")
        def old_api():
            pass
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_api()
            
            msg = str(w[0].message)
            self.assertIn("устаревший API", msg)
            self.assertIn("new_api()", msg)
    
    def test_deprecated_preserves_function(self):
        """deprecated_kostyl должен сохранять функцию."""
        @deprecated_kostyl(reason="test")
        def func(x, y, z=10):
            """Docstring."""
            return x + y + z
        
        self.assertEqual(func.__name__, "func")
        self.assertEqual(func.__doc__, "Docstring.")
        self.assertEqual(func(1, 2, 3), 6)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ log_execution
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestLogExecutionDecorator(unittest.TestCase):
    """Тесты декоратора log_execution."""
    
    def test_log_execution_calls_function(self):
        """log_execution должен вызывать функцию."""
        @log_execution(level="DEBUG")
        def func(x):
            return x * 2
        
        self.assertEqual(func(21), 42)
    
    def test_log_execution_preserves_name(self):
        """log_execution должен сохранять имя."""
        @log_execution()
        def my_func():
            pass
        
        self.assertEqual(my_func.__name__, "my_func")
    
    def test_log_execution_logs_args(self):
        """log_execution должен логировать аргументы."""
        @log_execution(level="DEBUG", log_args=True)
        def func(a, b):
            return a + b
        
        # Не падает
        result = func(1, 2)
        self.assertEqual(result, 3)
    
    def test_log_execution_logs_result(self):
        """log_execution должен логировать результат."""
        @log_execution(level="DEBUG", log_result=True)
        def func(x):
            return x * 10
        
        result = func(5)
        self.assertEqual(result, 50)
    
    def test_log_execution_logs_time(self):
        """log_execution должен логировать время."""
        @log_execution(level="DEBUG", log_time=True)
        def func():
            time.sleep(0.01)
            return "done"
        
        result = func()
        self.assertEqual(result, "done")
    
    def test_log_execution_with_error(self):
        """log_execution должен логировать ошибки."""
        @log_execution(level="ERROR")
        def failing():
            raise ValueError("Тест")
        
        with self.assertRaises(ValueError):
            failing()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ kostyl_method
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestKostylMethod(unittest.TestCase):
    """Тесты декоратора kostyl_method."""
    
    def test_kostyl_method_works(self):
        """kostyl_method должен работать."""
        @kostyl_method(safe_mode=True, retry_mode=False)
        def compute(x, y):
            return x / y
        
        result = compute(10, 2)
        self.assertEqual(result, 5)
    
    def test_kostyl_method_safe(self):
        """kostyl_method с safe_mode должен быть безопасным."""
        @kostyl_method(safe_mode=True, retry_mode=False, fallback_value=-1)
        def divide(a, b):
            return a / b
        
        self.assertEqual(divide(1, 0), -1)
    
    def test_kostyl_method_retry(self):
        """kostyl_method с retry должен повторять."""
        attempts = []
        
        @kostyl_method(safe_mode=True, retry_mode=True, 
                      max_attempts=3, fallback_value=0)
        def flaky():
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError()
            return 42
        
        result = flaky()
        self.assertEqual(result, 42)
        self.assertEqual(len(attempts), 2)
    
    def test_kostyl_method_log_calls(self):
        """kostyl_method с log_calls."""
        @kostyl_method(safe_mode=False, retry_mode=False, log_calls=True)
        def func(x):
            return x
        
        result = func(100)
        self.assertEqual(result, 100)
    
    def test_kostyl_method_measure_time(self):
        """kostyl_method с measure_time."""
        @kostyl_method(safe_mode=False, retry_mode=False, measure_time=True)
        def slow_func():
            time.sleep(0.05)
            return "slow"
        
        result = slow_func()
        self.assertEqual(result, "slow")
    
    def test_kostyl_method_cache(self):
        """kostyl_method с cache_results."""
        call_count = [0]
        
        @kostyl_method(safe_mode=False, retry_mode=False, cache_results=True)
        def cached_func(x):
            call_count[0] += 1
            return x * 2
        
        self.assertEqual(cached_func(5), 10)
        self.assertEqual(cached_func(5), 10)
        self.assertEqual(call_count[0], 1)
    
    def test_kostyl_method_all_features(self):
        """kostyl_method со всеми фичами."""
        @kostyl_method(
            safe_mode=True,
            retry_mode=True,
            max_attempts=2,
            fallback_value=-999,
            log_calls=True,
            measure_time=True,
            cache_results=True
        )
        def mega_func(x):
            if x < 0:
                raise ValueError()
            return x * x
        
        self.assertEqual(mega_func(10), 100)
        self.assertEqual(mega_func(-1), -999)
        self.assertEqual(mega_func(10), 100)  # Из кеша


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ monkey_patch
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestMonkeyPatchDecorator(unittest.TestCase):
    """Тесты декоратора monkey_patch."""
    
    def test_monkey_patch_decorator_exists(self):
        """Декоратор monkey_patch должен существовать."""
        self.assertTrue(callable(monkey_patch))
    
    def test_monkey_patch_function_replacement(self):
        """monkey_patch должен заменять функцию."""
        class TestClass:
            def original_method(self):
                return "original"
        
        @monkey_patch(TestClass, 'original_method')
        def new_method(self):
            return "patched"
        
        obj = TestClass()
        self.assertEqual(obj.original_method(), "patched")
    
    def test_monkey_patch_attribute_replacement(self):
        """monkey_patch должен заменять атрибут."""
        class TestClass:
            value = "old"
        
        @monkey_patch(TestClass, 'value')
        def new_value():
            return "new"
        
        # После патча value — это функция
        self.assertEqual(TestClass.value(), "new")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ all_decorators
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestAllDecorators(unittest.TestCase):
    """Тесты функции all_decorators."""
    
    def test_all_decorators_returns_dict(self):
        """all_decorators должен возвращать словарь."""
        result = all_decorators()
        
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
    
    def test_all_decorators_contains_key_types(self):
        """Все ключи — строки."""
        result = all_decorators()
        
        for key in result:
            self.assertIsInstance(key, str)
    
    def test_all_decorators_values_are_callable(self):
        """Все значения должны быть callable."""
        result = all_decorators()
        
        for key, value in result.items():
            self.assertTrue(callable(value), 
                          f"all_decorators['{key}'] не callable: {type(value)}")
    
    def test_all_decorators_expected_keys(self):
        """Должны быть все ожидаемые декораторы."""
        result = all_decorators()
        
        expected = ['safe', 'retry', 'fallback', 'cached', 
                   'deprecated_kostyl', 'log_execution', 
                   'kostyl_method', 'monkey_patch']
        
        for key in expected:
            self.assertIn(key, result, f"Декоратор {key} отсутствует")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ DecoratorStats
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestDecoratorStats(unittest.TestCase):
    """Тесты класса DecoratorStats."""
    
    def test_stats_creation(self):
        """DecoratorStats должен создаваться."""
        stats = DecoratorStats()
        
        self.assertEqual(stats.total_calls, 0)
        self.assertEqual(stats.successful_calls, 0)
        self.assertEqual(stats.failed_calls, 0)
    
    def test_stats_record_success(self):
        """record_success должен обновлять статистику."""
        stats = DecoratorStats()
        stats.record_success(0.5)
        
        self.assertEqual(stats.total_calls, 1)
        self.assertEqual(stats.successful_calls, 1)
        self.assertEqual(stats.total_time, 0.5)
    
    def test_stats_record_failure(self):
        """record_failure должен обновлять статистику."""
        stats = DecoratorStats()
        stats.record_failure("ValueError")
        
        self.assertEqual(stats.total_calls, 1)
        self.assertEqual(stats.failed_calls, 1)
        self.assertIn("ValueError", stats.errors)
    
    def test_stats_record_retry(self):
        """record_retry должен считать повторы."""
        stats = DecoratorStats()
        stats.record_retry()
        stats.record_retry()
        
        self.assertEqual(stats.retry_attempts, 2)
    
    def test_stats_record_fallback(self):
        """record_fallback должен считать использование запасных."""
        stats = DecoratorStats()
        stats.record_fallback()
        
        self.assertEqual(stats.fallbacks_used, 1)
    
    def test_stats_success_rate(self):
        """get_success_rate должен вычислять процент успеха."""
        stats = DecoratorStats()
        
        self.assertEqual(stats.get_success_rate(), 100.0)  # 0 вызовов = 100%
        
        stats.record_success(0.1)
        stats.record_failure("Error")
        
        self.assertEqual(stats.get_success_rate(), 50.0)
    
    def test_stats_average_time(self):
        """get_average_time должен вычислять среднее."""
        stats = DecoratorStats()
        
        self.assertEqual(stats.get_average_time(), 0.0)
        
        stats.record_success(0.5)
        stats.record_success(1.5)
        
        self.assertEqual(stats.get_average_time(), 1.0)
    
    def test_stats_summary(self):
        """summary должен возвращать строку."""
        stats = DecoratorStats()
        stats.record_success(0.1)
        stats.record_failure("Error")
        
        summary = stats.summary()
        self.assertIsInstance(summary, str)
        self.assertIn("Вызовов", summary)


# ═══════════════════════════════════════════════════════════════
# КОМБИНИРОВАННЫЕ ТЕСТЫ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestCombinedDecorators(unittest.TestCase):
    """Тесты комбинаций декораторов."""
    
    def test_safe_plus_retry(self):
        """safe + retry вместе."""
        @safe(fallback="final_fallback")
        @retry(max_attempts=3, delay=0.01, fallback="retry_fallback")
        def flaky():
            raise ValueError("Всегда падает")
        
        # retry fallback перезаписывается safe fallback
        result = flaky()
        self.assertEqual(result, "final_fallback")
    
    def test_retry_plus_cached(self):
        """retry + cached вместе."""
        call_count = [0]
        
        @retry(max_attempts=3, delay=0.01)
        @cached()
        def func(x):
            call_count[0] += 1
            return x * 2
        
        self.assertEqual(func(5), 10)
        self.assertEqual(func(5), 10)
        self.assertEqual(call_count[0], 1)
    
    def test_fallback_plus_deprecated(self):
        """fallback + deprecated_kostyl вместе."""
        @fallback("deprecated_fallback")
        @deprecated_kostyl(reason="old")
        def old_func(x):
            if x < 0:
                raise ValueError()
            return x
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(old_func(10), 10)
            self.assertEqual(old_func(-1), "deprecated_fallback")
    
    def test_all_decorators_stack(self):
        """Стек из нескольких декораторов."""
        @safe(fallback="safe_value")
        @retry(max_attempts=2, delay=0.01)
        @fallback("fallback_value")
        @deprecated_kostyl(reason="stack test", alternative="new_stack")
        def stack_func(x):
            if x < 0:
                raise ValueError()
            return f"ok:{x}"
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            self.assertEqual(stack_func(42), "ok:42")
            self.assertEqual(stack_func(-1), "safe_value")
    
    def test_decorator_order_matters(self):
        """Порядок декораторов имеет значение."""
        
        # Сначала retry, потом safe
        @safe(fallback="safe_wins")
        @retry(max_attempts=3, delay=0.01, fallback="retry_wins")
        def func1():
            raise Exception()
        
        self.assertEqual(func1(), "safe_wins")


# ═══════════════════════════════════════════════════════════════
# СТРЕСС-ТЕСТЫ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(DECORATORS_LOADED, "decorators не загружены")
class TestDecoratorStress(unittest.TestCase):
    """Стресс-тесты декораторов."""
    
    def test_many_calls_safe(self):
        """Много вызовов safe."""
        @safe(fallback=0)
        def func(x):
            if x % 2 == 0:
                raise ValueError()
            return x
        
        results = [func(i) for i in range(100)]
        self.assertEqual(len(results), 100)
    
    def test_deep_recursion_safe(self):
        """Глубокая рекурсия с safe."""
        @safe(fallback=0)
        def factorial(n):
            if n < 0:
                raise ValueError()
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        
        self.assertEqual(factorial(10), 3628800)
        self.assertEqual(factorial(-1), 0)
    
    def test_thread_safety_all_decorators(self):
        """Потокобезопасность всех декораторов."""
        results = []
        errors = []
        
        @safe(fallback="thread_safe")
        @retry(max_attempts=2, delay=0.01)
        @cached()
        def thread_func(x):
            if x < 0:
                raise ValueError()
            return x * 2
        
        def worker():
            try:
                for i in range(10):
                    results.append(thread_func(i - 5))
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 50)


if __name__ == '__main__':
    print(f"{'='*50}")
    print(f"🧪 Тесты декораторов kostylpy")
    print(f"{'='*50}")
    unittest.main(verbosity=2)