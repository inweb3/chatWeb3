.PHONY: all clean format test integration_tests help 

all: help

coverage:
	pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered

format:
	black .
	ruff --select I --fix .

TEST_FILE ?= tests/unit_tests/

test:
	pytest $(TEST_FILE)

integration_tests:
	pytest tests/integration_tests

help:
	@echo '----'
	@echo 'coverage                     - run unit tests and generate coverage report'
	@echo 'format                       - run code formatters'
	@echo 'test                         - run unit tests'
	@echo 'integration_tests            - run integration tests'
