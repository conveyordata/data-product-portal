ARG PYTHON_IMAGE=python:3.12.9-slim-bookworm@sha256:a866731a6b71c4a194a845d86e06568725e430ed21821d0c52e4efb385cf6c6f
FROM --platform=linux/amd64 ${PYTHON_IMAGE} AS build-stage

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

FROM --platform=linux/amd64 ${PYTHON_IMAGE}

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
