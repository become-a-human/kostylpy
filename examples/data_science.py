# examples/data_science.py
"""
Data Science на kostylpy.
Анализ данных, машинное обучение и статистика —
всё на костылях. Работает даже без numpy и pandas!
"""

import sys
import os
import random
import math
import statistics
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kostylpy as kp
from kostylpy import (
    safe, retry, fallback,
    KostylContext, kostyl_block,
    safe_get, safe_divide,
    DotDict, SafeList,
)
from kostylpy.utils import (
    clamp, round_to, safe_int, safe_float,
    human_readable_size, chunk_list,
    unique_list, group_by, sort_by_multiple_keys,
)
from kostylpy.metrics import metrics

# ═══════════════════════════════════════════════════════════════
# ДАННЫЕ
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("📊 DATA SCIENCE НА КОСТЫЛЯХ")
print("=" * 60)

# Генерируем тестовые данные
random.seed(42)

users_data = []
for i in range(100):
    users_data.append(DotDict({
        'id': i + 1,
        'name': kp.random_name(),
        'age': random.randint(18, 80),
        'salary': random.randint(30000, 200000),
        'score': round(random.uniform(0, 100), 2),
        'department': random.choice(['IT', 'HR', 'Sales', 'Marketing', 'Finance']),
        'is_active': random.choice([True, True, True, False]),  # 75% активных
        'projects': random.randint(0, 15),
        'experience': round(random.uniform(0, 40), 1),
    }))

print(f"\n📁 Загружено записей: {len(users_data)}")

# ═══════════════════════════════════════════════════════════════
# ОПИСАТЕЛЬНАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ОПИСАТЕЛЬНАЯ СТАТИСТИКА")
print("=" * 60)

@safe(fallback={})
def calculate_stats(data: list, field: str) -> dict:
    """Безопасный расчёт статистики по полю."""
    
    values = [safe_get(item, field, default=0) for item in data]
    values = [v for v in values if v is not None]
    
    if not values:
        return {'error': 'Нет данных'}
    
    with kostyl_block("расчёт статистики"):
        return {
            'count': len(values),
            'mean': round_to(statistics.mean(values), 2),
            'median': round_to(statistics.median(values), 2),
            'min': min(values),
            'max': max(values),
            'stdev': round_to(statistics.stdev(values) if len(values) > 1 else 0, 2),
            'sum': sum(values),
        }

# Статистика по всем числовым полям
fields = ['age', 'salary', 'score', 'projects', 'experience']

for field in fields:
    stats = calculate_stats(users_data, field)
    print(f"\n   Поле: {field}")
    print(f"   ├─ Количество: {stats['count']}")
    print(f"   ├─ Среднее: {stats['mean']}")
    print(f"   ├─ Медиана: {stats['median']}")
    print(f"   ├─ Мин: {stats['min']}")
    print(f"   ├─ Макс: {stats['max']}")
    print(f"   └─ Стандартное отклонение: {stats['stdev']}")

# ═══════════════════════════════════════════════════════════════
# ГРУППИРОВКА И АГРЕГАЦИЯ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ГРУППИРОВКА ПО ОТДЕЛАМ")
print("=" * 60)

@safe(fallback={})
def aggregate_by_department(data: list) -> dict:
    """Агрегация по отделам."""
    
    departments = group_by(data, lambda x: x.department)
    
    result = {}
    for dept, employees in departments.items():
        salaries = [e.salary for e in employees]
        scores = [e.score for e in employees]
        
        result[dept] = {
            'count': len(employees),
            'avg_salary': round_to(safe_divide(sum(salaries), len(salaries)), 0),
            'avg_score': round_to(safe_divide(sum(scores), len(scores)), 2),
            'total_projects': sum(e.projects for e in employees),
        }
    
    return result

dept_stats = aggregate_by_department(users_data)

# Сортируем по средней зарплате
sorted_depts = sorted(
    dept_stats.items(),
    key=lambda x: x[1]['avg_salary'],
    reverse=True
)

for dept, stats in sorted_depts:
    print(f"\n   {dept}:")
    print(f"   ├─ Сотрудников: {stats['count']}")
    print(f"   ├─ Средняя зарплата: {stats['avg_salary']:.0f} ₽")
    print(f"   ├─ Средний балл: {stats['avg_score']}")
    print(f"   └─ Всего проектов: {stats['total_projects']}")

