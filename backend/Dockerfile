ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13.4-slim-bookworm@sha256:9ed09f78253eb4f029f3d99e07c064f138a6f1394932c3807b3d0738a674d33b AS base-image

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

COPY poetry.lock pyproject.toml alembic.ini sample_data.sql /
RUN poetry install --no-root

FROM base-image
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY --from=build-stage /usr/local /usr/local
COPY --from=build-stage alembic.ini .
COPY --from=build-stage sample_data.sql .

COPY ./app ./app
COPY ./templates ./templates
COPY ./alembic.ini ./alembic.ini
COPY ./VERSION ./VERSION
COPY ./sample_data.sql ./sample_data.sql

EXPOSE 5050

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5050"]
