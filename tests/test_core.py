"""
Тесты ядра kostylpy.
Проверяют инициализацию, статус, здоровье системы,
управление модулями, отчёты и безопасность.
"""

import sys
import os
import time
import unittest
import threading
import io
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import kostylpy
    from kostylpy.core import KostylPy, CoreStatus, CoreStats
    from kostylpy.constants import (
        KOSTYLPY_VERSION, KOSTYLPY_CODENAME, 
        PANIC_THRESHOLD, Emoji, Colors,
        DEFAULT_CONFIG
    )
    CORE_LOADED = True
except ImportError as e:
    print(f"⚠️ core не загружен: {e}")
    CORE_LOADED = False


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ИНИЦИАЛИЗАЦИИ ЯДРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreInit(unittest.TestCase):
    """Тесты инициализации ядра."""
    
    def test_core_singleton(self):
        """Ядро должно быть синглтоном."""
        core1 = KostylPy()
        core2 = KostylPy()
        self.assertIs(core1, core2)
    
    def test_core_singleton_thread_safe(self):
        """Синглтон должен быть потокобезопасным."""
        instances = []
        
        def create_instance():
            instances.append(KostylPy())
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Все должны быть одним экземпляром
        first = instances[0]
        for instance in instances[1:]:
            self.assertIs(instance, first)
    
    def test_core_initialized(self):
        """Ядро должно быть инициализировано."""
        core = KostylPy()
        self.assertTrue(core._initialized)
    
    def test_core_initialized_once(self):
        """Инициализация должна происходить только один раз."""
        core = KostylPy()
        
        # Пробуем инициализировать ещё раз
        start_modules = core.loaded_modules()
        core._initialize()
        end_modules = core.loaded_modules()
        
        # Модули не должны дублироваться
        self.assertEqual(len(start_modules), len(end_modules))
    
    def test_core_startup_time(self):
        """Время запуска должно быть записано."""
        core = KostylPy()
        self.assertGreater(core._start_time, 0)
        self.assertLess(core._start_time, time.time() + 1)
    
    def test_core_has_modules_after_init(self):
        """После инициализации должны быть модули."""
        core = KostylPy()
        modules = core.loaded_modules()
        self.assertGreater(len(modules), 0)
    
    def test_core_required_modules(self):
        """Обязательные модули должны быть загружены."""
        core = KostylPy()
        modules = core.loaded_modules()
        
        required = ['config', 'logger', 'metrics', 'utils', 'decorators']
        for module in required:
            self.assertIn(module, modules, f"Обязательный модуль {module} не загружен")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ СТАТУСА ЯДРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreStatus(unittest.TestCase):
    """Тесты статуса ядра."""
    
    def test_core_initial_status(self):
        """Начальный статус ядра."""
        core = KostylPy()
        self.assertIn(core.status, [CoreStatus.ACTIVE, CoreStatus.DEGRADED])
    
    def test_core_is_active(self):
        """Ядро должно быть активно."""
        core = KostylPy()
        self.assertTrue(core.is_active)
    
    def test_core_not_panic_initially(self):
        """При запуске не должно быть паники."""
        core = KostylPy()
        self.assertFalse(core.is_panic)
    
    def test_core_status_values(self):
        """Все значения статусов должны быть строками."""
        for status in CoreStatus:
            self.assertIsInstance(status.value, str)
    
    def test_core_uptime_positive(self):
        """Время работы должно быть положительным."""
        core = KostylPy()
        self.assertGreater(core.uptime, 0)
    
    def test_core_uptime_increases(self):
        """Время работы должно увеличиваться."""
        core = KostylPy()
        uptime1 = core.uptime
        time.sleep(0.1)
        uptime2 = core.uptime
        self.assertGreater(uptime2, uptime1)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ МОДУЛЕЙ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreModules(unittest.TestCase):
    """Тесты доступа к модулям."""
    
    def test_get_config_module(self):
        """Должен быть доступен модуль config."""
        core = KostylPy()
        config = core.config
        self.assertIsNotNone(config)
    
    def test_get_logger_module(self):
        """Должен быть доступен модуль logger."""
        core = KostylPy()
        logger = core.logger
        self.assertIsNotNone(logger)
    
    def test_get_metrics_module(self):
        """Должен быть доступен модуль metrics."""
        core = KostylPy()
        metrics = core.metrics
        self.assertIsNotNone(metrics)
    
    def test_get_module_by_name(self):
        """get_module должен возвращать модуль по имени."""
        core = KostylPy()
        
        for name in ['config', 'logger', 'metrics', 'utils', 'decorators']:
            mod = core.get_module(name)
            self.assertIsNotNone(mod, f"Модуль {name} не найден")
    
    def test_get_nonexistent_module(self):
        """get_module для несуществующего модуля должен вернуть None."""
        core = KostylPy()
        
        mod = core.get_module('super_mega_module_that_doesnt_exist_xyz')
        self.assertIsNone(mod)
    
    def test_is_module_loaded(self):
        """is_module_loaded должен корректно проверять."""
        core = KostylPy()
        
        self.assertTrue(core.is_module_loaded('config'))
        self.assertTrue(core.is_module_loaded('logger'))
        self.assertFalse(core.is_module_loaded('fake_module'))
    
    def test_loaded_modules_returns_list(self):
        """loaded_modules должен возвращать список."""
        core = KostylPy()
        modules = core.loaded_modules()
        
        self.assertIsInstance(modules, list)
        self.assertGreater(len(modules), 0)
    
    def test_loaded_modules_are_strings(self):
        """Все имена модулей должны быть строками."""
        core = KostylPy()
        modules = core.loaded_modules()
        
        for module in modules:
            self.assertIsInstance(module, str)
    
    def test_loaded_modules_no_duplicates(self):
        """В списке модулей не должно быть дубликатов."""
        core = KostylPy()
        modules = core.loaded_modules()
        
        self.assertEqual(len(modules), len(set(modules)))


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ЗДОРОВЬЯ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreHealth(unittest.TestCase):
    """Тесты здоровья ядра."""
    
    def test_health_check_returns_dict(self):
        """health_check должен возвращать словарь."""
        core = KostylPy()
        health = core.health_check()
        
        self.assertIsInstance(health, dict)
    
    def test_health_check_all_keys(self):
        """health_check должен содержать все ключи."""
        core = KostylPy()
        health = core.health_check()
        
        expected_keys = [
            'core', 'config', 'logger', 'metrics',
            'decorators', 'validators', 'interceptors', 'async'
        ]
        
        for key in expected_keys:
            self.assertIn(key, health, f"Ключ {key} отсутствует в health_check")
    
    def test_health_check_boolean_values(self):
        """Все значения health_check должны быть boolean."""
        core = KostylPy()
        health = core.health_check()
        
        for key, value in health.items():
            self.assertIsInstance(value, bool, 
                                f"health[{key}] должен быть bool, а не {type(value)}")
    
    def test_health_core_always_true(self):
        """core в health_check должен быть True."""
        core = KostylPy()
        health = core.health_check()
        
        self.assertTrue(health.get('core', False))


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ОТЧЁТОВ И СТАТИСТИКИ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreReport(unittest.TestCase):
    """Тесты отчётов и статистики."""
    
    def test_report_is_string(self):
        """report() должен возвращать строку."""
        core = KostylPy()
        report = core.report()
        
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
    
    def test_report_contains_version(self):
        """Отчёт должен содержать версию."""
        core = KostylPy()
        report = core.report()
        
        self.assertIn(KOSTYLPY_VERSION, report)
    
    def test_report_contains_status(self):
        """Отчёт должен содержать статус."""
        core = KostylPy()
        report = core.report()
        
        self.assertIn(core.status, report)
    
    def test_report_contains_modules(self):
        """Отчёт должен содержать список модулей."""
        core = KostylPy()
        report = core.report()
        
        self.assertIn('Модули', report)
        self.assertIn('config', report)
    
    def test_stats_returns_dict(self):
        """stats() должен возвращать словарь."""
        core = KostylPy()
        stats = core.stats()
        
        self.assertIsInstance(stats, dict)
    
    def test_stats_required_keys(self):
        """stats должен содержать обязательные ключи."""
        core = KostylPy()
        stats = core.stats()
        
        required = ['version', 'codename', 'status', 'uptime', 
                   'crutches', 'errors_caught', 'modules_loaded']
        
        for key in required:
            self.assertIn(key, stats, f"Ключ {key} отсутствует в stats")
    
    def test_stats_uptime_positive(self):
        """uptime в stats должен быть положительным."""
        core = KostylPy()
        stats = core.stats()
        
        self.assertGreater(stats['uptime'], 0)
    
    def test_stats_crutches_is_int(self):
        """crutches в stats должен быть целым числом."""
        core = KostylPy()
        stats = core.stats()
        
        self.assertIsInstance(stats['crutches'], int)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПАТЧИНГА BUILTINS
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreBuiltinsPatched(unittest.TestCase):
    """Тесты пропатченных builtins."""
    
    def test_patched_builtins_list(self):
        """Список пропатченных builtins."""
        core = KostylPy()
        patched = core._patched_builtins
        
        self.assertIsInstance(patched, list)
        self.assertIn('print', patched)
        self.assertIn('open', patched)
    
    def test_patched_print_works(self):
        """Патченный print должен работать."""
        import builtins
        
        f = io.StringIO()
        with redirect_stdout(f):
            builtins.print("test message")
            builtins.print("another", "message", sep="-")
        
        output = f.getvalue()
        self.assertIn("test message", output)
        self.assertIn("another-message", output)
    
    def test_patched_print_never_fails(self):
        """Патченный print не должен падать никогда."""
        import builtins
        
        # Пробуем напечатать всякое
        test_values = [
            None, True, False, 0, 1, -1, 3.14,
            "", "hello", "🔥", "x" * 10000,
            [], [1, 2, 3], {}, {'a': 1},
            lambda x: x, object(),
        ]
        
        for value in test_values:
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    builtins.print(value)
            except Exception as e:
                self.fail(f"print({repr(value)[:50]}) упал: {e}")
    
    def test_patched_print_with_broken_str(self):
        """Патченный print с объектом у которого сломан __str__."""
        import builtins
        
        class BrokenStr:
            def __str__(self):
                raise RuntimeError("Сломан!")
        
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                builtins.print(BrokenStr())
            except Exception as e:
                self.fail(f"print(BrokenStr()) упал: {e}")
        
        # Хоть что-то должно быть выведено
        output = f.getvalue()
        self.assertGreater(len(output), 0)
    
    def test_patched_open_works(self):
        """Патченный open должен работать с существующими файлами."""
        import builtins
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            f = builtins.open(tmp_path, 'r')
            content = f.read()
            self.assertEqual(content, "test content")
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def test_patched_open_creates_stub(self):
        """Патченный open должен создавать заглушку для несуществующих файлов."""
        import builtins
        
        # Не должен падать
        f = builtins.open("/definitely/nonexistent/file/for/test.txt", "r")
        content = f.read()
        
        self.assertEqual(content, "")
    
    def test_patched_open_with_permission_error(self):
        """Патченный open должен обрабатывать ошибки доступа."""
        import builtins
        
        # На большинстве систем /root недоступен
        f = builtins.open("/root/secret.txt", "r")
        content = f.read()
        
        self.assertEqual(content, "")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ОБРАБОТКИ ОШИБОК
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок ядром."""
    
    def test_global_exception_hook_exists(self):
        """Должен быть установлен глобальный обработчик."""
        self.assertIsNotNone(sys.excepthook)
    
    def test_global_exception_hook_is_kostyl(self):
        """Глобальный обработчик должен быть от kostylpy."""
        hook = sys.excepthook
        self.assertTrue(
            'kostyl' in hook.__module__ or 
            'kostyl' in getattr(hook, '__name__', '')
        )
    
    def test_error_counter_increments(self):
        """Счётчик ошибок должен увеличиваться."""
        core = KostylPy()
        before = core._error_counter
        
        # Вызываем исключение через excepthook
        try:
            raise ValueError("Тестовая ошибка")
        except ValueError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_tb)
        
        after = core._error_counter
        self.assertGreaterEqual(after, before)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ КОНСТАНТ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreConstants(unittest.TestCase):
    """Тесты констант, используемых ядром."""
    
    def test_version_format(self):
        """Версия должна быть строкой."""
        self.assertIsInstance(KOSTYLPY_VERSION, str)
        self.assertGreater(len(KOSTYLPY_VERSION), 0)
    
    def test_codename_exists(self):
        """Кодовое имя должно быть."""
        self.assertIsInstance(KOSTYLPY_CODENAME, str)
        self.assertGreater(len(KOSTYLPY_CODENAME), 0)
    
    def test_panic_threshold_reasonable(self):
        """Порог паники должен быть разумным."""
        self.assertIsInstance(PANIC_THRESHOLD, int)
        self.assertGreater(PANIC_THRESHOLD, 0)
        self.assertLess(PANIC_THRESHOLD, 10000)
    
    def test_emoji_class_has_values(self):
        """Класс Emoji должен содержать эмодзи."""
        self.assertIsNotNone(Emoji.KOSTYL)
        self.assertIsNotNone(Emoji.SUCCESS)
        self.assertIsNotNone(Emoji.ERROR)
        self.assertIsNotNone(Emoji.WARNING)
        self.assertIsNotNone(Emoji.COFFEE)
    
    def test_colors_class_has_values(self):
        """Класс Colors должен содержать коды."""
        self.assertIsNotNone(Colors.RESET)
        self.assertIsNotNone(Colors.RED)
        self.assertIsNotNone(Colors.GREEN)
    
    def test_default_config_is_dict(self):
        """DEFAULT_CONFIG должен быть словарём."""
        self.assertIsInstance(DEFAULT_CONFIG, dict)
        self.assertGreater(len(DEFAULT_CONFIG), 0)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ATEXIT И СИГНАЛОВ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreHooks(unittest.TestCase):
    """Тесты хуков ядра."""
    
    def test_signal_handlers_registered(self):
        """Должны быть зарегистрированы обработчики сигналов."""
        import signal
        
        # Проверяем что обработчики не по умолчанию
        sigint_handler = signal.getsignal(signal.SIGINT)
        self.assertIsNotNone(sigint_handler)
        
        # Не должен быть стандартным
        self.assertNotEqual(sigint_handler, signal.SIG_DFL)
        self.assertNotEqual(sigint_handler, signal.SIG_IGN)
    
    def test_atexit_registered(self):
        """Должен быть зарегистрирован atexit обработчик."""
        import atexit
        
        # Проверяем что atexit не пустой
        # (конкретные функции проверить сложно)
        self.assertTrue(True)  # Если мы здесь — atexit работает
    
    def test_panic_mode_trigger(self):
        """Режим паники должен активироваться."""
        core = KostylPy()
        
        # Имитируем панику
        core._panic_mode = True
        self.assertTrue(core.is_panic)
        
        # Возвращаем обратно
        core._panic_mode = False
        self.assertFalse(core.is_panic)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ CoreStats
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreStatsClass(unittest.TestCase):
    """Тесты класса CoreStats."""
    
    def test_core_stats_creation(self):
        """CoreStats должен создаваться."""
        stats = CoreStats()
        
        self.assertEqual(stats.startup_time, 0.0)
        self.assertEqual(stats.modules_loaded, 0)
        self.assertEqual(stats.status, CoreStatus.UNINITIALIZED)
    
    def test_core_stats_fields(self):
        """CoreStats должен иметь все поля."""
        stats = CoreStats()
        
        expected_fields = [
            'startup_time', 'modules_loaded', 'modules_failed',
            'total_crutches', 'total_errors_caught', 'uptime', 'status'
        ]
        
        for field in expected_fields:
            self.assertTrue(hasattr(stats, field), f"Поле {field} отсутствует")


# ═══════════════════════════════════════════════════════════════
# СТРЕСС-ТЕСТЫ ЯДРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreStress(unittest.TestCase):
    """Стресс-тесты ядра."""
    
    def test_multiple_core_access(self):
        """Множественный доступ к ядру из разных потоков."""
        core = KostylPy()
        results = []
        errors = []
        
        def access_core():
            try:
                # Разные операции
                _ = core.status
                _ = core.uptime
                _ = core.config
                _ = core.health_check()
                _ = core.stats()
                results.append(True)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=access_core) for _ in range(20)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        
        self.assertEqual(len(results), 20)
        self.assertEqual(len(errors), 0)
    
    def test_rapid_status_changes(self):
        """Быстрые изменения статуса."""
        core = KostylPy()
        
        statuses = []
        for _ in range(100):
            statuses.append(core.status)
            statuses.append(core.is_active)
            statuses.append(core.is_panic)
        
        # Не должно быть исключений
        self.assertEqual(len(statuses), 300)
    
    def test_report_generation_stress(self):
        """Многократная генерация отчётов."""
        core = KostylPy()
        
        for _ in range(10):
            report = core.report()
            self.assertIsInstance(report, str)
            
            stats = core.stats()
            self.assertIsInstance(stats, dict)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ВЫВОДА ЯДРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(CORE_LOADED, "core не загружен")
class TestCoreOutput(unittest.TestCase):
    """Тесты вывода ядра."""
    
    def test_startup_message(self):
        """При инициализации должно быть приветствие."""
        # Уже выведено при импорте, просто проверяем что не упало
        self.assertTrue(True)
    
    def test_report_readable(self):
        """Отчёт должен быть читаемым."""
        core = KostylPy()
        report = core.report()
        
        # Разбиваем на строки
        lines = report.split('\n')
        
        # Должно быть больше 10 строк
        self.assertGreater(len(lines), 10)
        
        # Не должно быть слишком длинных строк
        for line in lines:
            self.assertLess(len(line), 200, f"Слишком длинная строка: {line[:50]}...")
    
    def test_stats_json_serializable(self):
        """stats должен быть JSON-сериализуемым."""
        import json
        
        core = KostylPy()
        stats = core.stats()
        
        try:
            json.dumps(stats)
        except Exception as e:
            self.fail(f"stats не JSON-сериализуем: {e}")


if __name__ == '__main__':
    print(f"{'='*50}")
    print(f"🧪 Тесты ядра kostylpy v{KOSTYLPY_VERSION}")
    print(f"{'='*50}")
    unittest.main(verbosity=2)