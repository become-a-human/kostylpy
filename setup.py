# setup.py
"""
Установка kostylpy.
Ставит всё, включая костыли.
"""

import os
import sys
from setuptools import setup, find_packages

# ═══════════════════════════════════════════════════════════════
# МЕТАДАННЫЕ
# ═══════════════════════════════════════════════════════════════

NAME = "kostylpy"
VERSION = "3.0.0b1"
DESCRIPTION = "Профессиональная библиотека костылей для Python"
LONG_DESCRIPTION = """
🦿 kostylpy — Профессиональная библиотека костылей для Python
===============================================================

Просто импортируй этот модуль, и весь твой код станет неубиваемым.

Фичи:
- Безопасный print, open, import
- Декораторы: safe, retry, fallback, cached
- Контекстные менеджеры: KostylContext, TimerContext
- Валидаторы: типы, строки, email, пароли
- Фабрики: исключений, декораторов, заглушек
- Перехватчики: функций, атрибутов, импортов
- Асинхронные костыли: async_safe, async_retry
- Метрики и логирование
- AST патчер
- Monkey patcher
- И ещё куча всего!

Принципы:
1. Если что-то работает — добавь костыль для надёжности.
2. Если что-то не работает — добавь ещё костылей.
3. Костылей много не бывает.

Установка:
    pip install kostylpy

Использование:
    import kostylpy as kp
    
    @kp.safe(fallback="всё ок")
    def risky_function():
        raise ValueError("Ошибка!")
    
    print(risky_function())  # "всё ок"

Лицензия: WTFPL + Kostyl Clause
"""

# ═══════════════════════════════════════════════════════════════
# ЗАВИСИМОСТИ
# ═══════════════════════════════════════════════════════════════

# Минимальные зависимости
INSTALL_REQUIRES = [
    # Встроенные модули Python — всё уже есть!
    # Но для некоторых фич нужны:
]

# Опциональные зависимости
EXTRAS_REQUIRE = {
    'yaml': ['pyyaml>=5.0'],           # Для YAML конфигов
    'astor': ['astor>=0.8'],           # Для AST трансформаций (Python < 3.9)
    'psutil': ['psutil>=5.0'],         # Для метрик памяти
    'all': [
        'pyyaml>=5.0',
        'astor>=0.8',
        'psutil>=5.0',
    ],
}

# Зависимости для разработки
DEV_REQUIRES = [
    'pytest>=6.0',
    'pytest-cov>=2.0',
    'unittest2>=1.1',
]

# ═══════════════════════════════════════════════════════════════
# КЛАССИФИКАТОРЫ
# ═══════════════════════════════════════════════════════════════

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Development Status :: 5 - Production/Stable (на костылях)",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License (WTFPL + Kostyl Clause)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Debuggers",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Utilities",
    "Natural Language :: Russian",
    "Environment :: Console",
    "Framework :: AsyncIO",
]

# ═══════════════════════════════════════════════════════════════
# КЛЮЧЕВЫЕ СЛОВА
# ═══════════════════════════════════════════════════════════════

KEYWORDS = [
    "kostyl", "crutch", "костыль", "костыли",
    "safe", "retry", "fallback",
    "error-handling", "exception",
    "monkey-patching", "patching",
    "validation", "logging", "metrics",
    "async", "asyncio",
    "debugging", "testing",
    "production", "enterprise",
    "костылизация", "защита-от-падений",
    "безопасный-код", "неубиваемый-код",
    "работает-не-трогай",
]

# ═══════════════════════════════════════════════════════════════
# ДАННЫЕ ПАКЕТА
# ═══════════════════════════════════════════════════════════════

PACKAGE_DATA = {
    'kostylpy': [
        '*.py',
        '*.json',
        '*.yaml',
        '*.yml',
    ],
}

# ═══════════════════════════════════════════════════════════════
# ТОЧКИ ВХОДА
# ═══════════════════════════════════════════════════════════════

ENTRY_POINTS = {
    'console_scripts': [
        'kostylpy = kostylpy.__main__:main',
        'kostyl = kostylpy.__main__:main',
    ],
}

# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКА
# ═══════════════════════════════════════════════════════════════

setup(
    # Основное
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown; charset=UTF-8",
    
    # Автор
    author="Коллектив костылестроителей им. В.Е.Лосипедова",
    author_email="the1stplayergetready@gmail.com",
    url="http://localhost:8080/kostylpy",
    
    # Лицензия
    license="WTFPL + Kostyl Clause",
    
    # Пакеты
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    package_data=PACKAGE_DATA,
    include_package_data=True,
    
    # Зависимости
    python_requires='>=3.6',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    
    # Точки входа
    entry_points=ENTRY_POINTS,
    
    # Классификаторы
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    
    # Прочее
    zip_safe=False,
    platforms=['any'],
    
    # Данные проекта
    project_urls={
        'Bug Tracker': 'http://localhost:8080/kostylpy/issues',
        'Documentation': 'http://localhost:8080/kostylpy/docs',
        'Source Code': 'http://localhost:8080/kostylpy/source',
        'Coffee Fund': 'http://localhost:8080/kostylpy/coffee',
    },
)

# ═══════════════════════════════════════════════════════════════
# ПОСТ-УСТАНОВКА
# ═══════════════════════════════════════════════════════════════

def post_install_message():
    """Сообщение после установки."""
    print("""
    ╔══════════════════════════════════════════════╗
    ║  🦿 KOSTYLPY УСТАНОВЛЕН!                    ║
    ║                                              ║
    ║  Теперь ваш код под защитой.                ║
    ║  Просто добавьте:                           ║
    ║      import kostylpy                        ║
    ║                                              ║
    ║  CLI:                                       ║
    ║      python -m kostylpy run main.py         ║
    ║      python -m kostylpy scan main.py        ║
    ║      python -m kostylpy patch main.py       ║
    ║                                              ║
    ║  Документация: отсутствует (читайте исходники) ║
    ║  Поддержка: kostyl@crutch.enterprise        ║
    ║                                              ║
    ║  ☕ Заварите кофе. Вы это заслужили.        ║
    ╚══════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    # При прямом запуске — показываем справку
    print("""
    🦿 Установка kostylpy:
    
        pip install .
        
    Или в режиме разработки:
        pip install -e .
    
    С опциональными зависимостями:
        pip install .[all]
    
    Тесты:
        python -m pytest tests/
        
    Примеры:
        python examples/hello_world.py
        
    CLI:
        python -m kostylpy help
    """)
else:
    # При установке через pip — показываем сообщение
    try:
        post_install_message()
    except:
        pass