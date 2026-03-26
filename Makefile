# ─── AI Support OpenEnv Makefile ──────────────────────────────────────────────

.PHONY: dev build run test lint seed validate baseline

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 7860

build:
	docker build -t ai-support-openenv .

run:
	docker run -p 7860:7860 --env-file .env ai-support-openenv

test:
	pytest tests/ -v --asyncio-mode=auto

lint:
	ruff check app/ tests/
	mypy app/ --ignore-missing-imports

seed:
	python -m scripts.seed_kb

generate-data:
	python -m scripts.generate_synthetic_data

validate:
	python -m scripts.validate_openenv --url http://localhost:7860

baseline:
	python -m baseline.run --url http://localhost:7860
