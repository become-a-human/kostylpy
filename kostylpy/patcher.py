"""
AST Патчер kostylpy.
Анализирует и модифицирует Python-код на уровне AST.
Находит проблемные места и автоматически закостыливает их.

Содержит:
- ASTTransformer — трансформер AST
- CodePatcher — патчер исходного кода
- PatchAnalyzer — анализатор кода
- AutoFixer — автоматическое исправление
- PatchReport — отчёт о патчинге
- Функции для патчинга файлов и строк кода
- Интеграция с patterns.py
"""

import ast
import sys
import os
import re
import textwrap
import tokenize
import io
from typing import Any, Callable, Optional, Dict, List, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum, auto

# Импортируем константы
try:
    from .constants import Emoji, Colors
except ImportError:
    class Emoji:
        KOSTYL = "🦿"
        FIX = "🩹"
        ERROR = "❌"
        SUCCESS = "✅"
        WARNING = "⚠️"
        BUG = "🐛"
        CODE = "📝"
    class Colors:
        @staticmethod
        def green(t): return t
        @staticmethod
        def red(t): return t
        @staticmethod
        def yellow(t): return t
        RESET = ""

# Импортируем паттерны
try:
    from .patterns import patterns as pattern_registry, PatternMatch
except ImportError:
    pattern_registry = None
    PatternMatch = None

# Импортируем состояние
try:
    from . import _kostyl_state, KostylSeverity, KostylCategory
except ImportError:
    _kostyl_state = None

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════

class PatchType(Enum):
    """Тип патча."""
    SAFE_DIV = "безопасное деление"
    SAFE_GETATTR = "безопасный getattr"
    SAFE_INDEX = "безопасный индекс"
    SAFE_CALL = "безопасный вызов"
    NULL_CHECK = "проверка на None"
    TYPE_CHECK = "проверка типа"
    EXCEPTION_HANDLE = "обработка исключений"
    LOGGING_ADD = "добавление логирования"
    IMPORT_FIX = "исправление импорта"
    PRINT_FIX = "исправление print"
    STYLE_FIX = "исправление стиля"

@dataclass
class PatchResult:
    """Результат патчинга."""
    file_path: str
    original_source: str
    patched_source: str
    patches: List['Patch'] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def patch_count(self) -> int:
        return len(self.patches)
    
    @property
    def was_changed(self) -> bool:
        return self.original_source != self.patched_source
    
    @property
    def success_rate(self) -> float:
        total = self.patch_count + len(self.errors)
        if total == 0:
            return 100.0
        return (self.patch_count / total) * 100

@dataclass
class Patch:
    """Один патч."""
    type: PatchType
    line: int
    column: int
    description: str
    original: str = ""
    replacement: str = ""
    reason: str = ""

# ═══════════════════════════════════════════════════════════════
# AST ТРАНСФОРМЕР
# ═══════════════════════════════════════════════════════════════

