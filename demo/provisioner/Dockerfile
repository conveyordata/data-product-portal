ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13.11-slim-bookworm@sha256:ac4274977cc5093aa7675b5f39e59403c7b692d0bf7549b49563177ddc02552d AS base-image

FROM base-image AS build-stage

# Python configuration
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

# Poetry configuration
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY requirements-poetry.txt .
RUN pip install -r requirements-poetry.txt --require-hashes

COPY poetry.lock pyproject.toml /
RUN poetry install --no-root

FROM base-image
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY --from=build-stage /usr/local /usr/local

COPY ./provisioner ./provisioner
COPY ./templates ./templates
COPY ./VERSION ./VERSION

EXPOSE 6060

CMD ["uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "6060"]
