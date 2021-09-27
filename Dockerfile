FROM python:3.7

WORKDIR /opt/app

RUN pip install -U pip

# update 
RUN apt-get update && apt-get install -y curl apt-utils
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
RUN apt-get install -y nodejs
RUN node -v
RUN npm -v

# RUN npm init
RUN npm i -g semantic-release @semantic-release/commit-analyzer @semantic-release/git @semantic-release/exec \
      @semantic-release/changelog @semantic-release/release-notes-generator

# install poetry to container
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH /root/.poetry/bin:$PATH

# build project env
COPY ./pyproject.toml /opt/app/pyproject.toml
COPY ./poetry.lock /opt/app/poetry.lock
COPY ./modelon/__init__.py /opt/app/modelon/__init__.py
COPY ./README.md /opt/app/README.md
RUN poetry install
