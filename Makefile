format:
	ruff check --select I --fix src/
	ruff format src/ tests/

lint:
	ruff check src/

test:
	. .env.test.rc; \
	python3 -m pytest --cov=src -s;


test-coverage:
	. .env.test.rc; \
	python3 -m pytest --cov-report html:coverage --cov=src


db_setup:
	python3 -m scripts.db_scripts create_db create_tables seed_db

drop_db:
	python3 -m scripts.db_scripts drop_db

create_db:
	python3 -m scripts.db_scripts create_db

create_tables:
	python3 -m scripts.db_scripts crate_tables


