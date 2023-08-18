PYTHON_VERSION := "3.11"
REPO_PATH := $(shell git rev-parse --show-toplevel)
PRE_COMMIT_HOOK_PATH := $(REPO_PATH)/.git/hooks/pre-commit
PYTEST_ARGS ?= "-vv"

ifndef CI
	# On non-CI environment, list all the python files that have been added or modified and not yet committed
	DIRTY_FILES := $(shell git diff --name-only --diff-filter=d | grep --color=never -E '\.py$$')
	# Add committed files that have been added or modified relative to origin/master
	MASTER_DIFF := $(shell git diff --name-only --diff-filter=d origin/master | grep --color=never -E '\.py$$')
	# Combine the lists and remove duplicates
	LINT_FILES := $(sort $(filter %.py,$(shell echo -e "$(MASTER_DIFF)\n$(DIRTY_FILES)" | tr ' ' '\n' | sort | uniq)))
else
	# On CI environment, list all the python files that have been modified between the current commit and master
	LINT_FILES := $(shell \
		git diff-tree --no-commit-id --name-only -r ${GITHUB_SHA} origin/master | \
		grep --color=never -E '\.py$$' | \
		xargs \
  	)
endif


.PHONY: default
default: install

.PHONY: setup
setup:
	@echo "Installing pre-commit hook..."
	@echo "#/usr/bin/env bash" > $(PRE_COMMIT_HOOK_PATH)
	@echo "make verify" >> $(PRE_COMMIT_HOOK_PATH)
	@chmod +x $(PRE_COMMIT_HOOK_PATH)

.PHONY: lock
lock: .env
	@poetry lock --no-update

.PHONY: install
install: .env
	@poetry install

.PHONY: update
update: .env
	@echo "Updating dependencies..."
	@poetry update

.PHONY: generate-source
generate-source: install
	@echo "Generating source..."
	@mkdir -p generated/proto/webapp/api
	@poetry run python -W ignore -m grpc_tools.protoc -I proto --python_out=generated/proto/webapp/api --pyi_out=generated/proto/webapp/api proto/message.proto
	@#protoc -I proto --python_out=generated/proto/webapp/api  proto/message.proto

.PHONY: test
test: generate-source .pytest

.PHONY: build
build: generate-source install
	@echo "Building package..."
	@poetry build

.PHONY: clean
clean:
	@echo "Cleaning up..."
	@poetry env remove --all
	@rm -rf generated .pytest_cache dist .coverage .coverage.xml

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
lint: install
	@# Only run linting on modified python files
	@if [ -n "$(LINT_FILES)" ]; then \
		make .mypy .pylint .black_check; \
	else \
		echo "lint: empty file list"; \
	fi

.PHONY: .coverage
.coverage:
	@poetry run coverage report --skip-covered
	@poetry run coverage xml

.PHONY: .pytest
.pytest:
	@poetry run pytest -n auto $(PYTEST_ARGS)


.PHONY: .pylint
.pylint:
	@echo "Running pylint..."
	@poetry run pylint --output-format=colorized --reports=n --recursive=y $(LINT_FILES)

.PHONY: .mypy
.mypy:
	@echo "Running mypy..."
	@poetry run mypy $(LINT_FILES)

.PHONY: .black_check
.black_check:
	@echo "Running format checks..."
	@poetry run black --safe --check --diff --color $(LINT_FILES)

.PHONY: .env
.env:
	@poetry env use python$(PYTHON_VERSION)