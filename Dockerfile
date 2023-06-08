FROM python:3.9.6

# Do not run as root
RUN adduser dev
WORKDIR /home/dev

ARG PIP_VERSION=23.0.1
RUN pip install -U pip==$PIP_VERSION

# update
RUN apt-get update && apt-get install -y curl apt-utils bash-completion vim git 

# Install enchant c libs for spell check
RUN apt-get install -y libenchant-2-2 aspell aspell-en

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash
RUN apt-get install -y nodejs
RUN node -v
RUN npm -v
ENV SHELL /bin/bash

# RUN npm init
RUN npm i -g semantic-release@21.0.1 @semantic-release/commit-analyzer @semantic-release/git @semantic-release/exec \
  @semantic-release/changelog @semantic-release/release-notes-generator \
  @commitlint/config-conventional @commitlint/cli

USER dev

# install poetry to container
ENV POETRY_HOME /home/dev/.local
ENV POETRY_VIRTUALENVS_PATH /home/dev/.poetry-virtualenvs
ENV POETRY_CACHE_DIR /home/dev/.poetry-cache
ARG POETRY_VERSION=1.4.0
RUN curl -sSL https://install.python-poetry.org  | POETRY_VERSION=$POETRY_VERSION python -
ENV PATH $POETRY_HOME/bin:$PATH

# build project env
WORKDIR /src
COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./modelon/__init__.py modelon/__init__.py
COPY ./README.md README.md
RUN poetry install
