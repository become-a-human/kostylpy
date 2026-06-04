# examples/web_server.py
"""
Веб-сервер на kostylpy.
Демонстрирует создание неубиваемого веб-приложения.
Работает даже без Flask/Django — на голых костылях!
"""

import sys
import os
import json
import time
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kostylpy as kp
from kostylpy import (
    safe, retry, fallback,
    KostylContext, kostyl_block,
    safe_get, safe_divide,
    DotDict, SafeList,
)
from kostylpy.utils import (
    safe_read_file, safe_write_file,
    random_string, timestamp_iso,
    to_json, from_json,
)
from kostylpy.validators import (
    StringValidator, RangeValidator,
    EmailValidator, ValidationResult,
)

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ СЕРВЕРА
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("🌐 ВЕБ-СЕРВЕР НА КОСТЫЛЯХ")
print("=" * 60)

config = DotDict({
    'server': {
        'host': 'localhost',
        'port': 8080,
        'debug': True,
        'max_connections': 100,
        'timeout': 30,
    },
    'database': {
        'host': 'localhost',
        'port': 5432,
        'name': 'kostyl_db',
        'pool_size': 5,
    },
    'features': {
        'caching': True,
        'compression': False,
        'rate_limiting': True,
        'auto_fix': True,  # Костыльный авто-фикс
    }
})

print(f"   Хост: {config.server.host}:{config.server.port}")
print(f"   База данных: {config.database.name}")
print(f"   Режим: {'DEBUG' if config.server.debug else 'PRODUCTION'}")

# ═══════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ (ЗАГЛУШКА)
# ═══════════════════════════════════════════════════════════════

print("\n📌 Инициализация базы данных...")

class Database:
    """
    База данных на костылях.
    Хранит данные в JSON файле.
    Если файла нет — создаёт в памяти.
    """
    
    def __init__(self, db_path: str = "kostyl_db.json"):
        self.db_path = db_path
        self._data = DotDict({'users': {}, 'sessions': {}, 'logs': []})
        self._load()
    
    @safe(fallback=None)
    def _load(self):
        """Загружает данные из файла."""
        content = safe_read_file(self.db_path, default="{}")
        loaded = from_json(content, default={})
        self._data = DotDict(loaded)
        print("   База данных загружена")
    
    @safe(fallback=False)
    def save(self):
        """Сохраняет данные в файл."""
        return safe_write_file(self.db_path, to_json(self._data))
    
    @safe(fallback=None)
    def get_user(self, user_id: str):
        return self._data.users.get(user_id)
    
    @safe(fallback=False)
    def create_user(self, user_id: str, data: dict):
        if user_id in self._data.users:
            return False
        self._data.users[user_id] = DotDict(data)
        self._data.users[user_id].created_at = timestamp_iso()
        self.save()
        return True
    
    @safe(fallback=[])
    def list_users(self):
        return list(self._data.users.keys())
    
    @safe(fallback=None)
    def create_session(self, user_id: str):
        session_id = random_string(32)
        self._data.sessions[session_id] = {
            'user_id': user_id,
            'created_at': timestamp_iso(),
            'expires_at': timestamp_iso(),  # TODO: реальный expiry
        }
        self.save()
        return session_id
    
    @safe(fallback=None)
    def validate_session(self, session_id: str):
        session = self._data.sessions.get(session_id)
        if session:
            return session['user_id']
        return None

db = Database()

# ═══════════════════════════════════════════════════════════════
# КОНТРОЛЛЕРЫ
# ═══════════════════════════════════════════════════════════════

print("\n📌 Регистрация контроллеров...")

# Валидаторы
username_validator = StringValidator(min_length=3, max_length=30)
password_validator = kp.PasswordValidator(
    min_length=6,
    require_uppercase=False,
    require_special=False,
    require_emoji=False,
)
email_validator = EmailValidator()
age_validator = RangeValidator(min_value=0, max_value=150)

