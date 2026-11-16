ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.14.10-slim-bookworm@sha256:516b51cb9db2ef061e465c803e50f64361b82cefd91e525b889b967b83e83527 AS base-image

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME='/usr/local'

RUN --mount=type=bind,src=./tools/poetry/requirements-poetry.txt,dst=/requirements-poetry.txt \
    apt-get update && apt-get upgrade -y && \
    pip install -r requirements-poetry.txt --require-hashes

COPY demo/agents/agent/pyproject.toml demo/agents/agent/poetry.lock ./
RUN poetry install --no-root

COPY demo/agents/agent/dpp_agent ./dpp_agent
COPY demo/agents/agent/skills ./skills

EXPOSE 7070

CMD ["uvicorn", "dpp_agent.server:app", "--host", "0.0.0.0", "--port", "7070", "--reload", "--reload-dir", "/agent_configs", "--reload-include", "*.yml"]
