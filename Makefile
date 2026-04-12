.PHONY: install lint test run build-image

install:
	uv sync --extra dev

lint:
	uv run ruff check .

test:
	uv run pytest -q

run:
	uv run omni-mcp --transport stdio

build-image:
	docker build -t omni-mcp:local .