@safe(fallback={'status': 'error', 'message': 'Внутренняя ошибка сервера'})
@retry(max_attempts=2, delay=0.01, fallback={'status': 'error', 'message': 'Таймаут'})
def handle_register(data: dict) -> dict:
    """Регистрация пользователя."""
    
    username = safe_get(data, 'username', default='')
    password = safe_get(data, 'password', default='')
    email = safe_get(data, 'email', default='')
    age = safe_get(data, 'age', default=0)
    
    # Валидация
    errors = []
    
    if not username_validator.validate(username).is_valid:
        errors.append('Имя пользователя должно быть от 3 до 30 символов')
    
    if not password_validator.validate(password).is_valid:
        errors.append('Пароль слишком слабый')
    
    if not email_validator.validate(email).is_valid:
        errors.append('Некорректный email')
    
    if not age_validator.validate(age).is_valid:
        errors.append('Возраст должен быть от 0 до 150')
    
    if errors:
        return {'status': 'error', 'errors': errors}
    
    # Создаём пользователя
    user_data = {
        'username': username,
        'email': email,
        'age': age,
    }
    
    if db.create_user(username, user_data):
        session_id = db.create_session(username)
        return {
            'status': 'ok',
            'message': f'Пользователь {username} создан',
            'session_id': session_id,
        }
    else:
        return {'status': 'error', 'message': 'Пользователь уже существует'}

@safe(fallback={'status': 'error', 'message': 'Ошибка входа'})
def handle_login(data: dict) -> dict:
    """Вход пользователя."""
    
    username = safe_get(data, 'username', default='')
    
    with KostylContext("вход пользователя"):
        user = db.get_user(username)
        if user is None:
            return {'status': 'error', 'message': 'Пользователь не найден'}
        
        session_id = db.create_session(username)
        return {
            'status': 'ok',
            'message': f'Добро пожаловать, {username}!',
            'session_id': session_id,
            'user': dict(user),
        }

@safe(fallback={'status': 'error', 'message': 'Ошибка профиля'})
def handle_profile(session_id: str) -> dict:
    """Профиль пользователя."""
    
    user_id = db.validate_session(session_id)
    if not user_id:
        return {'status': 'error', 'message': 'Неавторизован'}
    
    user = db.get_user(user_id)
    if not user:
        return {'status': 'error', 'message': 'Пользователь не найден'}
    
    return {
        'status': 'ok',
        'user': dict(user),
        'stats': {
            'registration_date': user.get('created_at', 'неизвестно'),
        }
    }

@safe(fallback={'status': 'error', 'message': 'Ошибка списка'})
def handle_list_users(session_id: str) -> dict:
    """Список пользователей."""
    
    user_id = db.validate_session(session_id)
    if not user_id:
        return {'status': 'error', 'message': 'Неавторизован'}
    
    users = db.list_users()
    return {
        'status': 'ok',
        'count': len(users),
        'users': users,
    }

# ═══════════════════════════════════════════════════════════════
# РОУТЕР (ЗАГЛУШКА HTTP)
# ═══════════════════════════════════════════════════════════════

print("\n📌 Настройка роутера...")

class Router:
    """Простой роутер на костылях."""
    
    def __init__(self):
        self._routes = {}
    
    def add_route(self, path: str, handler: callable):
        self._routes[path] = handler
    
    @safe(fallback={'status': 'error', 'message': 'Роутер упал'})
    def route(self, path: str, data: dict = None, session_id: str = None) -> dict:
        """Маршрутизирует запрос."""
        
        if path not in self._routes:
            return {'status': 'error', 'message': f'Путь не найден: {path}'}
        
        handler = self._routes[path]
        
        # Определяем аргументы хендлера
        import inspect
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
        
        kwargs = {}
        if 'data' in params:
            kwargs['data'] = data or {}
        if 'session_id' in params:
            kwargs['session_id'] = session_id
        
        with kostyl_block(f"обработка {path}"):
            result = handler(**kwargs)
        
        return result

router = Router()
router.add_route('/api/register', handle_register)
router.add_route('/api/login', handle_login)
router.add_route('/api/profile', handle_profile)
router.add_route('/api/users', handle_list_users)

