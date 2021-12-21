FROM python:3.7

# Do not run as root
RUN adduser dev
WORKDIR /home/dev

RUN pip install -U pip

# update 
RUN apt-get update && apt-get install -y curl apt-utils bash-completion
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
RUN apt-get install -y nodejs
RUN node -v
RUN npm -v

# RUN npm init
RUN npm i -g semantic-release @semantic-release/commit-analyzer @semantic-release/git @semantic-release/exec \
      @semantic-release/changelog @semantic-release/release-notes-generator

USER dev

# install poetry to container
ENV POETRY_HOME /home/dev/poetry
ENV POETRY_VIRTUALENVS_PATH /home/dev/poetry-virtualenvs
ENV POETRY_CACHE_DIR /home/dev/poetry-cache
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH $POETRY_HOME/bin:$PATH

# build project env
WORKDIR /home/dev/src
COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./modelon/__init__.py modelon/__init__.py
COPY ./README.md README.md
RUN poetry install
