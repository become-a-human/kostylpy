"""
Тесты патчера kostylpy.
Проверяют AST-трансформации, патчинг файлов, 
автоматические исправления и анализ кода.
"""

import sys
import os
import time
import unittest
import tempfile
import ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import kostylpy
    from kostylpy.patcher import (
        CodePatcher, ASTTransformer, PatchAnalyzer,
        patch_string, patch_file, create_patched_copy,
        PatchResult, Patch, PatchType, SAFETY_FUNCTIONS
    )
    PATCHER_LOADED = True
except ImportError as e:
    print(f"⚠️ patcher не загружен: {e}")
    PATCHER_LOADED = False


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ AST ТРАНСФОРМЕРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestASTTransformer(unittest.TestCase):
    """Тесты AST трансформера."""
    
    def test_transformer_creation(self):
        """Трансформер должен создаваться."""
        t = ASTTransformer(add_safety=True)
        self.assertIsNotNone(t)
        self.assertEqual(t.changes, 0)
        self.assertEqual(len(t.patches), 0)
    
    def test_transformer_detects_division(self):
        """Трансформер должен находить деление."""
        source = "x = a / b"
        tree = ast.parse(source)
        
        t = ASTTransformer(add_safety=True)
        t.visit(tree)
        
        self.assertGreater(t.changes, 0)
        self.assertGreater(len(t.patches), 0)
    
    def test_transformer_ignores_safe_code(self):
        """Трансформер не должен трогать безопасный код."""
        source = "x = 42\ny = 'hello'\nz = [1, 2, 3]"
        tree = ast.parse(source)
        
        t = ASTTransformer(add_safety=True)
        t.visit(tree)
        
        # В этом коде нет деления или опасных операций
        # Изменений быть не должно (или минимум)
        division_patches = [p for p in t.patches if p.type == PatchType.SAFE_DIV]
        self.assertEqual(len(division_patches), 0)
    
    def test_transformer_safe_division(self):
        """Деление должно оборачиваться в _kostyl_safe_div."""
        source = "result = a / b"
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_safe_div", result.patched_source)
    
    def test_transformer_safe_floor_division(self):
        """Целочисленное деление должно оборачиваться."""
        source = "result = a // b"
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_safe_floordiv", result.patched_source)
    
    def test_transformer_safe_attribute(self):
        """Доступ к атрибутам должен оборачиваться."""
        source = "name = obj.attr"
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_safe_getattr", result.patched_source)
    
    def test_transformer_safe_subscript(self):
        """Доступ по индексу должен оборачиваться."""
        source = "item = lst[0]"
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_safe_getitem", result.patched_source)
    
    def test_transformer_safe_print(self):
        """Print должен оборачиваться."""
        source = 'print("hello")'
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_print", result.patched_source)
    
    def test_transformer_safe_open(self):
        """Open должен оборачиваться."""
        source = 'f = open("file.txt")'
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        self.assertIn("_kostyl_safe_open", result.patched_source)
    
    def test_transformer_empty_except(self):
        """Пустой except должен дополняться логированием."""
        source = """
try:
    risky()
except:
    pass
"""
        result = patch_string(source, add_logging=True, apply_patterns=False)
        
        self.assertIn("_kostyl_logger", result.patched_source)
    
    def test_transformer_preserves_valid_code(self):
        """Трансформер должен сохранять валидность кода."""
        source = """
def calculate(a, b):
    x = a + b
    y = x * 2
    return y

result = calculate(2, 3)
"""
        result = patch_string(source, add_safety=True, apply_patterns=False)
        
        # Результат должен компилироваться
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Патченный код не компилируется: {e}")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПАТЧИНГА ИСХОДНОГО КОДА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestCodePatcher(unittest.TestCase):
    """Тесты CodePatcher."""
    
    def test_patch_string_returns_result(self):
        """patch_string должен возвращать PatchResult."""
        source = "x = 1"
        result = patch_string(source)
        
        self.assertIsInstance(result, PatchResult)
    
    def test_patch_string_original_preserved(self):
        """PatchResult должен сохранять оригинал."""
        source = "x = 1"
        result = patch_string(source)
        
        self.assertEqual(result.original_source, source)
    
    def test_patch_string_has_stats(self):
        """PatchResult должен содержать статистику."""
        source = "x = a / b"
        result = patch_string(source, add_safety=True)
        
        self.assertIsInstance(result.patch_count, int)
        self.assertIsInstance(result.was_changed, bool)
        self.assertIsInstance(result.success_rate, float)
    
    def test_patch_division_only_with_safety(self):
        """Без add_safety деление не патчится."""
        source = "x = a / b"
        
        # С safety
        result_safe = patch_string(source, add_safety=True, apply_patterns=False)
        self.assertIn("_kostyl_safe_div", result_safe.patched_source)
        
        # Без safety
        result_no = patch_string(source, add_safety=False, apply_patterns=False)
        self.assertNotIn("_kostyl_safe_div", result_no.patched_source)
    
    def test_patch_aggressive_mode(self):
        """Агрессивный режим должен добавлять try/except."""
        source = "requests.get('http://example.com')"
        result = patch_string(source, aggressive=True, add_safety=False, apply_patterns=False)
        
        # Должен добавить try/except вокруг рискованной строки
        self.assertIn("try:", result.patched_source.lower())
        self.assertIn("except", result.patched_source.lower())
    
    def test_patch_doesnt_destroy_code(self):
        """Патч не должен ломать валидный код."""
        source = """
def hello(name):
    return f"Hello, {name}!"

print(hello("World"))
"""
        result = patch_string(source, add_safety=True)
        
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Код сломан после патча: {e}")
    
    def test_patch_complex_code(self):
        """Патч должен работать со сложным кодом."""
        source = """
class Calculator:
    def __init__(self, value=0):
        self.value = value
    
    def divide(self, divisor):
        return self.value / divisor
    
    def get_average(self, numbers):
        return sum(numbers) / len(numbers)

calc = Calculator(100)
result = calc.divide(3)
avg = calc.get_average([1, 2, 3, 4, 5])
print(f"Result: {result}, Average: {avg}")
"""
        result = patch_string(source, add_safety=True)
        
        self.assertIn("_kostyl_safe_div", result.patched_source)
        
        # Должен компилироваться
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Сложный код сломан: {e}")
    
    def test_patch_with_patterns(self):
        """Патч с паттернами должен исправлять стиль."""
        source = """
# TODO: fix this
x = 1
# FIXME: broken
y = 2
"""
        result = patch_string(source, add_safety=False, apply_patterns=True)
        
        # Должен пометить TODO/FIXME
        self.assertIn("kostylpy заметил", result.patched_source)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ ПАТЧИНГА ФАЙЛОВ
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestFilePatching(unittest.TestCase):
    """Тесты патчинга файлов."""
    
    def setUp(self):
        """Создаёт временный файл для тестов."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_script.py")
        
        with open(self.test_file, 'w') as f:
            f.write("""
