# Костыльная система сборки для kostylpy
# Работает примерно так же как и сам kostylpy — на костылях

.PHONY: help install test test-core test-decorators test-patcher test-interceptors test-integration
.PHONY: test-all test-quick test-verbose test-coverage test-stress
.PHONY: lint format clean build publish examples
.PHONY: scan patch check report coffee

# ═══════════════════════════════════════════════════
# ПОМОЩЬ
# ═══════════════════════════════════════════════════

help: ## Показать эту справку
	@echo "🦿 Kostylpy Makefile"
	@echo ""
	@echo "Использование: make [команда]"
	@echo ""
	@echo "📦 Установка:"
	@echo "  make install        Установить библиотеку"
	@echo "  make install-dev    Установить с зависимостями для разработки"
	@echo "  make install-all    Установить со всеми опциональными зависимостями"
	@echo ""
	@echo "🧪 Тестирование:"
	@echo "  make test           Запустить все тесты"
	@echo "  make test-quick     Быстрые тесты (без стресс-тестов)"
	@echo "  make test-verbose   Подробные тесты"
	@echo "  make test-core      Тесты ядра"
	@echo "  make test-decorators Тесты декораторов"
	@echo "  make test-patcher   Тесты патчера"
	@echo "  make test-interceptors Тесты перехватчиков"
	@echo "  make test-integration Интеграционные тесты"
	@echo "  make test-coverage  Тесты с отчётом о покрытии"
	@echo "  make test-stress    Стресс-тесты"
	@echo ""
	@echo "🔧 Инструменты:"
	@echo "  make lint           Проверка кода (flake8)"
	@echo "  make format         Форматирование кода (black + isort)"
	@echo "  make clean          Очистка временных файлов"
	@echo "  make build          Сборка пакета"
	@echo ""
	@echo "🎮 Примеры:"
	@echo "  make example-hello  Hello World"
	@echo "  make example-web    Веб-сервер"
	@echo "  make example-ds     Data Science"
	@echo "  make example-prod   Продакшен-система"
	@echo "  make examples       Запустить все примеры"
	@echo ""
	@echo "🦿 Kostylpy CLI:"
	@echo "  make scan           Сканировать main.py"
	@echo "  make patch          Пропатчить main.py"
	@echo "  make check          Проверить здоровье"
	@echo "  make report         Показать отчёт"
	@echo "  make coffee         ☕ Кофе-брейк"

# ═══════════════════════════════════════════════════
# УСТАНОВКА
# ═══════════════════════════════════════════════════

install: ## Установить библиотеку
	pip install -e .

install-dev: ## Установить с зависимостями для разработки
	pip install -e .[dev]

install-all: ## Установить со всеми зависимостями
	pip install -e .[all]

# ═══════════════════════════════════════════════════
# ТЕСТЫ
# ═══════════════════════════════════════════════════

test: ## Запустить все тесты
	@echo "🧪 Запуск всех тестов..."
	python -m pytest tests/ -v --tb=short

test-all: test ## Алиас для всех тестов

test-quick: ## Быстрые тесты (без стресс-тестов)
	@echo "⚡ Быстрые тесты..."
	python -m pytest tests/ -v --tb=short -m "not stress" --timeout=10

test-verbose: ## Подробные тесты с полным трейсбеком
	@echo "🔍 Подробные тесты..."
	python -m pytest tests/ -v --tb=long -s

test-core: ## Тесты ядра
	@echo "🏗️ Тесты ядра..."
	python -m pytest tests/test_core.py -v --tb=short

test-decorators: ## Тесты декораторов
	@echo "🛡️ Тесты декораторов..."
	python -m pytest tests/test_decorators.py -v --tb=short

test-patcher: ## Тесты патчера
	@echo "💉 Тесты патчера..."
	python -m pytest tests/test_patcher.py -v --tb=short

test-interceptors: ## Тесты перехватчиков
	@echo "🕵️ Тесты перехватчиков..."
	python -m pytest tests/test_interceptors.py -v --tb=short

