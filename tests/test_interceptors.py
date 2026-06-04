"""
Тесты перехватчиков kostylpy.
Проверяют перехват функций, атрибутов, импортов,
глобальный перехват и режимы шпионажа.
"""

import sys
import os
import time
import unittest
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import kostylpy
    from kostylpy.interceptors import (
        BaseInterceptor,
        FunctionInterceptor,
        AttributeInterceptor,
        ImportInterceptor,
        GlobalInterceptor,
        InterceptMode,
        InterceptResult,
        InterceptRecord,
        InterceptorStats,
        intercept_all,
        spy_on_function,
        block_imports,
    )
    INTERCEPTORS_LOADED = True
except ImportError as e:
    print(f"⚠️ interceptors не загружены: {e}")
    INTERCEPTORS_LOADED = False


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ БАЗОВОГО ПЕРЕХВАТЧИКА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestBaseInterceptor(unittest.TestCase):
    """Тесты базового перехватчика."""
    
    def test_base_interceptor_creation(self):
        """Базовый перехватчик должен создаваться."""
        interceptor = BaseInterceptor(
            name="test_interceptor",
            mode=InterceptMode.LOG_ONLY
        )
        
        self.assertEqual(interceptor.name, "test_interceptor")
        self.assertEqual(interceptor.mode, InterceptMode.LOG_ONLY)
        self.assertFalse(interceptor.active)
    
    def test_base_interceptor_start_stop(self):
        """Перехватчик должен запускаться и останавливаться."""
        interceptor = BaseInterceptor(name="test", mode=InterceptMode.LOG_ONLY)
        
        self.assertFalse(interceptor.active)
        interceptor.start()
        self.assertTrue(interceptor.active)
        interceptor.stop()
        self.assertFalse(interceptor.active)
    
    def test_base_interceptor_auto_start(self):
        """Перехватчик с auto_start должен запускаться автоматически."""
        interceptor = BaseInterceptor(
            name="auto_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        self.assertTrue(interceptor.active)
        interceptor.stop()
    
    def test_base_interceptor_stats(self):
        """У перехватчика должна быть статистика."""
        interceptor = BaseInterceptor(name="stats_test")
        
        self.assertIsInstance(interceptor.stats, InterceptorStats)
        self.assertEqual(interceptor.stats.total_intercepts, 0)
    
    def test_base_interceptor_registry(self):
        """Перехватчики должны регистрироваться."""
        interceptor = BaseInterceptor(name="registry_test")
        
        found = BaseInterceptor.get_interceptor("registry_test")
        self.assertIs(found, interceptor)
    
    def test_list_interceptors(self):
        """Должен быть список всех перехватчиков."""
        interceptors = BaseInterceptor.list_interceptors()
        self.assertIsInstance(interceptors, list)
        self.assertIn("registry_test", interceptors)
    
    def test_stop_all(self):
        """Должна быть возможность остановить все перехватчики."""
        i1 = BaseInterceptor(name="stop_all_1", auto_start=True)
        i2 = BaseInterceptor(name="stop_all_2", auto_start=True)
        
        BaseInterceptor.stop_all()
        
        self.assertFalse(i1.active)
        self.assertFalse(i2.active)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПЕРЕХВАТЧИКА ФУНКЦИЙ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestFunctionInterceptor(unittest.TestCase):
    """Тесты перехватчика функций."""
    
    def setUp(self):
        """Создаёт тестовую функцию."""
        def test_func(x, y=10):
            return x * y
        
        self.test_func = test_func
    
    def test_function_interceptor_creation(self):
        """Перехватчик функций должен создаваться."""
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="func_test",
            mode=InterceptMode.LOG_ONLY
        )
        
        self.assertEqual(interceptor._func_name, "test_func")
    
    def test_function_interceptor_start_stop(self):
        """Перехватчик функций должен запускаться и останавливаться."""
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="func_start_test"
        )
        
        interceptor.start()
        self.assertTrue(interceptor.active)
        interceptor.stop()
        self.assertFalse(interceptor.active)
    
    def test_function_interceptor_logs_calls(self):
        """Перехватчик должен логировать вызовы."""
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="func_log_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        # Вызываем перехваченную функцию
        result = interceptor.target_func(5, 2)
        
        self.assertEqual(result, 10)
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_function_interceptor_before_call(self):
        """Должен работать before_call хук."""
        call_args = []
        
        def before_hook(args, kwargs):
            call_args.append((args, kwargs))
        
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="before_test",
            mode=InterceptMode.LOG_ONLY,
            before_call=before_hook,
            auto_start=True
        )
        
        interceptor.target_func(3, 4)
        
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0][0], (3, 4))
        
        interceptor.stop()
    
    def test_function_interceptor_after_call(self):
        """Должен работать after_call хук."""
        call_results = []
        
        def after_hook(result, args, kwargs):
            call_results.append(result)
        
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="after_test",
            mode=InterceptMode.LOG_ONLY,
            after_call=after_hook,
            auto_start=True
        )
        
        interceptor.target_func(6, 7)
        
        self.assertEqual(len(call_results), 1)
        self.assertEqual(call_results[0], 42)
        
        interceptor.stop()
    
    def test_function_interceptor_modify_args(self):
        """Должна работать модификация аргументов."""
        def modifier(args, kwargs):
            # Удваиваем первый аргумент
            return (args[0] * 2,) + args[1:], kwargs
        
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="modify_test",
            mode=InterceptMode.MODIFY,
            modify_args=modifier,
            auto_start=True
        )
        
        # test_func(5, 10) -> после модификации -> test_func(10, 10) = 100
        result = interceptor.target_func(5, 10)
        self.assertEqual(result, 100)
        
        interceptor.stop()
    
    def test_function_interceptor_modify_result(self):
        """Должна работать модификация результата."""
        def result_modifier(result, args, kwargs):
            return result * 2
        
        interceptor = FunctionInterceptor(
            target_func=self.test_func,
            name="result_test",
            mode=InterceptMode.MODIFY,
            modify_result=result_modifier,
            auto_start=True
        )
        
        # test_func(5, 10) = 50 -> модификация -> 100
        result = interceptor.target_func(5, 10)
        self.assertEqual(result, 100)
        
        interceptor.stop()
    
    def test_function_interceptor_on_error(self):
        """Должен работать обработчик ошибок."""
        errors = []
        
        def error_handler(error, args, kwargs):
            errors.append(error)
            return "fallback"
        
        def failing_func():
            raise ValueError("Тестовая ошибка")
        
        interceptor = FunctionInterceptor(
            target_func=failing_func,
            name="error_test",
            mode=InterceptMode.LOG_ONLY,
            on_error=error_handler,
            auto_start=True
        )
        
        result = interceptor.target_func()
        
        self.assertEqual(result, "fallback")
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ValueError)
        
        interceptor.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПЕРЕХВАТЧИКА АТРИБУТОВ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestAttributeInterceptor(unittest.TestCase):
    """Тесты перехватчика атрибутов."""
    
    def setUp(self):
        """Создаёт тестовый объект."""
        class TestObj:
            def __init__(self):
                self.name = "test"
                self.value = 42
                self._secret = "hidden"
        
        self.test_obj = TestObj()
    
    def test_attribute_interceptor_creation(self):
        """Перехватчик атрибутов должен создаваться."""
        interceptor = AttributeInterceptor(
            target_object=self.test_obj,
            name="attr_test"
        )
        
        self.assertEqual(interceptor.target, "TestObj")
    
    def test_attribute_interceptor_logs_get(self):
        """Должен логировать чтение атрибутов."""
        interceptor = AttributeInterceptor(
            target_object=self.test_obj,
            name="attr_get_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        # Читаем атрибут
        _ = self.test_obj.name
        
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_attribute_interceptor_logs_set(self):
        """Должен логировать запись атрибутов."""
        interceptor = AttributeInterceptor(
            target_object=self.test_obj,
            name="attr_set_test",
            mode=InterceptMode.LOG_ONLY,
            log_set=True,
            auto_start=True
        )
        
        # Пишем атрибут
        self.test_obj.new_attr = "new_value"
        
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_attribute_interceptor_blocked(self):
        """Должен блокировать запрещённые атрибуты."""
        interceptor = AttributeInterceptor(
            target_object=self.test_obj,
            name="attr_block_test",
            mode=InterceptMode.FILTER,
            blocked_attributes=['_secret'],
            default_value=None,
            auto_start=True
        )
        
        # Пытаемся прочитать заблокированный атрибут
        result = self.test_obj._secret
        
        # Должен вернуть default_value
        self.assertIsNone(result)
        
        interceptor.stop()
    
    def test_attribute_interceptor_allowed_only(self):
        """Должен разрешать только указанные атрибуты."""
        interceptor = AttributeInterceptor(
            target_object=self.test_obj,
            name="attr_allow_test",
            mode=InterceptMode.FILTER,
            allowed_attributes=['name'],
            default_value="DENIED",
            auto_start=True
        )
        
        # Разрешённый атрибут
        self.assertEqual(self.test_obj.name, "test")
        
        # Неразрешённый атрибут
        self.assertEqual(self.test_obj.value, "DENIED")
        
        interceptor.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПЕРЕХВАТЧИКА ИМПОРТОВ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestImportInterceptor(unittest.TestCase):
    """Тесты перехватчика импортов."""
    
    def test_import_interceptor_creation(self):
        """Перехватчик импортов должен создаваться."""
        interceptor = ImportInterceptor(
            name="import_test",
            mode=InterceptMode.LOG_ONLY
        )
        
        self.assertEqual(interceptor.name, "import_test")
    
    def test_import_interceptor_start_stop(self):
        """Должен запускаться и останавливаться."""
        interceptor = ImportInterceptor(name="import_start_test")
        
        original_import = __builtins__.__import__
        
        interceptor.start()
        self.assertNotEqual(__builtins__.__import__, original_import)
        
        interceptor.stop()
        self.assertEqual(__builtins__.__import__, original_import)
    
    def test_import_interceptor_logs(self):
        """Должен логировать импорты."""
        interceptor = ImportInterceptor(
            name="import_log_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        # Импортируем что-нибудь
        import json as test_json
        
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_import_interceptor_blocked(self):
        """Должен блокировать запрещённые модули."""
        interceptor = ImportInterceptor(
            name="import_block_test",
            mode=InterceptMode.FILTER,
            blocked_modules=['os'],
            auto_start=True
        )
        
        with self.assertRaises(ImportError):
            __import__('os')
        
        interceptor.stop()
    
    def test_import_interceptor_redirect(self):
        """Должен перенаправлять импорты."""
        interceptor = ImportInterceptor(
            name="import_redirect_test",
            mode=InterceptMode.MODIFY,
            redirect_map={'json': 'os'},
            auto_start=True
        )
        
        # Импорт json должен перенаправиться на os
        import json as test_mod
        
        self.assertEqual(test_mod.__name__, 'os')
        
        interceptor.stop()
    
    def test_import_interceptor_stub(self):
        """Должен создавать заглушки."""
        interceptor = ImportInterceptor(
            name="import_stub_test",
            mode=InterceptMode.REPLACE,
            stub_modules=['nonexistent_module_xyz'],
            auto_start=True
        )
        
        module = __import__('nonexistent_module_xyz')
        self.assertTrue(getattr(module, '__kostyl_stub__', False))
        
        interceptor.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ГЛОБАЛЬНОГО ПЕРЕХВАТЧИКА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestGlobalInterceptor(unittest.TestCase):
    """Тесты глобального перехватчика."""
    
    def test_global_interceptor_creation(self):
        """Глобальный перехватчик должен создаваться."""
        interceptor = GlobalInterceptor(
            name="global_test",
            mode=InterceptMode.LOG_ONLY
        )
        
        self.assertEqual(interceptor.name, "global_test")
    
    def test_global_interceptor_print(self):
        """Должен перехватывать print."""
        interceptor = GlobalInterceptor(
            name="global_print_test",
            mode=InterceptMode.LOG_ONLY,
            intercept_print=True,
            intercept_open=False,
            intercept_import=False,
            intercept_exceptions=False,
            auto_start=True
        )
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            print("test message")
        
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_global_interceptor_selective(self):
        """Должен работать с выборочными перехватами."""
        # Перехватываем только print, не трогаем open
        interceptor = GlobalInterceptor(
            name="selective_test",
            intercept_print=True,
            intercept_open=False,
            intercept_import=False,
            intercept_exceptions=False,
            auto_start=True
        )
        
        # print должен перехватываться
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            print("test")
        
        print_count = interceptor.stats.total_intercepts
        
        # open не должен перехватываться (счётчик не должен увеличиться)
        try:
            f = open("/nonexistent/path", "r")
        except:
            pass
        
        self.assertEqual(interceptor.stats.total_intercepts, print_count)
        
        interceptor.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ РЕЖИМОВ ПЕРЕХВАТА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestInterceptModes(unittest.TestCase):
    """Тесты режимов перехвата."""
    
    def test_log_only_mode(self):
        """Режим LOG_ONLY должен только логировать."""
        def test_func(x):
            return x * 2
        
        interceptor = FunctionInterceptor(
            target_func=test_func,
            name="log_only_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        result = interceptor.target_func(21)
        self.assertEqual(result, 42)
        self.assertGreater(interceptor.stats.total_intercepts, 0)
        
        interceptor.stop()
    
    def test_modify_mode(self):
        """Режим MODIFY должен изменять аргументы/результат."""
        def test_func(x, y):
            return x + y
        
        def modifier(args, kwargs):
            return (args[0] * 10, args[1] * 10), kwargs
        
        interceptor = FunctionInterceptor(
            target_func=test_func,
            name="modify_mode_test",
            mode=InterceptMode.MODIFY,
            modify_args=modifier,
            auto_start=True
        )
        
        # 2+3=5, но аргументы модифицируются: 20+30=50
        result = interceptor.target_func(2, 3)
        self.assertEqual(result, 50)
        
        interceptor.stop()
    
    def test_filter_mode(self):
        """Режим FILTER должен блокировать."""
        # Тестируем через ImportInterceptor
        interceptor = ImportInterceptor(
            name="filter_mode_test",
            mode=InterceptMode.FILTER,
            blocked_modules=['csv'],
            auto_start=True
        )
        
        with self.assertRaises(ImportError):
            __import__('csv')
        
        interceptor.stop()
    
    def test_replace_mode(self):
        """Режим REPLACE должен заменять."""
        interceptor = ImportInterceptor(
            name="replace_mode_test",
            mode=InterceptMode.REPLACE,
            stub_modules=['fake_module_123'],
            auto_start=True
        )
        
        module = __import__('fake_module_123')
        self.assertIsNotNone(module)
        self.assertTrue(hasattr(module, '__kostyl_stub__'))
        
        interceptor.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ СТАТИСТИКИ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestInterceptorStats(unittest.TestCase):
    """Тесты статистики перехватчиков."""
    
    def test_interceptor_stats_creation(self):
        """Статистика должна создаваться."""
        stats = InterceptorStats()
        
        self.assertEqual(stats.total_intercepts, 0)
        self.assertEqual(stats.allowed, 0)
        self.assertEqual(stats.denied, 0)
    
    def test_interceptor_stats_summary(self):
        """Должна быть строка со сводкой."""
        stats = InterceptorStats()
        summary = stats.summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn("Перехватов", summary)
    
    def test_interceptor_stats_average_time(self):
        """Должно вычисляться среднее время."""
        stats = InterceptorStats()
        stats.total_intercepts = 10
        stats.total_time = 5.0
        
        self.assertEqual(stats.average_time, 0.5)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestInterceptorHelpers(unittest.TestCase):
    """Тесты вспомогательных функций."""
    
    def test_intercept_all(self):
        """intercept_all должен создавать глобальный перехватчик."""
        interceptor = intercept_all()
        
        self.assertIsInstance(interceptor, GlobalInterceptor)
        self.assertTrue(interceptor.active)
        
        interceptor.stop()
    
    def test_spy_on_function(self):
        """spy_on_function должен создавать шпиона."""
        def target():
            return "secret"
        
        spy = spy_on_function(target)
        
        self.assertIsInstance(spy, FunctionInterceptor)
        self.assertTrue(spy.active)
        self.assertEqual(spy.mode, InterceptMode.SPY)
        
        spy.stop()
    
    def test_block_imports(self):
        """block_imports должен блокировать модули."""
        blocker = block_imports('math')
        
        self.assertIsInstance(blocker, ImportInterceptor)
        self.assertTrue(blocker.active)
        self.assertIn('math', blocker.blocked_modules)
        
        blocker.stop()


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ InterceptRecord
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestInterceptRecord(unittest.TestCase):
    """Тесты записи перехвата."""
    
    def test_record_creation(self):
        """Запись должна создаваться."""
        record = InterceptRecord(
            id=1,
            timestamp=time.time(),
            interceptor_name="test",
            target="test_func",
            mode=InterceptMode.LOG_ONLY,
            result=InterceptResult.ALLOW,
            args_summary="(1, 2)",
            result_summary="42",
            duration=0.001
        )
        
        self.assertEqual(record.id, 1)
        self.assertEqual(record.interceptor_name, "test")
        self.assertEqual(record.result, InterceptResult.ALLOW)
    
    def test_record_string(self):
        """Запись должна преобразовываться в строку."""
        record = InterceptRecord(
            id=1,
            timestamp=time.time(),
            interceptor_name="test",
            target="func",
            mode=InterceptMode.LOG_ONLY,
            result=InterceptResult.ALLOW,
            args_summary="()",
            result_summary="None",
            duration=0.0
        )
        
        s = str(record)
        self.assertIsInstance(s, str)
        self.assertIn("test", s)
        self.assertIn("func", s)


# ═══════════════════════════════════════════════════════════════
# СТРЕСС-ТЕСТЫ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(INTERCEPTORS_LOADED, "interceptors не загружены")
class TestInterceptorStress(unittest.TestCase):
    """Стресс-тесты перехватчиков."""
    
    def test_many_interceptions(self):
        """Много перехватов не должны ломать систему."""
        def fast_func(x):
            return x + 1
        
        interceptor = FunctionInterceptor(
            target_func=fast_func,
            name="stress_test",
            mode=InterceptMode.LOG_ONLY,
            auto_start=True
        )
        
        # Много вызовов
        for i in range(100):
            result = interceptor.target_func(i)
            self.assertEqual(result, i + 1)
        
        self.assertEqual(interceptor.stats.total_intercepts, 100)
        
        interceptor.stop()
    
    def test_multiple_interceptors(self):
        """Несколько перехватчиков одновременно."""
        interceptors = []
        
        for i in range(5):
            interceptor = BaseInterceptor(
                name=f"multi_test_{i}",
                mode=InterceptMode.LOG_ONLY,
                auto_start=True
            )
            interceptors.append(interceptor)
        
        # Все должны быть активны
        for i, interceptor in enumerate(interceptors):
            self.assertTrue(interceptor.active, f"Interceptor {i} not active")
        
        # Останавливаем
        for interceptor in interceptors:
            interceptor.stop()
    
    def test_thread_safety(self):
        """Перехватчики должны работать в многопоточной среде."""
        results = []
        errors = []
        
        def thread_func():
            try:
                interceptor = BaseInterceptor(
                    name=f"thread_test_{threading.get_ident()}",
                    auto_start=True
                )
                time.sleep(0.01)
                interceptor.stop()
                results.append(True)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=thread_func) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)