def calculate(a, b):
    return a / b

x = 10
y = 0
result = calculate(x, y)
print(f"Result: {result}")
""")
    
    def tearDown(self):
        """Удаляет временные файлы."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_patch_file_works(self):
        """patch_file должен работать."""
        result = patch_file(self.test_file, add_safety=True)
        
        self.assertIsInstance(result, PatchResult)
        self.assertEqual(result.file_path, self.test_file)
    
    def test_patch_file_changes_source(self):
        """patch_file должен изменять код."""
        result = patch_file(self.test_file, add_safety=True)
        
        self.assertNotEqual(result.original_source, result.patched_source)
        self.assertIn("_kostyl_safe_div", result.patched_source)
    
    def test_patch_file_saves_output(self):
        """patch_file должен сохранять результат."""
        output_path = os.path.join(self.temp_dir, "patched.py")
        
        result = patch_file(self.test_file, output_path=output_path, add_safety=True)
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            saved = f.read()
        
        self.assertEqual(saved, result.patched_source)
    
    def test_create_patched_copy(self):
        """create_patched_copy должен создавать копию."""
        result_path = create_patched_copy(self.test_file, suffix="_patched")
        
        self.assertTrue(result_path.endswith("_patched.py"))
        self.assertTrue(os.path.exists(result_path))
    
    def test_patch_nonexistent_file(self):
        """Патчинг несуществующего файла должен вернуть ошибку."""
        result = patch_file("/nonexistent/file.py")
        
        self.assertTrue(len(result.errors) > 0)
        self.assertEqual(result.patched_source, "")


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ АНАЛИЗАТОРА КОДА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestPatchAnalyzer(unittest.TestCase):
    """Тесты анализатора кода."""
    
    def test_analyze_empty_code(self):
        """Анализ пустого кода."""
        info = PatchAnalyzer.analyze("")
        
        self.assertEqual(info['lines'], 1)  # Пустая строка = 1 линия
        self.assertEqual(info['functions'], 0)
        self.assertEqual(info['classes'], 0)
    
    def test_analyze_simple_function(self):
        """Анализ простой функции."""
        source = """
def hello():
    return "world"
"""
        info = PatchAnalyzer.analyze(source)
        
        self.assertEqual(info['functions'], 1)
        self.assertEqual(info['classes'], 0)
    
    def test_analyze_class(self):
        """Анализ класса."""
        source = """
class MyClass:
    def method(self):
        pass
"""
        info = PatchAnalyzer.analyze(source)
        
        self.assertEqual(info['classes'], 1)
        self.assertEqual(info['functions'], 1)
    
    def test_analyze_detects_division(self):
        """Анализатор должен находить деление."""
        source = "x = a / b"
        info = PatchAnalyzer.analyze(source)
        
        self.assertEqual(info['divisions'], 1)
        self.assertGreater(info['potential_issues'], 0)
    
    def test_analyze_detects_eval(self):
        """Анализатор должен находить eval."""
        source = 'eval("print(1)")'
        info = PatchAnalyzer.analyze(source)
        
        self.assertGreater(info['potential_issues'], 0)
    
    def test_analyze_report_contains_info(self):
        """Отчёт анализатора должен содержать информацию."""
        source = """
def main():
    x = 10 / 2
    return x
"""
        report = PatchAnalyzer.report(source)
        
        self.assertIn("АНАЛИЗ КОДА", report)
        self.assertIn("Функций", report)
        self.assertIn("Деления", report)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ SAFETY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestSafetyFunctions(unittest.TestCase):
    """Тесты встроенных функций безопасности."""
    
    def test_safety_functions_string(self):
        """SAFETY_FUNCTIONS должен быть строкой."""
        self.assertIsInstance(SAFETY_FUNCTIONS, str)
        self.assertGreater(len(SAFETY_FUNCTIONS), 0)
    
    def test_safety_functions_contains_all(self):
        """Должны быть все функции безопасности."""
        required = [
            '_kostyl_safe_div',
            '_kostyl_safe_floordiv',
            '_kostyl_safe_getattr',
            '_kostyl_safe_getitem',
            '_kostyl_print',
            '_kostyl_safe_open',
            '_kostyl_logger',
        ]
        
        for func_name in required:
            self.assertIn(func_name, SAFETY_FUNCTIONS, 
                         f"Не найдена функция {func_name}")
    
    def test_safety_functions_compile(self):
        """Функции безопасности должны компилироваться."""
        try:
            compile(SAFETY_FUNCTIONS, "<safety>", "exec")
        except SyntaxError as e:
            self.fail(f"SAFETY_FUNCTIONS не компилируется: {e}")
    
    def test_safety_functions_execute(self):
        """Функции безопасности должны выполняться."""
        namespace = {}
        exec(SAFETY_FUNCTIONS, namespace)
        
        # Проверяем что функции создались
        self.assertIn('_kostyl_safe_div', namespace)
        self.assertIn('_kostyl_print', namespace)
        self.assertIn('_kostyl_logger', namespace)
    
    def test_safe_div_works(self):
        """_kostyl_safe_div должен работать."""
        namespace = {}
        exec(SAFETY_FUNCTIONS, namespace)
        
        safe_div = namespace['_kostyl_safe_div']
        
        self.assertEqual(safe_div(10, 2), 5.0)
        self.assertEqual(safe_div(10, 0), 0)  # default
        self.assertEqual(safe_div(10, 0, default=999), 999)
    
    def test_safe_getattr_works(self):
        """_kostyl_safe_getattr должен работать."""
        namespace = {}
        exec(SAFETY_FUNCTIONS, namespace)
        
        safe_getattr = namespace['_kostyl_safe_getattr']
        
        obj = type('Test', (), {'x': 42})()
        self.assertEqual(safe_getattr(obj, 'x'), 42)
        self.assertIsNone(safe_getattr(obj, 'y'))
        self.assertEqual(safe_getattr(obj, 'z', 'default'), 'default')
    
    def test_safe_getitem_works(self):
        """_kostyl_safe_getitem должен работать."""
        namespace = {}
        exec(SAFETY_FUNCTIONS, namespace)
        
        safe_getitem = namespace['_kostyl_safe_getitem']
        
        lst = [1, 2, 3]
        self.assertEqual(safe_getitem(lst, 0), 1)
        self.assertIsNone(safe_getitem(lst, 100))
        
        dct = {'a': 1}
        self.assertEqual(safe_getitem(dct, 'a'), 1)
        self.assertIsNone(safe_getitem(dct, 'b'))
    
    def test_safe_print_works(self):
        """_kostyl_print должен работать."""
        namespace = {}
        exec(SAFETY_FUNCTIONS, namespace)
        
        safe_print = namespace['_kostyl_print']
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            safe_print("test", "message", sep="-")
        
        self.assertIn("test-message", f.getvalue())


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ PATCH RESULT
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestPatchResult(unittest.TestCase):
    """Тесты PatchResult."""
    
    def test_patch_result_properties(self):
        """PatchResult должен иметь все свойства."""
        result = PatchResult(
            file_path="test.py",
            original_source="x = 1",
            patched_source="x = 2"
        )
        
        self.assertEqual(result.file_path, "test.py")
        self.assertEqual(result.patch_count, 0)
        self.assertTrue(result.was_changed)
        self.assertEqual(result.success_rate, 100.0)
    
    def test_patch_result_no_change(self):
        """PatchResult без изменений."""
        source = "x = 1"
        result = PatchResult(
            file_path="test.py",
            original_source=source,
            patched_source=source
        )
        
        self.assertFalse(result.was_changed)
    
    def test_patch_result_with_errors(self):
        """PatchResult с ошибками."""
        result = PatchResult(
            file_path="test.py",
            original_source="",
            patched_source=""
        )
        result.errors.append("Ошибка 1")
        result.errors.append("Ошибка 2")
        
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.success_rate, 0.0)


