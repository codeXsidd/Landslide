.PHONY: help dev stop seed demo test lint format clean

# ============================================================
# NER-SAGE Makefile
# ============================================================

PYTHON := python
UVICORN := uvicorn
PYTEST := pytest
NPM := npm

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Infrastructure ────────────────────────────────────────────

# ── Development ───────────────────────────────────────────────

dev:  ## Start full dev environment (backend + frontend)
	@echo ""
	@echo "Starting backend..."
	@cd backend && .venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	@cd frontend && npm run dev &
	@echo ""
	@echo "NER-SAGE is starting:"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Swagger:  http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Neo4j:    http://localhost:7474"
	@echo "  MinIO:    http://localhost:9001"

backend:  ## Start backend only (assumes infra is running)
	cd backend && .venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:  ## Start frontend only
	cd frontend && npm run dev

# ── Setup ─────────────────────────────────────────────────────

setup-backend:  ## Create venv and install Python dependencies
	cd backend && python -m venv .venv
	cd backend && .venv\Scripts\pip install -r ../requirements.txt

setup-frontend:  ## Install Node dependencies
	cd frontend && npm install

setup: setup-backend setup-frontend  ## Full setup

# ── Data & Demo ───────────────────────────────────────────────

seed:  ## Generate synthetic demo data and seed databases
	$(PYTHON) scripts/generate_synthetic_data.py
	$(PYTHON) scripts/seed_neo4j.py
	@echo "Demo data seeded successfully."

demo:  ## Run the SIH demo scenario (Road B incident)
	$(PYTHON) scripts/run_demo.py

reset-data:  ## Drop and re-seed all demo data
	$(PYTHON) scripts/generate_synthetic_data.py
	$(PYTHON) scripts/seed_neo4j.py
	@echo "Demo data re-seeded."

train-ml:  ## Train the XGBoost models and save artifacts
	$(PYTHON) scripts/train_ml_model.py

# ── Testing ───────────────────────────────────────────────────

test:  ## Run all tests
	cd backend && .venv\Scripts\pytest tests/ -v --tb=short
	cd frontend && npm test -- --watchAll=false

test-backend:  ## Run backend tests only
	cd backend && .venv\Scripts\pytest tests/ -v --tb=short

test-evidence:  ## Run evidence engine tests
	cd backend && .venv\Scripts\pytest tests/evidence/ -v

test-graph:  ## Run graph engine tests
	cd backend && .venv\Scripts\pytest tests/graph/ -v

test-ml:  ## Run ML tests
	cd backend && .venv\Scripts\pytest tests/ml/ -v

test-api:  ## Run API integration tests
	cd backend && .venv\Scripts\pytest tests/api/ -v

# ── Code Quality ──────────────────────────────────────────────

lint:  ## Run linters
	cd backend && .venv\Scripts\ruff check app/ scripts/
	cd frontend && npm run lint

format:  ## Auto-format code
	cd backend && .venv\Scripts\ruff format app/ scripts/
	cd frontend && npm run format

typecheck:  ## Run type checking
	cd backend && .venv\Scripts\mypy app/
	cd frontend && npm run typecheck

# ── Cleanup ───────────────────────────────────────────────────

clean:  ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf frontend/.next frontend/out

clean-all: clean  ## Remove all artifacts
	@echo "All build artifacts removed."
