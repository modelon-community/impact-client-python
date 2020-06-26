#!/usr/bin/env bash
poetry config repositories.modelon https://artifactory.modelon.com/artifactory/api/pypi/pypi-release-local
poetry publish --build --repository modelon --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}
