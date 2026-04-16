ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664 AS base-image

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
    pip install -r requirements-poetry.txt --require-hashes

COPY pyproject.toml ./
RUN poetry install --no-root

COPY ./dpp_agent ./dpp_agent
COPY ./skills ./skills

EXPOSE 7070

CMD ["uvicorn", "dpp_agent.server:app", "--host", "0.0.0.0", "--port", "7070", "--reload", "--reload-dir", "/agent_configs", "--reload-include", "*.yml"]
