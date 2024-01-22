FROM python:3.9.6

# Do not run as root
RUN adduser dev

ARG PIP_VERSION=23.0.1
RUN pip install -U pip==$PIP_VERSION

# update
ARG NODE_VERSION=20.x
RUN apt-get update && apt-get install -y ca-certificates curl gnupg && mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION} nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y curl apt-utils bash-completion vim git nodejs

# Install enchant c libs for spell check
RUN apt-get install -y libenchant-2-2 aspell aspell-en

ENV SHELL /bin/bash

# RUN npm init
RUN npm i -g semantic-release @semantic-release/commit-analyzer @semantic-release/git @semantic-release/exec \
  @semantic-release/changelog @semantic-release/release-notes-generator \
  @commitlint/config-conventional @commitlint/cli

USER dev

# install poetry to container
ENV POETRY_HOME /home/dev/.local
ENV POETRY_VIRTUALENVS_IN_PROJECT true
ENV POETRY_CACHE_DIR /home/dev/.poetry-cache
ARG POETRY_VERSION=1.6.1
RUN curl -sSL https://install.python-poetry.org  | POETRY_VERSION=$POETRY_VERSION python -
ENV PATH $POETRY_HOME/bin:$PATH

WORKDIR /src