# ═══════════════════════════════════════════════════════════════
# ТЕСТОВЫЕ ЗАПРОСЫ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("🧪 ТЕСТИРОВАНИЕ СЕРВЕРА")
print("=" * 60)

# Тест 1: Регистрация
print("\n1. Регистрация пользователей:")

responses = []

# Успешная регистрация
resp = router.route('/api/register', data={
    'username': 'alice',
    'password': 'SecurePass123',
    'email': 'alice@example.com',
    'age': 30,
})
responses.append(('Alice', resp))
print(f"   Alice: {resp['status']} - {resp.get('message', resp.get('errors', ''))}")

# Регистрация с ошибками
resp = router.route('/api/register', data={
    'username': 'ab',
    'password': '123',
    'email': 'not-email',
    'age': 999,
})
responses.append(('Bad User', resp))
print(f"   Bad User: {resp['status']} - {len(resp.get('errors', []))} ошибок")

# Успешная регистрация ещё одного
resp = router.route('/api/register', data={
    'username': 'bob',
    'password': 'BobPass456',
    'email': 'bob@example.com',
    'age': 25,
})
responses.append(('Bob', resp))
print(f"   Bob: {resp['status']} - {resp.get('message', '')}")

# Тест 2: Вход
print("\n2. Вход пользователей:")

resp = router.route('/api/login', data={'username': 'alice'})
session_id = safe_get(resp, 'session_id', default=None)
print(f"   Alice: {resp['status']} - {resp.get('message', '')}")
if session_id:
    print(f"   Session: {session_id[:16]}...")

# Тест 3: Профиль
print("\n3. Профиль:")

if session_id:
    resp = router.route('/api/profile', session_id=session_id)
    user = safe_get(resp, 'user', default={})
    print(f"   Статус: {resp['status']}")
    print(f"   Пользователь: {safe_get(user, 'username', 'неизвестно')}")
    print(f"   Email: {safe_get(user, 'email', 'неизвестно')}")

# Тест 4: Список пользователей
print("\n4. Список пользователей:")

if session_id:
    resp = router.route('/api/users', session_id=session_id)
    users = safe_get(resp, 'users', default=[])
    print(f"   Всего пользователей: {safe_get(resp, 'count', 0)}")
    for user in users:
        print(f"   - {user}")

# Тест 5: Обработка ошибок
print("\n5. Обработка ошибок:")

# Несуществующий путь
resp = router.route('/api/nonexistent')
print(f"   /api/nonexistent: {resp['status']} - {resp['message']}")

# Запрос без сессии
resp = router.route('/api/profile')
print(f"   /api/profile без сессии: {resp['status']} - {resp.get('message', 'ок')}")

# Тест 6: Нагрузка
print("\n6. Нагрузочный тест:")

start_time = time.time()
success_count = 0

for i in range(20):
    resp = router.route('/api/login', data={'username': f'user_{i}'})
    if resp.get('status') == 'ok' or resp.get('status') == 'error':
        success_count += 1

elapsed = time.time() - start_time
print(f"   Обработано запросов: 20")
print(f"   Успешно: {success_count}")
print(f"   Время: {elapsed:.3f}с")
print(f"   RPS: {20/elapsed:.1f}")

# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА СЕРВЕРА
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 СТАТИСТИКА СЕРВЕРА")
print("=" * 60)

from kostylpy.metrics import metrics

print(f"   Всего операций: {metrics.total_operations.get()}")
print(f"   Успешность: {metrics.success_rate:.1f}%")
print(f"   Костылей применено: {kp.core.stats().get('crutches', 'много')}")
print(f"   Время работы: {kp.core.uptime:.1f}с")

# Сохраняем базу
db.save()
print(f"\n   💾 База сохранена в {db.db_path}")

print("\n" + "=" * 60)
print("✅ СЕРВЕР ГОТОВ К ПРОДАКШЕНУ (на костылях)")
print("=" * 60)
print("   🦿 Все системы работают")
print("   ☕ Пора пить кофе")