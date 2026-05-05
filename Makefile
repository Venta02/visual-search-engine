.PHONY: help install dev test lint format clean docker-up docker-down index demo

help:
	@echo "Visual Search Engine - Development Commands"
	@echo ""
	@echo "  make install      Install Python dependencies"
	@echo "  make dev          Run the API server in development mode"
	@echo "  make demo         Run the Streamlit demo"
	@echo "  make test         Run the test suite"
	@echo "  make lint         Run linters (ruff, mypy)"
	@echo "  make format       Auto-format code with black"
	@echo "  make docker-up    Start infrastructure (Qdrant, Redis, Prometheus, Grafana)"
	@echo "  make docker-down  Stop infrastructure"
	@echo "  make index        Run sample dataset indexing"
	@echo "  make clean        Remove cached files"

install:
	pip install -r requirements.txt

dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

demo:
	streamlit run frontend/streamlit_app/app.py

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	ruff check --fix src/ tests/

docker-up:
	docker compose up -d qdrant redis
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@echo "Services ready. API: http://localhost:6333  Redis: localhost:6379"

docker-up-full:
	docker compose up -d
	@echo "All services started including monitoring."
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

docker-down:
	docker compose down

index:
	python scripts/build_index.py --dataset data/raw/sample --batch-size 16

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .ruff_cache htmlcov .coverage
