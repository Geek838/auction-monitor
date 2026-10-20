.PHONY: install api web test test-api test-web check build

install:
	python3 -m venv .venv
	PIP_CACHE_DIR="$(CURDIR)/.cache/pip" .venv/bin/python -m pip install -r services/api/requirements.txt
	npm --cache "$(CURDIR)/.cache/npm" --prefix apps/web ci

api:
	.venv/bin/python -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000 --reload

web:
	npm --prefix apps/web run dev

test: test-api test-web

test-api:
	.venv/bin/python -m pytest services/api/tests

test-web:
	npm --prefix apps/web run test:e2e

check:
	npm --prefix apps/web run typecheck

build:
	npm --prefix apps/web run build
