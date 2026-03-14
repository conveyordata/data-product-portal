ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13-slim AS base-image

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME='/usr/local'

RUN apt-get update && apt-get upgrade -y && \
    pip install poetry==2.2.1

COPY pyproject.toml ./
RUN poetry install --no-root

COPY ./data_agents ./data_agents
COPY ./skills ./skills

EXPOSE 7070

CMD ["uvicorn", "data_agents.server:app", "--host", "0.0.0.0", "--port", "7070", "--reload", "--reload-dir", "/agent_configs", "--reload-include", "*.yml"]
