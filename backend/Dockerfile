ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13.13-slim-bookworm@sha256:eabbb62836ee44c18d350821e9f78488bcf65134bf763ae9989d63e611fa04d9 AS base-image

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

COPY backend/requirements-poetry.txt .
RUN pip install -r requirements-poetry.txt --require-hashes

COPY backend/poetry.lock backend/pyproject.toml backend/alembic.ini backend/sample_data.sql /
COPY sdk /sdk
RUN poetry install --no-root

FROM base-image
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY --from=build-stage /usr/local /usr/local
COPY --from=build-stage alembic.ini ./alembic.ini
COPY --from=build-stage sample_data.sql ./sample_data.sql

COPY ./backend/app ./app
COPY ./backend/templates ./templates
COPY ./backend/alembic.ini ./alembic.ini
COPY ./backend/VERSION ./VERSION
COPY ./backend/sample_data.sql ./sample_data.sql
ENV FASTEMBED_CACHE_PATH=/fastembed

RUN mkdir $FASTEMBED_CACHE_PATH && python -m app.embed

EXPOSE 5050

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5050"]
