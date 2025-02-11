FROM --platform=linux/amd64 python:3.12.2-slim-bookworm@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997 AS build-stage

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=2.0.1
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl
RUN pip install poetry==${POETRY_VERSION}
COPY poetry.lock pyproject.toml alembic.ini sample_data.sql /

RUN poetry install --no-root

FROM --platform=linux/amd64 python:3.12.2-slim-bookworm@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997

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
