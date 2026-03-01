# ========================
# Requirements
# ========================

requirements: ## Скомпилировать requirements.in в requirements.txt
	pip-compile requirements.in

install: requirements ## Установить зависимости
	pip install -r requirements.txt

# ========================
# Test
# ========================

test: ## Запустить все тесты с подробным выводом
	pytest -v

# ========================
# Code Quality
# ========================

format: ## Автоматическое форматирование кода (isort + black)
	isort .
	black .

lint: ## Проверка стиля и типов (flake8 + mypy)
	flake8 .
	mypy .

check: format lint test ## Полная проверка качества кода

# ========================
# Run
# ========================

run: ## Запустить HTTP сервис (uvicorn)
	@if [ ! -f .env ]; then \
		echo ".env not found. Create it from .env.example"; \
		exit 1; \
	fi
	@for key in JWT_ISSUER JWT_AUDIENCE JWT_PRIVATE_KEY_PEM JWT_PUBLIC_KEY_PEM; do \
		if ! grep -q "^$$key=" .env; then \
			echo "Missing required env var in .env: $$key"; \
			exit 1; \
		fi; \
	done
	uvicorn src.interface.http.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env

# ========================
# API Contract
# ========================

openapi-export: ## Сгенерировать versioned OpenAPI artifact (openapi.yaml)
	python scripts/export_openapi.py --output openapi.yaml

openapi-check: ## Проверить, что openapi.yaml синхронизирован с кодом
	python scripts/export_openapi.py --output openapi.yaml --check

contract-provider: openapi-check test ## Проверка provider-контракта (OpenAPI + tests)

# ========================
# Pre-commit
# ========================

precommit: ## Запуск pre-commit хуков на всех файлах
	pre-commit run --all-files

# ========================
# Help
# ========================

help: ## Показать список доступных команд
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
