PYTHON ?= python

.PHONY: clean install lint typecheck test test-security test-e2e demo demo-offline reset-demo reliability docker-build docker-scan verify release-check cloud-verify deploy

clean:
	$(PYTHON) scripts/reset_demo.py
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

install:
	$(PYTHON) -m pip install --upgrade "pip>=26.2.1"
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
	$(PYTHON) scripts/run_demo.py --mode live

demo-offline:
	$(PYTHON) scripts/run_demo.py --mode offline_demo

reset-demo:
	$(PYTHON) scripts/reset_demo.py

reliability:
	$(PYTHON) scripts/reliability_check.py --cycles 20

docker-build:
	docker build --tag devfest-verifiable-ai:local .

docker-scan: docker-build
	trivy image --severity HIGH,CRITICAL --exit-code 1 devfest-verifiable-ai:local

verify: lint typecheck test test-security test-e2e docker-build

release-check: lint typecheck test test-security test-e2e reliability docker-build

cloud-verify:
	$(PYTHON) -m app.cloud_verify

deploy:
	bash deploy/deploy_confidential_space.sh