# ═══════════════════════════════════════════════════════════════
# КОРРЕЛЯЦИОННЫЙ АНАЛИЗ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 КОРРЕЛЯЦИОННЫЙ АНАЛИЗ")
print("=" * 60)

@safe(fallback=0.0)
def correlation(x: list, y: list) -> float:
    """Коэффициент корреляции Пирсона."""
    n = len(x)
    if n < 2:
        return 0.0
    
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    # Безопасные вычисления
    std_x = safe_divide(
        math.sqrt(sum((xi - mean_x) ** 2 for xi in x)),
        math.sqrt(n - 1),
        default=1.0
    )
    std_y = safe_divide(
        math.sqrt(sum((yi - mean_y) ** 2 for yi in y)),
        math.sqrt(n - 1),
        default=1.0
    )
    
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / (n - 1)
    
    return safe_divide(cov, (std_x * std_y), default=0.0)

# Сравниваем пары полей
correlations = [
    ('Опыт vs Зарплата', [u.experience for u in users_data], [u.salary for u in users_data]),
    ('Проекты vs Балл', [u.projects for u in users_data], [u.score for u in users_data]),
    ('Возраст vs Зарплата', [u.age for u in users_data], [u.salary for u in users_data]),
    ('Опыт vs Проекты', [u.experience for u in users_data], [u.projects for u in users_data]),
]

for name, x, y in correlations:
    corr = correlation(x, y)
    strength = (
        "сильная" if abs(corr) > 0.7 else
        "средняя" if abs(corr) > 0.3 else
        "слабая"
    )
    direction = "положительная" if corr > 0 else "отрицательная"
    print(f"   {name}: r = {corr:.3f} ({strength} {direction})")

# ═══════════════════════════════════════════════════════════════
# ПРОСТАЯ ЛИНЕЙНАЯ РЕГРЕССИЯ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ЛИНЕЙНАЯ РЕГРЕССИЯ (Опыт → Зарплата)")
print("=" * 60)

@safe(fallback={'slope': 0, 'intercept': 0})
def linear_regression(x: list, y: list) -> dict:
    """Простая линейная регрессия y = slope * x + intercept."""
    n = len(x)
    if n < 2:
        return {'slope': 0, 'intercept': 0}
    
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    
    slope = safe_divide(numerator, denominator, default=0)
    intercept = mean_y - slope * mean_x
    
    return {
        'slope': round_to(slope, 2),
        'intercept': round_to(intercept, 0),
    }

@safe(fallback=0.0)
def predict(slope: float, intercept: float, x: float) -> float:
    """Предсказание по модели."""
    return slope * x + intercept

@safe(fallback=0.0)
def r_squared(x: list, y: list, slope: float, intercept: float) -> float:
    """Коэффициент детерминации R²."""
    mean_y = statistics.mean(y)
    
    ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(len(x)))
    ss_tot = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
    
    return 1 - safe_divide(ss_res, ss_tot, default=1)

x_exp = [u.experience for u in users_data]
y_salary = [u.salary for u in users_data]

model = linear_regression(x_exp, y_salary)
print(f"\n   Модель: зарплата = {model['slope']} × опыт + {model['intercept']}")

# Предсказания
test_exp = [1, 5, 10, 20, 30]
print("\n   Предсказания:")
for exp in test_exp:
    pred = predict(model['slope'], model['intercept'], exp)
    print(f"   ├─ Опыт {exp} лет → зарплата {pred:,.0f} ₽")

# Качество модели
r2 = r_squared(x_exp, y_salary, model['slope'], model['intercept'])
print(f"\n   R² = {r2:.3f} ({'хорошая модель' if r2 > 0.7 else 'средняя' if r2 > 0.3 else 'слабая'})")

# ═══════════════════════════════════════════════════════════════
# ФИЛЬТРАЦИЯ И ПОИСК АНОМАЛИЙ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ПОИСК АНОМАЛИЙ")
print("=" * 60)

