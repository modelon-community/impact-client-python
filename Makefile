.PHONY: build build-docker shell poetry unit-test test test-watch test-with-coverage lint commitlint wheel publish format regenerate-cassette vcr-test all-test experimental-test
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
IN_DOCKER_IMG := $(shell ( test -f /.dockerenv && echo 1 ) || ( test -f /opt/impact/notebook_manifest.json && echo 1 ) || echo 0)
SECRETS := $(CURDIR)/.secrets
export MODELON_IMPACT_CLIENT_INTERACTIVE:=false
export MODELON_IMPACT_CLIENT_API_KEY ?= $(shell cat $(SECRETS)/api.key)
export MODELON_IMPACT_CLIENT_URL ?= https://impact.modelon.cloud/
export MODELON_IMPACT_USERNAME ?= $(shell git config user.email)
export MODELON_IMPACT_USERID_JSON ?= $(shell cat $(SECRETS)/userid.json)

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
	$(call _run_bare, poetry install && touch .venv || rm -rf .venv)

.devcontainerenv:
	@echo "MODELON_IMPACT_CLIENT_INTERACTIVE=$${MODELON_IMPACT_CLIENT_INTERACTIVE}" > .devcontainer/devcontainer.env
	@echo "MODELON_IMPACT_CLIENT_API_KEY=$${MODELON_IMPACT_CLIENT_API_KEY}" >> .devcontainer/devcontainer.env
	@echo "MODELON_IMPACT_CLIENT_URL=$${MODELON_IMPACT_CLIENT_URL}" >> .devcontainer/devcontainer.env
	@echo "MODELON_IMPACT_USERNAME=$${MODELON_IMPACT_USERNAME}" >> .devcontainer/devcontainer.env
	@echo "MODELON_IMPACT_USERID=$${MODELON_IMPACT_USERID}" >> .devcontainer/devcontainer.env
	@echo "MODELON_IMPACT_USERID_JSON=$${MODELON_IMPACT_USERID_JSON}" >> .devcontainer/devcontainer.env
	@echo "UPDATE_CASSETTE=$${UPDATE_CASSETTE}" >> .devcontainer/devcontainer.env

build: build-docker .venv

shell:
	$(call _run_interactive, bash)

poetry:
	$(call _run_interactive, poetry shell)

unit-test: export IMPACT_PYTHON_CLIENT_EXPERIMENTAL=0
unit-test:
	$(call _run_bare, poetry run -- pytest -vv -m 'not (experimental)' ${EXTRA_PYTEST_FLAGS})

experimental-test: export IMPACT_PYTHON_CLIENT_EXPERIMENTAL=1
experimental-test:
	$(call _run_bare, poetry run -- pytest -vv -m '(experimental)' ${EXTRA_PYTEST_FLAGS})

vcr-test: 
	$(call _run_bare, poetry run -- pytest -vv -m '(vcr)' ${EXTRA_PYTEST_FLAGS})

all-test: export IMPACT_PYTHON_CLIENT_EXPERIMENTAL=1
all-test:
	$(call _run_bare, poetry run -- pytest -vv ${EXTRA_PYTEST_FLAGS})


test: build lint all-test

check_environment_variables:
	@echo "Checking for environmental variables..."
	@if [ -z "$$MODELON_IMPACT_CLIENT_API_KEY" ]; then \
		echo "Error: 'MODELON_IMPACT_CLIENT_API_KEY' variable not set"; \
		exit 1; \
	else \
		echo "Variable 'MODELON_IMPACT_CLIENT_API_KEY' is set"; \
	fi
	@if [ -z "$$MODELON_IMPACT_CLIENT_URL" ]; then \
		echo "Error: 'MODELON_IMPACT_CLIENT_URL' variable not set"; \
		exit 1; \
	else \
		echo "Variable 'MODELON_IMPACT_CLIENT_URL' is set"; \
	fi

regenerate-cassette: userid 
	IMPACT_PYTHON_CLIENT_EXPERIMENTAL=1 UPDATE_CASSETTE=1 $(MAKE) vcr-test

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
	$(call _run_bare, npx commitlint --from=HEAD~$(COMMITS_TO_LINT) --config commitlint.config.js)


lint: commitlint
	$(call _run_bare, poetry run -- bash -c "black --check modelon tests && flake8 modelon tests --config .flake8 && mypy --disallow-untyped-defs modelon && isort --check modelon tests && docformatter -c modelon --config ./pyproject.toml && sphinx-build -b spelling docs/source docs/build && pylint --disable all --enable spelling modelon")

wheel: build
	$(call _run_bare, poetry build -f wheel)

publish: build
	$(call _run_bare, npx semantic-release --ci false)

docs: build
	$(call _run_bare, bash -c "poetry run -- sphinx-apidoc -f -d 5 -o docs/source modelon && poetry run -- $(MAKE) -C ./docs clean && poetry run -- $(MAKE) -C ./docs html")

format:
	$(call _run_bare, poetry run -- bash -c "black modelon tests && isort modelon tests && docformatter -i modelon --config ./pyproject.toml")

.secrets/api.key:
	echo "Please follow README to create the api.key file"
	exit 1

userid: .secrets/userid.json check_environment_variables

.secrets/userid.json: .secrets/api.key .secrets/getuid.py
	$(call _run_bare, poetry run -- python .secrets/getuid.py)
