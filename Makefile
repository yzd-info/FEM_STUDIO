.PHONY: setup lint type test check e2e tex wheel dev

setup:
	cd core && uv sync
	cd web && npm ci
	cd web && npx playwright install chromium

lint:
	cd core && uv run ruff check .
	cd core && uv run ruff format --check .

type:
	cd core && uv run mypy
	cd web && npx tsc --noEmit

test:
	cd core && uv run pytest -m "not slow"
	cd web && npx vitest run

check: lint type test

wheel:
	cd core && uv build --wheel --out-dir ../web/public

dev: wheel
	cd web && npm run dev

e2e: wheel
	cd web && npx playwright test

tex:
	@command -v latexmk >/dev/null 2>&1 && echo "latexmk found — fixture export not implemented yet (M5)" || echo "TeX Live not found locally; skipping (CI compiles via latex job, added in M5.9)"
