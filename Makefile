.PHONY: build coverage shell unit-test test test-watch lint wheel publish
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)

define _run
	docker run \
	--rm $(1) \
	-v $(CURDIR):/home/dev/src \
	-u $(USER_ID):$(GROUP_ID) \
	-e GIT_CREDENTIALS \
	-e PYPI_USERNAME \
	-e PYPI_PASSWORD \
	modelon-impact-client-build:latest \
	$(2)
endef

define _run_interactive
	$(call _run, -it, $(1))
endef

define _run_bare
	$(call _run, , $(1))
endef

build:
	docker build -t modelon-impact-client-build:latest .

coverage:
	$(call _run_bare, poetry run pytest --cov-report=html:htmlcov --cov-report=term --cov=modelon)

shell:
	$(call _run_interactive, //bin/bash)

poetry:
	$(call _run_interactive, //bin/sh -c "poetry shell")

unit-test:
	$(call _run_bare, poetry run pytest -vv)

test: build unit-test lint

test-watch: build
	$(call _run_interactive, poetry run pytest-watch -- -vv)

lint:
	$(call _run_bare, bash -c "poetry run black -S modelon && poetry run flake8 modelon && poetry run mypy modelon")

wheel: build
	$(call _run_bare, poetry build -f wheel)

publish: build
	$(call _run_bare, npx semantic-release --ci false)
