PYTHON ?= python

.PHONY: install lint typecheck test test-security test-e2e demo demo-offline docker-build docker-scan verify deploy

install:
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m playwright install chromium

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest -m "not e2e" --cov --cov-report=term-missing --cov-fail-under=90

test-security:
	$(PYTHON) -m pytest -m security
	$(PYTHON) -m bandit -c pyproject.toml -r app scripts
	$(PYTHON) -m pip_audit --progress-spinner off --cache-dir .codex-pip-audit-cache
	$(PYTHON) scripts/check_secrets.py

test-e2e:
	$(PYTHON) -m pytest -m e2e

demo:
	APP_MODE=live $(PYTHON) -m uvicorn app.main:app --host 127.0.0.1 --port 8000

demo-offline:
	APP_MODE=offline_demo $(PYTHON) -m uvicorn app.main:app --host 127.0.0.1 --port 8000

docker-build:
	docker build --tag devfest-verifiable-ai:local .

docker-scan: docker-build
	trivy image --severity HIGH,CRITICAL --exit-code 1 devfest-verifiable-ai:local

verify: lint typecheck test test-security test-e2e docker-build

deploy:
	bash deploy/deploy_confidential_space.sh
