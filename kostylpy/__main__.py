"""
CLI интерфейс kostylpy.
Запускается при вызове python -m kostylpy.
Позволяет запускать, патчить, сканировать и костылизировать файлы.

Использование:
    python -m kostylpy run <файл>       — запустить с костылями
    python -m kostylpy patch <файл>      — пропатчить файл
    python -m kostylpy scan <файл>       — просканировать на проблемы
    python -m kostylpy check             — проверить здоровье
    python -m kostylpy report            — показать отчёт
    python -m kostylpy version           — версия
    python -m kostylpy help              — справка
"""

import sys
import os
import time
import argparse
import traceback
from typing import Optional, List

# Добавляем родительскую директорию в путь (на случай если запускаем как скрипт)
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'kostylpy'

# Импортируем ядро
try:
    from .core import kostylpy, KOSTYLPY_VERSION, Emoji, Colors
    from .patcher import patch_file, patch_directory, create_patched_copy, PatchAnalyzer
    from .patterns import scan_file, patterns as pattern_registry
except ImportError:
    # Упрощённый режим если не можем импортировать
    print("kostylpy: ошибка импорта модулей", file=sys.stderr)
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ CLI
# ═══════════════════════════════════════════════════════════════

def cmd_run(args):
    """Запускает файл с костылями."""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print(f"{Emoji.ERROR} Файл не найден: {filepath}")
        return 1
    
    print(f"{Emoji.KOSTYL} Запуск с костылями: {filepath}")
    print(f"{'='*50}")
    
    # Читаем файл
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Добавляем функции безопасности если нужно
    if args.safe:
        from .patcher import SAFETY_FUNCTIONS
        source = SAFETY_FUNCTIONS + '\n' + source
    
    # Создаём глобальное окружение
    globals_dict = {
        '__name__': '__main__',
        '__file__': filepath,
        '__builtins__': __builtins__,
    }
    
    try:
        # Компилируем
        code = compile(source, filepath, 'exec')
        
        # Выполняем
        exec(code, globals_dict)
        
        print(f"\n{'='*50}")
        print(f"{Emoji.SUCCESS} Выполнение завершено")
        return 0
        
    except SystemExit as e:
        return e.code if e.code is not None else 0
    except Exception as e:
        print(f"\n{Emoji.ERROR} Ошибка выполнения: {type(e).__name__}: {e}")
        if args.traceback:
            traceback.print_exc()
        print(f"{Emoji.KOSTYL} Но мы не падаем!")
        return 1

def cmd_patch(args):
    """Патчит файл(ы)."""
    if os.path.isdir(args.path):
        print(f"{Emoji.FIX} Патчинг директории: {args.path}")
        results = patch_directory(
            args.path,
            recursive=not args.no_recursive,
            backup=not args.no_backup,
            aggressive=args.aggressive,
        )
        
        total_patches = sum(r.patch_count for r in results)
        total_errors = sum(len(r.errors) for r in results)
        
        print(f"\n{Emoji.SUCCESS} Патчинг завершён")
        print(f"   Файлов обработано: {len(results)}")
        print(f"   Патчей применено: {total_patches}")
        if total_errors:
            print(f"   Ошибок: {total_errors}")
    
    else:
        print(f"{Emoji.FIX} Патчинг файла: {args.path}")
        
        output = args.output
        if not output and not args.in_place:
            output = args.path.replace('.py', '_kostylized.py')
        elif args.in_place:
            output = args.path
        
        result = patch_file(
            args.path,
            output_path=output,
            aggressive=args.aggressive,
        )
        
        if result.errors:
            print(f"\n{Emoji.ERROR} Ошибки:")
            for error in result.errors:
                print(f"  • {error}")
        
        print(f"\n{Emoji.SUCCESS} Патчинг завершён")
        print(f"   Патчей применено: {result.patch_count}")
        if output:
            print(f"   Результат сохранён в: {output}")
    
    return 0

def cmd_scan(args):
    """Сканирует файл на проблемы."""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print(f"{Emoji.ERROR} Файл не найден: {filepath}")
        return 1
    
    print(f"{Emoji.BUG} Сканирование: {filepath}")
    
    # Анализ кода
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # AST анализ
    print(PatchAnalyzer.report(source))
    
    # Поиск паттернов
    if not args.no_patterns:
        print(f"\n{Emoji.BUG} Поиск проблемных паттернов...")
        matches = scan_file(filepath)
        
        if matches:
            # Группируем по серьёзности
            from .patterns import PatternSeverity
            
            by_severity = {}
            for match in matches:
                sev = match.severity
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(match)
            
            for severity in PatternSeverity:
                if severity in by_severity:
                    sev_matches = by_severity[severity]
                    print(f"\n  {severity.value[1]} {severity.value[2]} ({len(sev_matches)}):")
                    for match in sev_matches[:10]:
                        print(f"    Строка {match.line_number}: {match.message[:100]}")
                    if len(sev_matches) > 10:
                        print(f"    ... и ещё {len(sev_matches) - 10}")
            
            print(f"\n{Emoji.INFO} Всего найдено проблем: {len(matches)}")
        else:
            print(f"\n{Emoji.SUCCESS} Проблем не найдено (подозрительно)")
    
    return 0

