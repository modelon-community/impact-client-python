.PHONY: build shell test test-watch lint wheel publish set-permissions
USER_ID := `id -u`
GROUP_ID := `id -g`

define _run
	docker run \
	--rm \
	-v $(CURDIR):/opt/app \
	-e GIT_CREDENTIALS \
	-e PYPI_USERNAME \
	-e PYPI_PASSWORD \
	modelon-impact-client-build:latest \
	$(1)
endef

define _run_it
	docker run \
	--rm -it \
	-v $(CURDIR):/opt/app \
	-e GIT_CREDENTIALS \
	-e PYPI_USERNAME \
	-e PYPI_PASSWORD \
	modelon-impact-client-build:latest \
	$(1)
endef

build:
	docker build -t modelon-impact-client-build:latest .

shell:
	$(call _run_it, /bin/bash)

test:
	$(call _run, poetry run pytest -vv)

test-watch:
	$(call _run_it, poetry run pytest-watch -- -vv)

lint:
	$(call _run,  bash -c "poetry run black modelon && poetry run flake8 modelon && poetry run mypy modelon")

wheel:
	$(call _run,  poetry build -f wheel)

publish:
	$(call _run,  npx semantic-release --ci false)

set-permissions:
	docker run -v $(CURDIR):/opt/data busybox sh -c "chmod -R 777 /opt/data && chown -R ${USER_ID}:${GROUP_ID} /opt/data"
