ARG PYTHON_IMAGE=python:3.12.2-slim-bookworm@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997
FROM --platform=linux/amd64 ${PYTHON_IMAGE} AS build-stage

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
COPY agentic-system/poetry.lock agentic-system/pyproject.toml /
COPY ./backend ./backend
WORKDIR /agentic-system
RUN poetry install --no-root

FROM --platform=linux/amd64 ${PYTHON_IMAGE}

COPY --from=build-stage /usr/local /usr/local

COPY ./agentic-system/agentic_system ./agentic-system/agentic_system
COPY ./agentic-system/VERSION ./agentic-system/VERSION

EXPOSE 5050
WORKDIR /agentic-system
CMD ["uvicorn", "agentic_system.main:app", "--host", "0.0.0.0", "--port", "5051"]