def cmd_check(args):
    """Проверяет здоровье kostylpy."""
    print(f"{Emoji.KOSTYL} Проверка здоровья kostylpy...")
    print()
    
    health = kostylpy.health_check()
    
    all_ok = True
    for component, status in health.items():
        icon = Emoji.SUCCESS if status else Emoji.ERROR
        print(f"  {icon} {component}: {'OK' if status else 'ПРОБЛЕМА'}")
        if not status:
            all_ok = False
    
    print()
    if all_ok:
        print(f"{Emoji.SUCCESS} Все системы в порядке!")
    else:
        print(f"{Emoji.WARNING} Некоторые системы не загружены. Работаем в деградированном режиме.")
    
    print(f"\nСтатус ядра: {kostylpy.status}")
    print(f"Время работы: {kostylpy.uptime:.1f}с")
    print(f"Загружено модулей: {len(kostylpy.loaded_modules())}")
    
    return 0 if all_ok else 1

def cmd_report(args):
    """Показывает полный отчёт."""
    print(kostylpy.report())
    return 0

def cmd_version(args):
    """Показывает версию."""
    from .constants import get_kostylpy_banner
    print(get_kostylpy_banner())
    return 0

def cmd_help(args):
    """Показывает справку."""
    help_text = f"""
{Emoji.KOSTYL} KOSTYLPY CLI v{KOSTYLPY_VERSION}

ИСПОЛЬЗОВАНИЕ:
    python -m kostylpy <команда> [аргументы]

КОМАНДЫ:

  {Colors.GREEN}run{Colors.RESET} <файл> [--safe] [--traceback]
      Запускает Python-файл с костылями.
      --safe      Добавить функции безопасности
      --traceback Показать traceback при ошибке

  {Colors.GREEN}patch{Colors.RESET} <путь> [--output <файл>] [--in-place] [--aggressive] [--no-backup]
      Патчит файл или директорию.
      --output    Путь для сохранения результата
      --in-place  Изменить файл на месте
      --aggressive Агрессивный режим (больше костылей!)
      --no-backup Не создавать бекап

  {Colors.GREEN}scan{Colors.RESET} <файл> [--no-patterns]
      Сканирует файл на проблемы.
      --no-patterns Только AST-анализ

  {Colors.GREEN}check{Colors.RESET}
      Проверяет здоровье kostylpy.

  {Colors.GREEN}report{Colors.RESET}
      Показывает полный отчёт.

  {Colors.GREEN}version{Colors.RESET}
      Показывает версию.

  {Colors.GREEN}help{Colors.RESET}
      Показывает эту справку.

ПРИМЕРЫ:
    python -m kostylpy run my_script.py
    python -m kostylpy scan my_script.py
    python -m kostylpy patch my_script.py --output fixed.py
    python -m kostylpy patch ./project --aggressive
    python -m kostylpy check
"""
    print(help_text)
    return 0

# ═══════════════════════════════════════════════════════════════
# ПАРСЕР АРГУМЕНТОВ
# ═══════════════════════════════════════════════════════════════

def create_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog='kostylpy',
        description=f'{Emoji.KOSTYL} Kostylpy CLI v{KOSTYLPY_VERSION}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # run
    run_parser = subparsers.add_parser('run', help='Запустить файл с костылями')
    run_parser.add_argument('file', help='Python файл для запуска')
    run_parser.add_argument('--safe', action='store_true', help='Добавить функции безопасности')
    run_parser.add_argument('--traceback', action='store_true', help='Показать traceback')
    run_parser.set_defaults(func=cmd_run)
    
    # patch
    patch_parser = subparsers.add_parser('patch', help='Пропатчить файл или директорию')
    patch_parser.add_argument('path', help='Файл или директория')
    patch_parser.add_argument('--output', '-o', help='Выходной файл')
    patch_parser.add_argument('--in-place', '-i', action='store_true', help='Изменить на месте')
    patch_parser.add_argument('--aggressive', '-a', action='store_true', help='Агрессивный режим')
    patch_parser.add_argument('--no-backup', action='store_true', help='Не создавать бекап')
    patch_parser.add_argument('--no-recursive', action='store_true', help='Не рекурсивно (для директорий)')
    patch_parser.set_defaults(func=cmd_patch)
    
    # scan
    scan_parser = subparsers.add_parser('scan', help='Просканировать файл')
    scan_parser.add_argument('file', help='Python файл для сканирования')
    scan_parser.add_argument('--no-patterns', action='store_true', help='Только AST анализ')
    scan_parser.set_defaults(func=cmd_scan)
    
    # check
    check_parser = subparsers.add_parser('check', help='Проверить здоровье')
    check_parser.set_defaults(func=cmd_check)
    
    # report
    report_parser = subparsers.add_parser('report', help='Показать отчёт')
    report_parser.set_defaults(func=cmd_report)
    
    # version
    version_parser = subparsers.add_parser('version', help='Показать версию')
    version_parser.set_defaults(func=cmd_version)
    
    # help
    help_parser = subparsers.add_parser('help', help='Показать справку')
    help_parser.set_defaults(func=cmd_help)
    
    return parser

# ═══════════════════════════════════════════════════════════════
# ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════

def main(args: Optional[List[str]] = None) -> int:
    """Главная функция CLI."""
    
    # Если нет аргументов — показываем справку
    if args is None:
        args = sys.argv[1:]
    
    if not args:
        cmd_help(None)
        return 0
    
    parser = create_parser()
    
    try:
        parsed = parser.parse_args(args)
        
        if hasattr(parsed, 'func'):
            return parsed.func(parsed)
        else:
            parser.print_help()
            return 0
            
    except SystemExit:
        return 0
    except KeyboardInterrupt:
        print(f"\n{Emoji.KOSTYL} Прервано пользователем. Но мы не падаем!")
        return 130
    except Exception as e:
        print(f"{Emoji.ERROR} Ошибка CLI: {e}")
        if '--traceback' in args:
            traceback.print_exc()
        return 1

# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    sys.exit(main())