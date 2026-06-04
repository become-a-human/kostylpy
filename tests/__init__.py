"""
kostylpy — Профессиональная библиотека костылей для Python.
Версия: 3.0.0-beta-kostyl-enterprise-edition
Статус: "Работает — не трогай, не дыши, не смотри"

Просто импортируй этот модуль, и весь твой код станет
неубиваемым. Серьёзно. Мы патчим всё: print, open, import,
деление, индексы, атрибуты, даже сам интерпретатор
начинает работать через костыли.

ПРИНЦИПЫ:
    1. Если что-то работает — добавь костыль для надёжности.
    2. Если что-то не работает — добавь ещё костылей.
    3. Если костылей больше 1000 — ты на верном пути.
"""

import sys
import os
import time
import random
import threading
import unittest

# ═══════════════════════════════════════════════════════════════
# КОСТЫЛЬНАЯ МАГИЯ ДЛЯ ТЕСТОВ
# ═══════════════════════════════════════════════════════════════

# Добавляем родительскую директорию в путь
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_TEST_DIR)
sys.path.insert(0, _PROJECT_DIR)

# Удаляем скомпилированные кеши (костыль против багов импорта)
for root, dirs, files in os.walk(_TEST_DIR):
    if '__pycache__' in dirs:
        dirs.remove('__pycache__')

# ═══════════════════════════════════════════════════════════════
# МЕТАДАННЫЕ ТЕСТОВ
# ═══════════════════════════════════════════════════════════════

__author__ = "Коллектив костылестроителей"
__email__ = "the1stplayergetready@gmail.com"
__version__ = "3.0.0b1"
__status__ = "Testing on crutches"
__coffee_level__ = "87%"

# ═══════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЕ ФИКСТУРЫ И ХЕЛПЕРЫ
# ═══════════════════════════════════════════════════════════════

class TestHelpers:
    """Вспомогательные функции для тестов."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Случайная строка для тестов."""
        import string
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    @staticmethod
    def random_int(min_val: int = 0, max_val: int = 1000) -> int:
        """Случайное число для тестов."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_email() -> str:
        """Случайный email для тестов."""
        return f"test_{TestHelpers.random_string(8)}@kostylpy.test"
    
    @staticmethod
    def wait_for(condition, timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Ждёт пока условие станет True."""
        start = time.time()
        while time.time() - start < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False

# ═══════════════════════════════════════════════════════════════
# АВТО-ОБНАРУЖЕНИЕ ТЕСТОВ (если pytest не справляется)
# ═══════════════════════════════════════════════════════════════

def discover_tests():
    """Находит все тесты в директории. Костыльно, но работает."""
    test_files = []
    for f in os.listdir(_TEST_DIR):
        if f.startswith('test_') and f.endswith('.py') and f != '__init__.py':
            test_files.append(f[:-3])  # убираем .py
    return sorted(test_files)

def run_all_tests():
    """Запускает все тесты без pytest. На случай если pytest не установлен."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module_name in discover_tests():
        try:
            module = __import__(f'tests.{module_name}', fromlist=[module_name])
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    suite.addTests(loader.loadTestsFromTestCase(obj))
        except Exception as e:
            print(f"⚠️ Не удалось загрузить тесты из {module_name}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

# ═══════════════════════════════════════════════════════════════
# ПРИВЕТСТВИЕ
# ═══════════════════════════════════════════════════════════════

_available_tests = discover_tests()

print(f"🧪 kostylpy tests v{__version__}")
print(f"   Директория: {_TEST_DIR}")
print(f"   Найдено тестовых модулей: {len(_available_tests)}")
for test_file in _available_tests:
    print(f"   • {test_file}")
print(f"   Кофе: {__coffee_level__}")
print(f"   Статус: {__status__}")
print()

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    'TestHelpers',
    'discover_tests',
    'run_all_tests',
    '_TEST_DIR',
    '_PROJECT_DIR',
]

# ═══════════════════════════════════════════════════════════════
# САМОДИАГНОСТИКА
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 ЗАПУСК ТЕСТОВ В КОСТЫЛЬНОМ РЕЖИМЕ")
    print("=" * 60)
    result = run_all_tests()
    
    if result.wasSuccessful():
        print("\n✅ Все тесты пройдены! Костыли работают!")
    else:
        print("\n❌ Некоторые тесты упали. Нужно больше костылей!")
        print(f"   Провалов: {len(result.failures)}")
        print(f"   Ошибок: {len(result.errors)}")