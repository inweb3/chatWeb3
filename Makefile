.PHONY: all clean format test tests integration_tests help extended_tests

all: help

coverage:
	poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered

TEST_FILE ?= tests/unit_tests/

test:
	poetry run pytest --disable-socket --allow-unix-socket $(TEST_FILE)

tests: 
	poetry run pytest --disable-socket --allow-unix-socket $(TEST_FILE)

extended_tests:
	poetry run pytest --disable-socket --allow-unix-socket --only-extended tests/unit_tests

integration_tests:
	poetry run pytest tests/integration_tests

help:
	@echo '----'
	@echo 'coverage                     - run unit tests and generate coverage report'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests'
	@echo 'test TEST_FILE=<test_file>   - run all tests in file'
	@echo 'extended_tests               - run only extended unit tests'
	@echo 'integration_tests            - run integration tests'
