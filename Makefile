.PHONY: build build-docker shell poetry unit-test test test-watch test-with-coverage lint commitlint wheel publish format
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
IN_DOCKER_IMG := $(shell test -f /.dockerenv && echo 1 || echo 0)

define _run
	@if [ $(IN_DOCKER_IMG) -eq 1 ]; then \
		$(2);\
	else \
		docker run \
		--rm $(1) \
		-v $(CURDIR):/src \
		-u $(USER_ID):$(GROUP_ID) \
		--env-file docker.env \
		modelon-impact-client-build:latest \
		$(2);\
	fi
endef

define _run_interactive
	$(call _run, -it, $(1))
endef

define _run_bare
	$(call _run, , $(1))
endef

ifdef WITH_COVERAGE
EXTRA_PYTEST_FLAGS+=--cov-config=.coveragerc --cov-report=html:htmlcov --cov-report=term --cov=modelon/impact
endif

build-docker:
	@if [ $(IN_DOCKER_IMG) -eq 0 ]; then \
        docker build -t modelon-impact-client-build:latest . ;\
    fi

.venv: poetry.lock pyproject.toml
	$(call _run_bare, poetry install && touch .venv)

build: build-docker .venv

shell:
	$(call _run_interactive, bash)

poetry:
	$(call _run_interactive, poetry shell)

unit-test:
	$(call _run_bare, poetry run -- pytest -vv -m 'not (experimental)' ${EXTRA_PYTEST_FLAGS})

experimental-test:
	$(call _run_bare, poetry run -- pytest -vv ${EXTRA_PYTEST_FLAGS})

test: build lint
	IMPACT_PYTHON_CLIENT_EXPERIMENTAL=0 $(MAKE) unit-test
	IMPACT_PYTHON_CLIENT_EXPERIMENTAL=1 $(MAKE) experimental-test 

test-with-coverage:
	$(MAKE) WITH_COVERAGE=YES test

test-watch: build
	$(call _run_bare, poetry run -- pytest-watch -- -vv ${EXTRA_PYTEST_FLAGS})

commitlint:
# Will lint the latest 10 or all commits, whicher is the smallest number:
	$(eval REV_LIST_HEAD=$$(shell (git rev-list HEAD --count --first-parent)))
# rev-list gives 1 too many commits...
	$(eval COMMITS_IN_REPO=$$(shell (expr $(REV_LIST_HEAD) - 1)))
	$(eval COMMITS_TO_LINT=$$(shell (echo $(COMMITS_IN_REPO) && echo 10) | sort -g | head -n1))
	@echo "Will lint the last '$(COMMITS_TO_LINT)' commits"
	$(call _run_bare, npx commitlint --from=HEAD~$(COMMITS) --config commitlint.config.js)


lint: commitlint
	$(call _run_bare, poetry run -- bash -c "black -S --check modelon && flake8 modelon --config .flake8 && mypy --disallow-untyped-defs modelon && isort --check modelon && docformatter -c modelon --config ./pyproject.toml && sphinx-build -b spelling docs/source docs/build && pylint --disable all --enable spelling modelon")

wheel: build
	$(call _run_bare, poetry build -f wheel)

publish: build
	$(call _run_bare, npx semantic-release --ci false)

docs: build
	$(call _run_bare, bash -c "poetry run -- sphinx-apidoc -f -d 5 -o docs/source modelon && poetry run -- $(MAKE) -C ./docs clean && poetry run -- $(MAKE) -C ./docs html")

format:
	$(call _run_bare, poetry run -- bash -c "black -S modelon && docformatter -i modelon --config ./pyproject.toml")