@safe(fallback=[])
def find_outliers(data: list, field: str, threshold: float = 2.0) -> list:
    """Поиск выбросов методом z-score."""
    
    values = [(i, safe_get(item, field, default=0)) for i, item in enumerate(data)]
    vals = [v for _, v in values]
    
    if len(vals) < 3:
        return []
    
    mean = statistics.mean(vals)
    std = statistics.stdev(vals)
    
    if std == 0:
        return []
    
    outliers = []
    for idx, val in values:
        z_score = abs((val - mean) / std)
        if z_score > threshold:
            outliers.append({
                'index': idx,
                'value': val,
                'z_score': round_to(z_score, 2),
                'name': data[idx].name,
                'department': data[idx].department,
            })
    
    return outliers

# Ищем аномалии по зарплате
salary_outliers = find_outliers(users_data, 'salary', threshold=2.0)
print(f"\n   Выбросы по зарплате (z-score > 2.0): {len(salary_outliers)}")
for out in salary_outliers[:5]:
    print(f"   ├─ {out['name']} ({out['department']}): {out['value']:,} ₽ (z={out['z_score']})")

if len(salary_outliers) > 5:
    print(f"   └─ ... и ещё {len(salary_outliers) - 5}")

# Ищем аномалии по баллам
score_outliers = find_outliers(users_data, 'score', threshold=2.5)
print(f"\n   Выбросы по баллам (z-score > 2.5): {len(score_outliers)}")
for out in score_outliers[:3]:
    print(f"   ├─ {out['name']}: {out['value']} (z={out['z_score']})")

# ═══════════════════════════════════════════════════════════════
# КЛАСТЕРИЗАЦИЯ (ПРОСТАЯ)
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ПРОСТАЯ КЛАСТЕРИЗАЦИЯ (возрастные группы)")
print("=" * 60)

@safe(fallback={})
def cluster_by_age(data: list) -> dict:
    """Кластеризация по возрастным группам."""
    
    clusters = {
        'Junior (18-25)': [],
        'Middle (26-35)': [],
        'Senior (36-50)': [],
        'Expert (51+)': [],
    }
    
    for user in data:
        if user.age <= 25:
            clusters['Junior (18-25)'].append(user)
        elif user.age <= 35:
            clusters['Middle (26-35)'].append(user)
        elif user.age <= 50:
            clusters['Senior (36-50)'].append(user)
        else:
            clusters['Expert (51+)'].append(user)
    
    return clusters

clusters = cluster_by_age(users_data)

for cluster_name, members in clusters.items():
    if members:
        avg_salary = statistics.mean([m.salary for m in members])
        avg_score = statistics.mean([m.score for m in members])
        print(f"\n   {cluster_name}:")
        print(f"   ├─ Человек: {len(members)}")
        print(f"   ├─ Средняя зарплата: {avg_salary:,.0f} ₽")
        print(f"   └─ Средний балл: {avg_score:.1f}")

# ═══════════════════════════════════════════════════════════════
# ОТЧЁТ
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("📊 ИТОГОВЫЙ ОТЧЁТ")
print("=" * 60)

# Собираем ключевые метрики
total_employees = len(users_data)
active_employees = sum(1 for u in users_data if u.is_active)
avg_salary = statistics.mean([u.salary for u in users_data])
avg_score = statistics.mean([u.score for u in users_data])
total_projects = sum(u.projects for u in users_data)
avg_experience = statistics.mean([u.experience for u in users_data])

print(f"""
   👥 Всего сотрудников: {total_employees}
   ✅ Активных: {active_employees} ({safe_divide(active_employees, total_employees) * 100:.1f}%)
   
   💰 Средняя зарплата: {avg_salary:,.0f} ₽
   📊 Средний балл: {avg_score:.1f}
   📁 Всего проектов: {total_projects}
   ⏳ Средний опыт: {avg_experience:.1f} лет
   
   🏢 Отделов: {len(dept_stats)}
   📈 Модель: з/п = {model['slope']} × опыт + {model['intercept']}
   📉 R² модели: {r2:.3f}
   🔍 Выбросов: {len(salary_outliers) + len(score_outliers)}
""")

# Метрики kostylpy
print(f"   🦿 Костылей применено: {kp.core.stats().get('crutches', 'много')}")
print(f"   ⏱️ Время анализа: {kp.core.uptime:.1f}с")
print(f"   ☕ Кофе-брейков: {metrics.coffee.total_coffees}")

print("\n" + "=" * 60)
print("✅ АНАЛИЗ ДАННЫХ ЗАВЕРШЁН (на костылях)")
print("=" * 60)