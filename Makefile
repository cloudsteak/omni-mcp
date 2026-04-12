.PHONY: install lint test init-db run build-image

install:
	uv sync --extra dev

lint:
	uv run ruff check .

test:
	uv run pytest -q

init-db:
	uv run omni-mcp --init-db-only

run:
	uv run omni-mcp --transport stdio

build-image:
	docker build -t omni-mcp:local .
