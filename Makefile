.PHONY: install lint test run build-image

install:
	pip install -e '.[dev]'

lint:
	ruff check .

test:
	pytest -q

run:
	omni-mcp --transport stdio

build-image:
	docker build -t omni-mcp:local .
