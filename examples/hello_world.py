# examples/hello_world.py
"""
Hello World на kostylpy.
Демонстрирует основные возможности библиотеки
на максимально простом примере.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kostylpy as kp
from kostylpy import (
    safe, retry, fallback,
    KostylContext, kostyl_block,
    safe_get, safe_divide,
    DotDict, SafeList,
)

# ═══════════════════════════════════════════════════════════════
# 1. САМЫЙ ПРОСТОЙ ПРИМЕР
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("🦿 HELLO WORLD НА КОСТЫЛЯХ")
print("=" * 60)

# Обычный print работает как обычно
print("Hello World!")
print("Этот print никогда не падает.")

# Даже если что-то пойдёт не так
print(None, [], {}, lambda x: x)  # Всё работает

# ═══════════════════════════════════════════════════════════════
# 2. БЕЗОПАСНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Безопасные функции:")

@safe(fallback="Всё сломалось, но мы держимся!")
def greet(name):
    if not isinstance(name, str):
        raise ValueError("Имя должно быть строкой!")
    return f"Привет, {name}!"

print(greet("Мир"))
print(greet(42))  # Не падает!

# ═══════════════════════════════════════════════════════════════
# 3. ПОВТОРНЫЕ ПОПЫТКИ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Повторные попытки:")

attempts = []

@retry(max_attempts=5, delay=0.1, fallback="Не удалось :(")
def unstable_greeting():
    attempts.append(1)
    if len(attempts) < 3:
        raise ConnectionError("Сервер не отвечает...")
    return "Привет после нескольких попыток!"

print(unstable_greeting())
print(f"   (потребовалось попыток: {len(attempts)})")

# ═══════════════════════════════════════════════════════════════
# 4. КОНТЕКСТНЫЙ МЕНЕДЖЕР
# ═══════════════════════════════════════════════════════════════

print("\n📌 Контекстный менеджер:")

with KostylContext("опасная операция"):
    print("   Внутри защищённого блока...")
    # Эта ошибка будет подавлена
    raise RuntimeError("Что-то пошло не так!")
    print("   Это сообщение не появится")

print("   А мы всё ещё живы!")

# ═══════════════════════════════════════════════════════════════
# 5. БЕЗОПАСНАЯ РАБОТА С ДАННЫМИ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Безопасная работа с данными:")

# Словарь с доступом через точку
config = DotDict({
    'app': {
        'name': 'KostylApp',
        'version': '3.0.0',
        'settings': {
            'debug': True
        }
    }
})

print(f"   Приложение: {config.app.name} v{config.app.version}")

# Безопасный доступ
debug_mode = safe_get(config, 'app.settings.debug', default=False)
print(f"   Debug: {debug_mode}")

# Несуществующий путь
timeout = safe_get(config, 'app.settings.timeout', default=30)
print(f"   Timeout: {timeout} (значение по умолчанию)")

# ═══════════════════════════════════════════════════════════════
# 6. БЕЗОПАСНЫЕ ВЫЧИСЛЕНИЯ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Безопасные вычисления:")

# Деление на ноль
result = safe_divide(100, 0, default=float('inf'))
print(f"   100 / 0 = {result}")

# Безопасный список
items = SafeList([1, 2, 3], default="НЕТ ЭЛЕМЕНТА")
print(f"   items[0] = {items[0]}")
print(f"   items[100] = {items[100]}")

# ═══════════════════════════════════════════════════════════════
# 7. ВАЛИДАЦИЯ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Валидация:")

from kostylpy.validators import StringValidator, RangeValidator, EmailValidator

name_validator = StringValidator(min_length=2, max_length=50)
age_validator = RangeValidator(min_value=0, max_value=150)
email_validator = EmailValidator()

# Проверяем данные
checks = [
    ("Имя: 'Jo'", name_validator.validate("Jo")),
    ("Имя: 'A'", name_validator.validate("A")),
    ("Возраст: 25", age_validator.validate(25)),
    ("Возраст: -5", age_validator.validate(-5)),
    ("Email: test@example.com", email_validator.validate("test@example.com")),
    ("Email: не email", email_validator.validate("не email")),
]

for description, result in checks:
    status = "✅" if result.is_valid else "❌"
    print(f"   {status} {description}")

# ═══════════════════════════════════════════════════════════════
# 8. МЕТРИКИ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Метрики:")

from kostylpy.metrics import metrics

metrics.record_operation(success=True, duration=0.05)
metrics.record_operation(success=True, duration=0.1)
metrics.record_operation(success=False, duration=0.2)

stats = metrics.stats()
print(f"   Всего операций: {metrics.total_operations.get()}")
print(f"   Успешность: {metrics.success_rate:.1f}%")

# Кофе-метрика
metrics.coffee.drink(duration=300.0)
print(f"   ☕ Кофе-брейков: {metrics.coffee.total_coffees}")

# ═══════════════════════════════════════════════════════════════
# 9. УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Утилиты:")

from kostylpy.utils import truncate, human_readable_size, time_ago, random_string

print(f"   truncate('Очень длинная строка...', 20) = {truncate('Очень длинная строка для примера', 20)}")
print(f"   human_readable_size(1234567) = {human_readable_size(1234567)}")
print(f"   time_ago(3661) = {time_ago(3661)}")
print(f"   random_string(8) = {random_string(8)}")
print(f"   random_email() = {kp.random_email()}")

# ═══════════════════════════════════════════════════════════════
# 10. КОСТЫЛЬНЫЙ БЛОК
# ═══════════════════════════════════════════════════════════════

print("\n📌 Быстрый костыльный блок:")

with kostyl_block("быстрая операция"):
    # Здесь может упасть что угодно
    1 / 0  # Не упадёт!

print("   Операция завершена (несмотря на деление на ноль)")

# ═══════════════════════════════════════════════════════════════
# ФИНАЛ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("✅ HELLO WORLD УСПЕШНО ОТРАБОТАЛ")
print("=" * 60)
print(f"   kostylpy версия: {kp.__version__}")
print(f"   Статус ядра: {kp.core.status}")
print(f"   Загружено модулей: {len(kp.core.loaded_modules())}")
print()
print("   🦿 Весь код под защитой костылей!")
print("   ☕ Можно идти пить кофе.")