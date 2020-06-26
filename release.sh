#!/usr/bin/env bash
poetry config repositories.modelon https://artifactory01.modelon.com/api/pypi/pypi-release-local 
poetry publish --build --repository modelon --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}
