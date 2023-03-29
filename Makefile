.PHONY: build shell unit-test test test-watch lint wheel publish docformatter
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
IN_DOCKER_IMG := $(shell test -f /.dockerenv && echo 1 || echo 0)

ifdef WITH_COVERAGE
EXTRA_PYTEST_FLAGS+=--cov-config=.coveragerc --cov-report=html:htmlcov --cov-report=term --cov=modelon/impact/client
endif

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

build:
	@if [ $(IN_DOCKER_IMG) -eq 0 ]; then \
        docker build -t modelon-impact-client-build:latest . ;\
    fi

shell:
	$(call _run_interactive, bash)

poetry:
	$(call _run_interactive, poetry shell)

unit-test:
	$(call _run_bare, poetry run -- pytest -vv ${EXTRA_PYTEST_FLAGS})

test: build unit-test lint docformatter-check docs-spell-check

test-with-coverage:
	$(MAKE) WITH_COVERAGE=YES test

test-watch: build
	$(call _run_interactive, poetry run -- pytest-watch -- -vv ${EXTRA_PYTEST_FLAGS})

commitlint:
# Will lint the latest 10 or all commits, whicher is the smallest number:
	$(eval REV_LIST_HEAD=$$(shell (git rev-list HEAD --count --first-parent)))
# rev-list gives 1 too many commits...
	$(eval COMMITS_IN_REPO=$$(shell (expr $(REV_LIST_HEAD) - 1)))
	$(eval COMMITS_TO_LINT=$$(shell (echo $(COMMITS_IN_REPO) && echo 10) | sort -g | head -n1))
	@echo "Will lint the last '$(COMMITS_TO_LINT)' commits"
	$(call _run_bare, npx commitlint --from=HEAD~$(COMMITS))


lint: commitlint
	$(call _run_bare, bash -c "poetry run -- black -S modelon && poetry run -- flake8 modelon --config .flake8 && poetry run -- mypy --disallow-untyped-defs modelon")


wheel: build
	$(call _run_bare, poetry build -f wheel)

publish: build
	$(call _run_bare, npx semantic-release --ci false)

docformatter: build
	$(call _run_bare, bash -c "poetry run -- docformatter -i modelon --config ./pyproject.toml ")

docformatter-check: build 
	$(call _run_bare, bash -c "poetry run -- docformatter -c modelon --config ./pyproject.toml ")

docs-spell-check: build
	$(call _run_bare, bash -c "poetry run -- sphinx-build -b spelling docs/source docs/build")

docs: build
	$(call _run_bare, bash -c "poetry run -- sphinx-apidoc -f -d 5 -o docs/source modelon && poetry run -- $(MAKE) -C ./docs clean && poetry run -- $(MAKE) -C ./docs html")
