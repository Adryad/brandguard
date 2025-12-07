# brandguard/Makefile

.PHONY: help install install-dev test test-backend test-frontend lint lint-backend lint-frontend format check-security run-backend run-prod docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  install        - Install production requirements"
	@echo "  install-dev    - Install development requirements"
	@echo "  test           - Run all tests"
	@echo "  test-backend   - Run backend tests only"
	@echo "  test-frontend  - Run frontend tests only"
	@echo "  lint           - Run all linting"
	@echo "  format         - Format all code"
	@echo "  run-backend    - Run backend dev server"
	@echo "  run-prod       - Run production services"

install:
	cd backend && python -m pip install -r requirements.txt

install-dev:
	cd backend && python -m pip install -r requirements-dev.txt
	cd frontend && npm install

test:
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:
	cd backend && python -m pytest tests/ --cov=app --cov-report=html

test-frontend:
	cd frontend && npm run test:coverage

lint:
	$(MAKE) lint-backend
	$(MAKE) lint-frontend

lint-backend:
	cd backend && flake8 app/
	cd backend && mypy app/
	cd backend && bandit -r app/

lint-frontend:
	cd frontend && npm run lint

format:
	cd backend && black app/ tests/
	cd backend && isort app/ tests/
	cd frontend && npm run format

check-security:
	trivy fs .
	$(MAKE) lint-backend

run-backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

run-prod:
	docker-compose -f docker-compose.prod.yml up -d

docker-build:
	docker-compose -f docker-compose.prod.yml build

docker-run:
	docker-compose -f docker-compose.prod.yml up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	docker system prune -f