test-integration: ## Интеграционные тесты
	@echo "🔗 Интеграционные тесты..."
	python -m pytest tests/test_integration.py -v --tb=short

test-coverage: ## Тесты с отчётом о покрытии
	@echo "📊 Тесты с покрытием..."
	python -m pytest tests/ --cov=kostylpy --cov-report=html --cov-report=term -v
	@echo "Отчёт сохранён в htmlcov/index.html"

test-stress: ## Стресс-тесты
	@echo "💪 Стресс-тесты..."
	python -m pytest tests/ -v -m "stress" --timeout=60

# ═══════════════════════════════════════════════════
# ЛИНТИНГ И ФОРМАТИРОВАНИЕ
# ═══════════════════════════════════════════════════

lint: ## Проверка кода
	@echo "🔍 Проверка кода..."
	flake8 kostylpy/ --max-line-length=120 --ignore=E203,E266,E501,W503 || true
	@echo "✅ Проверка завершена (ошибки выше — это фичи)"

format: ## Форматирование кода
	@echo "✨ Форматирование..."
	isort kostylpy/ tests/ examples/ 2>/dev/null || true
	black kostylpy/ tests/ examples/ --line-length=120 2>/dev/null || true
	@echo "✅ Форматирование завершено"

# ═══════════════════════════════════════════════════
# СБОРКА
# ═══════════════════════════════════════════════════

build: ## Сборка пакета
	@echo "📦 Сборка пакета..."
	python -m build
	@echo "✅ Пакет собран в dist/"

publish: ## Публикация в PyPI (нужен twine)
	@echo "🚀 Публикация в PyPI..."
	twine upload dist/*
	@echo "✅ Опубликовано!"

# ═══════════════════════════════════════════════════
# ПРИМЕРЫ
# ═══════════════════════════════════════════════════

example-hello: ## Hello World
	@echo "👋 Hello World на костылях..."
	python examples/hello_world.py

example-web: ## Веб-сервер
	@echo "🌐 Веб-сервер на костылях..."
	python examples/web_server.py

example-ds: ## Data Science
	@echo "📊 Data Science на костылях..."
	python examples/data_science.py

example-prod: ## Продакшен-система
	@echo "🏭 Продакшен-система на костылях..."
	python examples/production.py

examples: example-hello example-web example-ds example-prod ## Запустить все примеры

# ═══════════════════════════════════════════════════
# KOSTYLPY CLI (быстрый доступ)
# ═══════════════════════════════════════════════════

FILE ?= main.py

scan: ## Сканировать файл (FILE=main.py)
	@echo "🔍 Сканирование $(FILE)..."
	python -m kostylpy scan $(FILE)

patch: ## Пропатчить файл (FILE=main.py)
	@echo "💉 Патчинг $(FILE)..."
	python -m kostylpy patch $(FILE) --aggressive

check: ## Проверить здоровье
	python -m kostylpy check

report: ## Показать отчёт
	python -m kostylpy report

version: ## Показать версию
	python -m kostylpy version

coffee: ## ☕ Кофе-брейк
	@echo "☕"
	@echo "☕☕"
	@echo "☕☕☕"
	@echo "Кофе готов!"
	@python -c "import kostylpy as kp; kp.metrics.coffee.drink(); print('🦿 Костыли заряжены!')"

# ═══════════════════════════════════════════════════
# ОЧИСТКА
# ═══════════════════════════════════════════════════

clean: ## Очистка временных файлов
	@echo "🧹 Очистка..."
	rm -rf __pycache__
	rm -rf kostylpy/__pycache__
	rm -rf tests/__pycache__
	rm -rf examples/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	rm -f *.log
	rm -f coffee_breaks.log
	rm -f production.log
	rm -f kostyl_db.json
	@echo "✅ Очищено!"

# ═══════════════════════════════════════════════════
# МАГИЯ
# ═══════════════════════════════════════════════════

.DEFAULT_GOAL := help