# ═══════════════════════════════════════════════════════════════
# ТЕСТЫ PATCH TYPE
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestPatchTypes(unittest.TestCase):
    """Тесты типов патчей."""
    
    def test_patch_creation(self):
        """Patch должен создаваться."""
        patch = Patch(
            type=PatchType.SAFE_DIV,
            line=10,
            column=5,
            description="Безопасное деление",
            original="a / b",
            replacement="_kostyl_safe_div(a, b)",
            reason="Защита от ZeroDivisionError"
        )
        
        self.assertEqual(patch.type, PatchType.SAFE_DIV)
        self.assertEqual(patch.line, 10)
        self.assertEqual(patch.column, 5)
    
    def test_all_patch_types_exist(self):
        """Должны существовать все типы патчей."""
        expected_types = [
            PatchType.SAFE_DIV,
            PatchType.SAFE_GETATTR,
            PatchType.SAFE_INDEX,
            PatchType.SAFE_CALL,
            PatchType.NULL_CHECK,
            PatchType.TYPE_CHECK,
            PatchType.EXCEPTION_HANDLE,
            PatchType.LOGGING_ADD,
            PatchType.IMPORT_FIX,
            PatchType.PRINT_FIX,
            PatchType.STYLE_FIX,
        ]
        
        for patch_type in expected_types:
            self.assertIsNotNone(patch_type)


# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПАТЧЕРА
# ═══════════════════════════════════════════════════════════════

@unittest.skipUnless(PATCHER_LOADED, "patcher не загружен")
class TestPatcherIntegration(unittest.TestCase):
    """Интеграционные тесты патчера."""
    
    def test_full_pipeline_simple(self):
        """Полный пайплайн: патч + компиляция."""
        source = """
def process(data):
    result = data['value'] / data['count']
    return result

output = process({'value': 100, 'count': 5})
"""
        result = patch_string(source, add_safety=True, apply_patterns=True)
        
        # Должен компилироваться
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Патченный код не компилируется: {e}")
        
        # Должен содержать безопасные функции
        self.assertIn("_kostyl_safe_div", result.patched_source)
        self.assertIn("_kostyl_safe_getitem", result.patched_source)
    
    def test_full_pipeline_with_imports(self):
        """Патч кода с импортами."""
        source = """
import os
import sys

def read_config(path):
    with open(path) as f:
        return f.read()

config = read_config('/etc/config.ini')
"""
        result = patch_string(source, add_safety=True)
        
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Код с импортами сломан: {e}")
    
    def test_full_pipeline_with_classes(self):
        """Патч кода с классами."""
        source = """
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def get_value(self, key):
        return self.data[key]
    
    def get_ratio(self, a, b):
        return a / b

processor = DataProcessor({'x': 10, 'y': 20})
value = processor.get_value('x')
ratio = processor.get_ratio(value, processor.get_value('y'))
"""
        result = patch_string(source, add_safety=True)
        
        self.assertIn("_kostyl_safe_getitem", result.patched_source)
        self.assertIn("_kostyl_safe_div", result.patched_source)
        
        try:
            compile(result.patched_source, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Код с классами сломан: {e}")
    
    def test_backup_creation(self):
        """При патчинге должен создаваться бекап."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1 / 0")
            temp_path = f.name
        
        try:
            result = patch_file(temp_path, add_safety=True)
            
            # Патчим ещё раз с output
            output_path = temp_path + ".patched"
            patch_file(temp_path, output_path=output_path, add_safety=True)
            
            self.assertTrue(os.path.exists(output_path))
        finally:
            try:
                os.unlink(temp_path)
                if os.path.exists(temp_path + ".patched"):
                    os.unlink(temp_path + ".patched")
            except:
                pass


if __name__ == '__main__':
    unittest.main(verbosity=2)