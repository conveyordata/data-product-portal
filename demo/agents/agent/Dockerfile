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

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl && \
    pip install poetry==2.2.1 && \
    curl -O https://storage.googleapis.com/genai-toolbox/v0.28.0/linux/amd64/toolbox && \
    chmod +x toolbox && \
    mv toolbox /usr/local/bin/toolbox

COPY pyproject.toml ./
RUN poetry install --no-root

COPY ./dpp_agent ./dpp_agent
COPY ./skills ./skills

EXPOSE 7070

CMD ["uvicorn", "dpp_agent.server:app", "--host", "0.0.0.0", "--port", "7070", "--reload", "--reload-include", "*.yml"]
