format:
	ruff check --select I --fix src/
	ruff format src/ tests/

lint:
	ruff check src/

test:
	python3 -m pytest -s