class ASTTransformer(ast.NodeTransformer):
    """
    Трансформирует AST дерево.
    Добавляет костыли в критические места.
    """
    
    def __init__(self, add_safety: bool = True, add_logging: bool = False):
        super().__init__()
        self.add_safety = add_safety
        self.add_logging = add_logging
        self._patches: List[Patch] = []
        self._changes = 0
    
    @property
    def patches(self) -> List[Patch]:
        return self._patches
    
    @property
    def changes(self) -> int:
        return self._changes
    
    # ═══════════════════════════════════════════
    # ПОСЕТИТЕЛИ УЗЛОВ
    # ═══════════════════════════════════════════
    
    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        """Трансформирует бинарные операции."""
        # Деление → безопасное деление
        if isinstance(node.op, ast.Div) and self.add_safety:
            return self._make_safe_division(node)
        
        # Целочисленное деление тоже
        if isinstance(node.op, ast.FloorDiv) and self.add_safety:
            return self._make_safe_floor_division(node)
        
        return self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Трансформирует доступ к атрибутам."""
        if self.add_safety:
            return self._make_safe_attribute(node)
        return self.generic_visit(node)
    
    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        """Трансформирует доступ по индексу."""
        if self.add_safety:
            return self._make_safe_subscript(node)
        return self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Трансформирует вызовы функций."""
        # Проверяем print
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            return self._make_safe_print(node)
        
        # Проверяем open
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            return self._make_safe_open(node)
        
        return self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        """Трансформирует обработчики исключений."""
        # Добавляем логирование в пустые except
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return self._add_exception_logging(node)
        
        return self.generic_visit(node)
    
    # ═══════════════════════════════════════════
    # ГЕНЕРАТОРЫ БЕЗОПАСНЫХ КОНСТРУКЦИЙ
    # ═══════════════════════════════════════════
    
    def _make_safe_division(self, node: ast.BinOp) -> ast.Call:
        """Оборачивает деление в безопасную функцию."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.SAFE_DIV,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="Деление обёрнуто в _kostyl_safe_div()",
            reason="Защита от ZeroDivisionError"
        ))
        
        return ast.Call(
            func=ast.Name(id='_kostyl_safe_div', ctx=ast.Load()),
            args=[node.left, node.right],
            keywords=[]
        )
    
    def _make_safe_floor_division(self, node: ast.BinOp) -> ast.Call:
        """Оборачивает целочисленное деление."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.SAFE_DIV,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="Целочисленное деление обёрнуто в _kostyl_safe_floordiv()",
            reason="Защита от ZeroDivisionError"
        ))
        
        return ast.Call(
            func=ast.Name(id='_kostyl_safe_floordiv', ctx=ast.Load()),
            args=[node.left, node.right],
            keywords=[]
        )
    
    def _make_safe_attribute(self, node: ast.Attribute) -> ast.Call:
        """Оборачивает доступ к атрибуту."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.SAFE_GETATTR,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description=f"Доступ к атрибуту '{node.attr}' обёрнут",
            reason="Защита от AttributeError"
        ))
        
        return ast.Call(
            func=ast.Name(id='_kostyl_safe_getattr', ctx=ast.Load()),
            args=[
                node.value,
                ast.Constant(value=node.attr),
                ast.Constant(value=None)
            ],
            keywords=[]
        )
    
    def _make_safe_subscript(self, node: ast.Subscript) -> ast.Call:
        """Оборачивает доступ по индексу."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.SAFE_INDEX,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="Доступ по индексу обёрнут",
            reason="Защита от IndexError/KeyError"
        ))
        
        return ast.Call(
            func=ast.Name(id='_kostyl_safe_getitem', ctx=ast.Load()),
            args=[
                node.value,
                node.slice,
                ast.Constant(value=None)
            ],
            keywords=[]
        )
    
    def _make_safe_print(self, node: ast.Call) -> ast.Call:
        """Оборачивает print."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.PRINT_FIX,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="print обёрнут в безопасную версию",
            reason="Защита от ошибок вывода"
        ))
        
        # _kostyl_print(*args)
        return ast.Call(
            func=ast.Name(id='_kostyl_print', ctx=ast.Load()),
            args=node.args,
            keywords=node.keywords
        )
    
    def _make_safe_open(self, node: ast.Call) -> ast.Call:
        """Оборачивает open."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.SAFE_CALL,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="open() обёрнут в _kostyl_safe_open()",
            reason="Защита от FileNotFoundError"
        ))
        
        return ast.Call(
            func=ast.Name(id='_kostyl_safe_open', ctx=ast.Load()),
            args=node.args,
            keywords=node.keywords
        )
    
    def _add_exception_logging(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        """Добавляет логирование в except."""
        self._changes += 1
        self._patches.append(Patch(
            type=PatchType.EXCEPTION_HANDLE,
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            description="В except добавлено логирование",
            reason="Пустой except — плохая практика"
        ))
        
        log_call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='_kostyl_logger', ctx=ast.Load()),
                    attr='warning',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=f"Исключение перехвачено: {ast.dump(node)}")],
                keywords=[]
            )
        )
        
        node.body = [log_call] + node.body
        return node

