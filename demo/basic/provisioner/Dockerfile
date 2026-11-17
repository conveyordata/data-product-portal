ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.15.2-slim-bookworm@sha256:96599df822d0e1c6bb700014a05c7f3c8cabc6e0f7ff3c4f9f69cee033b4b5d9 AS base-image

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

COPY tools/poetry/requirements-poetry.txt .
RUN pip install -r requirements-poetry.txt --require-hashes

COPY demo/basic/provisioner/poetry.lock demo/basic/provisioner/pyproject.toml /
COPY sdk /sdk
RUN poetry install --no-root

FROM base-image
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY --from=build-stage /usr/local /usr/local

COPY demo/basic/provisioner/provisioner ./provisioner
COPY demo/basic/provisioner/templates ./templates

EXPOSE 6060

CMD ["uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "6060"]
