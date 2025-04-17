MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PYTHON_CODE = src/ tests/
PYTHON_VERSIONS = 3.11 3.12 3.13

PYTEST_COVERAGE = --cov=src/ --cov-context=test --cov-report=term-missing
PYTEST_SETTINGS =


.PHONY: all
all: install check coverage


.PHONY: clean
clean:
	git clean -fdx


.PHONY: install
install:
	uv sync


.PHONY: check
check:
	uvx pre-commit run --all-files


.PHONY: coverage
coverage:
	uv run -- pytest $(PYTEST_COVERAGE)


.PHONY: test
test:
	uv run -- pytest $(PYTEST_SETTINGS)


.PHONY: top100
top100:
	# uv export --script scripts/generate-test-data.py | uv pip install -r -
	uv run ./scripts/generate-top100.py

.PHONY: integration
integration: $(PYTHON_VERSIONS)

.PHONY: $(PYTHON_VERSIONS)
$(PYTHON_VERSIONS):
	$(MAKE) UV_PROJECT_ENVIRONMENT=.uv/$@ UV_PYTHON=$@ install test