# ═══════════════════════════════════════════════════════════════
# ПАТЧЕР КОДА
# ═══════════════════════════════════════════════════════════════

class CodePatcher:
    """
    Патчит исходный код.
    Комбинирует AST-трансформации и текстовые замены.
    """
    
    def __init__(
        self,
        add_safety: bool = True,
        add_logging: bool = False,
        apply_patterns: bool = True,
        aggressive: bool = False,
    ):
        self.add_safety = add_safety
        self.add_logging = add_logging
        self.apply_patterns = apply_patterns
        self.aggressive = aggressive
        
        self._ast_transformer = ASTTransformer(
            add_safety=add_safety,
            add_logging=add_logging
        )
    
    def patch_source(self, source: str, file_path: str = "<string>") -> PatchResult:
        """Патчит исходный код."""
        result = PatchResult(
            file_path=file_path,
            original_source=source,
            patched_source=source
        )
        
        try:
            # Шаг 1: AST трансформация
            if self.add_safety or self.add_logging:
                result = self._apply_ast_patches(result)
            
            # Шаг 2: Текстовые паттерны
            if self.apply_patterns and pattern_registry:
                result = self._apply_pattern_patches(result)
            
            # Шаг 3: Дополнительные проверки
            if self.aggressive:
                result = self._apply_aggressive_patches(result)
            
        except SyntaxError as e:
            result.errors.append(f"Синтаксическая ошибка: {e}")
        except Exception as e:
            result.errors.append(f"Ошибка патчинга: {e}")
        
        return result
    
    def _apply_ast_patches(self, result: PatchResult) -> PatchResult:
        """Применяет AST-трансформации."""
        try:
            tree = ast.parse(result.patched_source)
            transformed = self._ast_transformer.visit(tree)
            ast.fix_missing_locations(transformed)
            
            try:
                result.patched_source = ast.unparse(transformed)
            except AttributeError:
                # Python < 3.9
                import astor
                result.patched_source = astor.to_source(transformed)
            
            result.patches.extend(self._ast_transformer.patches)
            
            if self._ast_transformer.changes > 0:
                if _kostyl_state:
                    _kostyl_state.record_kostyl(
                        KostylSeverity.COSMETIC,
                        KostylCategory.UNKNOWN,
                        f"AST патчер: {self._ast_transformer.changes} изменений"
                    )
        except Exception as e:
            result.errors.append(f"Ошибка AST-трансформации: {e}")
        
        return result
    
    def _apply_pattern_patches(self, result: PatchResult) -> PatchResult:
        """Применяет текстовые паттерны."""
        try:
            from .patterns import scan_code, apply_fixes
            
            matches = scan_code(result.patched_source, result.file_path)
            
            if matches:
                result.patched_source = apply_fixes(
                    result.patched_source,
                    matches,
                    auto_apply=True
                )
                
                for match in matches:
                    if match.auto_fix:
                        result.patches.append(Patch(
                            type=PatchType.STYLE_FIX,
                            line=match.line_number,
                            column=match.column,
                            description=match.message,
                            original=match.matched_text,
                            replacement=match.auto_fix or "",
                            reason=match.suggestion
                        ))
        except Exception as e:
            result.warnings.append(f"Ошибка применения паттернов: {e}")
        
        return result
    
    def _apply_aggressive_patches(self, result: PatchResult) -> PatchResult:
        """Применяет агрессивные патчи."""
        lines = result.patched_source.split('\n')
        patched_lines = []
        
        for i, line in enumerate(lines):
            # Добавляем try/except вокруг подозрительных строк
            if self._is_risky_line(line) and not line.strip().startswith('try:'):
                indent = len(line) - len(line.lstrip())
                patched_lines.append(' ' * indent + 'try:')
                patched_lines.append(line)
                patched_lines.append(' ' * indent + 'except Exception as _kostyl_e:')
                patched_lines.append(' ' * (indent + 4) + 'pass  # kostylpy: aggressive patch')
            else:
                patched_lines.append(line)
        
        result.patched_source = '\n'.join(patched_lines)
        return result
    
    def _is_risky_line(self, line: str) -> bool:
        """Определяет, является ли строка рискованной."""
        risky_patterns = [
            r'\.execute\s*\(',
            r'\.read\s*\(',
            r'\.write\s*\(',
            r'\.send\s*\(',
            r'\.connect\s*\(',
            r'requests\.\w+',
            r'urllib',
            r'subprocess',
            r'os\.system',
            r'os\.popen',
        ]
        
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""'):
            return False
        
        for pattern in risky_patterns:
            if re.search(pattern, stripped):
                return True
        
        return False
    
    def patch_file(self, filepath: str, output_path: Optional[str] = None) -> PatchResult:
        """Патчит файл."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            result = PatchResult(
                file_path=filepath,
                original_source="",
                patched_source=""
            )
            result.errors.append(f"Не удалось прочитать файл: {e}")
            return result
        
        result = self.patch_source(source, filepath)
        
        # Сохраняем результат если указан output_path
        if output_path and result.was_changed:
            try:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.patched_source)
            except Exception as e:
                result.errors.append(f"Не удалось сохранить файл: {e}")
        
        return result

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ БЕЗОПАСНОСТИ (вставляются в патченный код)
# ═══════════════════════════════════════════════════════════════

SAFETY_FUNCTIONS = '''
# ═══════════════════════════════════════════
# ВСТАВЛЕНО KOSTYLPY PATCHER
# ═══════════════════════════════════════════

def _kostyl_safe_div(a, b, default=0):
    """Безопасное деление."""
    try:
        return a / b
    except ZeroDivisionError:
        return default

def _kostyl_safe_floordiv(a, b, default=0):
    """Безопасное целочисленное деление."""
    try:
        return a // b
    except ZeroDivisionError:
        return default

def _kostyl_safe_getattr(obj, attr, default=None):
    """Безопасный доступ к атрибуту."""
    try:
        return getattr(obj, attr)
    except (AttributeError, Exception):
        return default

def _kostyl_safe_getitem(obj, key, default=None):
    """Безопасный доступ по индексу/ключу."""
    try:
        return obj[key]
    except (IndexError, KeyError, TypeError):
        return default

def _kostyl_print(*args, **kwargs):
    """Безопасный print."""
    try:
        print(*args, **kwargs)
    except Exception:
        import sys
        sys.stderr.write("KOSTYLPY: print failed\\n")

def _kostyl_safe_open(*args, **kwargs):
    """Безопасный open."""
    try:
        return open(*args, **kwargs)
    except FileNotFoundError:
        import io
        return io.StringIO("")
    except Exception:
        import io
        return io.StringIO("")

import logging as _logging
_kostyl_logger = _logging.getLogger("kostylpy")
_kostyl_logger.addHandler(_logging.NullHandler())

# ═══════════════════════════════════════════
'''

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ ДЛЯ ПАТЧИНГА
# ═══════════════════════════════════════════════════════════════

def patch_string(source: str, **kwargs) -> PatchResult:
    """Патчит строку с кодом."""
    patcher = CodePatcher(**kwargs)
    return patcher.patch_source(source)

def patch_file(filepath: str, output_path: Optional[str] = None, **kwargs) -> PatchResult:
    """Патчит файл."""
    patcher = CodePatcher(**kwargs)
    return patcher.patch_file(filepath, output_path)

def patch_directory(
    directory: str,
    pattern: str = "*.py",
    recursive: bool = True,
    backup: bool = True,
    **kwargs
) -> List[PatchResult]:
    """Патчит все Python-файлы в директории."""
    import fnmatch
    
    results = []
    patcher = CodePatcher(**kwargs)
    
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            filepath = os.path.join(root, filename)
            
            # Пропускаем уже патченные файлы
            if filepath.endswith('_kostylized.py') or filepath.endswith('_backup.py'):
                continue
            
            output = filepath
            
            if backup:
                # Делаем бекап
                backup_path = filepath + '.kostyl_backup'
                try:
                    import shutil
                    shutil.copy2(filepath, backup_path)
                except:
                    pass
            
            result = patcher.patch_file(filepath, output)
            results.append(result)
        
        if not recursive:
            break
    
    return results

def create_patched_copy(filepath: str, suffix: str = "_kostylized") -> str:
    """Создаёт патченную копию файла."""
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    
    output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
    
    result = patch_file(filepath, output_path)
    
    if result.was_changed:
        print(f"{Emoji.SUCCESS} Создан патченный файл: {output_path}")
        print(f"   Патчей применено: {result.patch_count}")
        return output_path
    else:
        print(f"{Emoji.WARNING} Файл не требует патчей: {filepath}")
        return filepath

# ═══════════════════════════════════════════════════════════════
# АНАЛИЗАТОР КОДА
# ═══════════════════════════════════════════════════════════════

class PatchAnalyzer:
    """Анализирует код перед патчингом."""
    
    @staticmethod
    def analyze(source: str) -> Dict[str, Any]:
        """Анализирует исходный код."""
        info = {
            'lines': len(source.split('\n')),
            'chars': len(source),
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'try_blocks': 0,
            'except_blocks': 0,
            'divisions': 0,
            'potential_issues': 0,
        }
        
        try:
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    info['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    info['classes'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    info['imports'] += 1
                elif isinstance(node, ast.Try):
                    info['try_blocks'] += 1
                elif isinstance(node, ast.ExceptHandler):
                    info['except_blocks'] += 1
                elif isinstance(node, ast.BinOp):
                    if isinstance(node.op, (ast.Div, ast.FloorDiv)):
                        info['divisions'] += 1
                        info['potential_issues'] += 1
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ('eval', 'exec', 'compile'):
                            info['potential_issues'] += 1
        except:
            pass
        
        return info
    
    @staticmethod
    def report(source: str) -> str:
        """Генерирует отчёт об анализе."""
        info = PatchAnalyzer.analyze(source)
        
        report = f"""
{Emoji.CODE} ═══════════════════════════════════════
{Emoji.CODE} АНАЛИЗ КОДА
{Emoji.CODE} ═══════════════════════════════════════

Строк: {info['lines']}
Символов: {info['chars']}
Функций: {info['functions']}
Классов: {info['classes']}
Импортов: {info['imports']}
Try-блоков: {info['try_blocks']}
Except-блоков: {info['except_blocks']}
Деления: {info['divisions']}
Потенциальных проблем: {info['potential_issues']}

{Emoji.CODE} ═══════════════════════════════════════
"""
        return report

# ═══════════════════════════════════════════════════════════════
# ЭКСПОРТ
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Основные классы
    'ASTTransformer',
    'CodePatcher',
    'PatchAnalyzer',
    
    # Результаты
    'PatchResult',
    'Patch',
    'PatchType',
    
    # Функции
    'patch_string',
    'patch_file',
    'patch_directory',
    'create_patched_copy',
    
    # Строка с функциями безопасности
    'SAFETY_FUNCTIONS',
]

print(f"{Emoji.FIX} kostylpy.patcher: AST-патчер загружен")
print(f"   Функции: patch_string, patch_file, patch_directory, create_patched_copy")
print(f"   Трансформер: ASTTransformer ({len(ASTTransformer.__dict__)} методов)")