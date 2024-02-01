PYTHON_VERSION := "3.12"
REPO_PATH := $(shell git rev-parse --show-toplevel)
PRE_COMMIT_HOOK_PATH := $(REPO_PATH)/.git/hooks/pre-commit
PYTEST_ARGS ?= "-vv"
PROTO_GEN_SOURCES_DIR := "."
GOOGLE_API_PATH := $(REPO_PATH)/external/lib/googleapis
GOPATH ?= $(HOME)/go
GOBIN ?= $(GOPATH)/bin
PATH := $(GOBIN):$(PATH)

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
setup: init generate-source install
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
	@mkdir -p $(PROTO_GEN_SOURCES_DIR)
	@go install github.com/google/gnostic/cmd/protoc-gen-openapi@latest
	@poetry run python -W ignore -m grpc_tools.protoc -I$(GOOGLE_API_PATH) -I proto --grpc_python_out=$(PROTO_GEN_SOURCES_DIR) --python_out=$(PROTO_GEN_SOURCES_DIR) --pyi_out=$(PROTO_GEN_SOURCES_DIR) proto/webapp/api/generated/*.proto
	@protoc proto/webapp/api/generated/*.proto -I=. -I=$(GOOGLE_API_PATH) --openapi_out=webapp/api/generated
	@poetry run datamodel-codegen \
	    --target-python-version=$(PYTHON_VERSION) \
	    --input webapp/api/generated/openapi.yaml \
	    --input-file-type openapi \
	    --output webapp/api/generated/pydantic_models.py


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
	@rm -rf webapp/api/generated .pytest_cache dist .coverage .coverage.xml

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

.PHONY: init
init: init-external install

.PHONY: init-external
init-external:
	@echo "Initializing submodules..."
	@git submodule init
	@git submodule update

.PHONY: update-external
update-external:
	@echo "Updating submodules..."
	@git submodule update --recursive --remote

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