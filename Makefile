REPO_PATH := $(shell git rev-parse --show-toplevel)
PRE_COMMIT_HOOK_PATH := $(REPO_PATH)/.git/hooks/pre-commit
APP_NAME ?= "llm_insight_generation"
PYTEST_ARGS ?=

LINT_FILES := $(shell git diff --name-only)
LINT_FILES += $(shell git diff --name-only origin/HEAD)
LINT_FILES := $(shell echo ${LINT_FILES} | uniq | xargs)

.PHONY: default
default: setup

.PHONY: setup
setup:
	@echo "Installing pre-commit hook..."
	@echo "#/usr/bin/env bash" > $(PRE_COMMIT_HOOK_PATH)
	@echo "make lint" >> $(PRE_COMMIT_HOOK_PATH)
	@chmod +x $(PRE_COMMIT_HOOK_PATH)
	@echo "Syncing dependencies..."
	@make sync-dev

.PHONY: sync
sync:
	@pipenv sync

.PHONY: sync-dev
sync-dev:
	@pipenv sync --dev


.PHONY: install
install:
	@pipenv install

.PHONY: update
update:
	@pipenv update

.PHONY: test
test: sync-dev .pytest

.PHONY: coverage
coverage: sync-dev .coverage

.PHONY: clean
clean:
	@rm -rf .pytest_cache
	@pipenv clean
	@pipenv --rm

.PHONY: format
format:
	@echo "Running black formatter..."
	@pipenv run black --safe $(LINT_FILES)

.PHONY: lint
lint:
	@# Only run linting on modified python files
	@if [ -n "$(LINT_FILES)" ]; then \
		make .pylint .black_check; \
	else \
		echo "lint: empty file list"; \
	fi

.PHONY: .coverage
.coverage:
	@pipenv run coverage report --skip-covered
	@pipenv run coverage xml

.PHONY: .pytest
.pytest:
	@pipenv run pytest $(PYTEST_ARGS)


.PHONY: .pylint
.pylint:
	@echo "Running pylint..."
	@pipenv run pylint --rcfile=.pylintrc --output-format=colorized --reports=n --recursive=y $(LINT_FILES)

.PHONY: .black_check
.black_check:
	@echo "Running format checks..."
	@pipenv run black --safe --check --diff --color $(LINT_FILES)

