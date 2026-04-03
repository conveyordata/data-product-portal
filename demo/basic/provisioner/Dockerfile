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

COPY demo/basic/provisioner/requirements-poetry.txt .
RUN pip install -r requirements-poetry.txt --require-hashes

# Copy pyproject.toml and lock file; SDK is expected at ../../../sdk relative to pyproject.toml,
# which resolves to /sdk when pyproject.toml is at /.
COPY demo/basic/provisioner/poetry.lock demo/basic/provisioner/pyproject.toml /
COPY sdk/ /sdk/
RUN poetry install --no-root

FROM base-image
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY --from=build-stage /usr/local /usr/local

COPY demo/basic/provisioner/provisioner ./provisioner
COPY demo/basic/provisioner/templates ./templates
COPY demo/basic/provisioner/VERSION ./VERSION

EXPOSE 6060

CMD ["uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "6060"]
