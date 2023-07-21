# git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

REPO_PATH := $(shell git rev-parse --show-toplevel)
PRE_COMMIT_HOOK_PATH := $(REPO_PATH)/.git/hooks/pre-commit
PYTEST_ARGS ?=

ifndef CI
	DIRTY_FILES := $(shell git diff --name-only --diff-filter=d | grep --color=never -E '\.py$$')
	MASTER_DIFF := $(shell git diff --name-only --diff-filter=d origin/HEAD | grep --color=never -E '\.py$$')
	LINT_FILES := $(shell echo "${MASTER_DIFF}\n${DIRTY_FILES}" | sort | uniq | xargs)
else
	# On CI environment, list all the python files that have been modified between the current commit and master
	LINT_FILES := $(shell \
		git diff-tree --no-commit-id --name-only -r ${GITHUB_SHA} origin/master | \
		grep --color=never -E '\.py$$' | \
		xargs \
  	)
endif

.PHONY: default
default: test

.PHONY: setup
setup:
	@echo "Installing pre-commit hook..."
	@echo "#/usr/bin/env bash" > $(PRE_COMMIT_HOOK_PATH)
	@echo "make verify" >> $(PRE_COMMIT_HOOK_PATH)
	@chmod +x $(PRE_COMMIT_HOOK_PATH)


.PHONY: sync
sync:
	@echo "Syncing dependencies..."
	@poetry install


.PHONY: test
test: sync .pytest

.PHONY: coverage
coverage: sync-dev .coverage

.PHONY: build
build: sync
	@echo "Building package..."
	@poetry build

.PHONY: clean
clean:
	@rm -rf .pytest_cache dist .coverage .coverage.xml

.PHONY: format
format:
	@echo "Running black formatter..."
	@poetry run black --safe $(LINT_FILES)

.PHONY: verify
verify: .poetry-check lint

.PHONY: .poetry-check
.poetry-check:
	@echo "Running Poetry check..."
	@poetry check

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
	@poetry run coverage report --skip-covered
	@poetry run coverage xml

.PHONY: .pytest
.pytest:
	@poetry run pytest $(PYTEST_ARGS)


.PHONY: .pylint
.pylint:
	@echo "Running pylint..."
	@poetry run pylint --output-format=colorized --reports=n --recursive=y $(LINT_FILES)


.PHONY: .black_check
.black_check:
	@echo "Running format checks..."
	@poetry run black --safe --check --diff --color $(LINT_FILES)

