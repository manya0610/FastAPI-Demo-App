format:
	ruff check --select I --fix ./
	ruff format src/

lint:
	ruff check src/