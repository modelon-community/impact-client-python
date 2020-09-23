#!/usr/bin/env bash
poetry publish --build --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}
