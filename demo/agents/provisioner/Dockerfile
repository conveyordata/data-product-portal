ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.15.1-slim-bookworm@sha256:575f8bc12ec26542e0678bc6b60e385218248019d433157ec327264a78c3a853 AS base-image

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
    apt-get update && apt-get upgrade -y && apt-get install -y curl && \
    pip install -r requirements-poetry.txt --require-hashes

COPY sdk ./sdk
COPY demo/agents/provisioner ./demo/agents/provisioner/

WORKDIR ./demo/agents/provisioner
RUN poetry install --no-root

EXPOSE 6060

CMD ["python", "-m", "uvicorn", "provisioner.main:app", "--host", "0.0.0.0", "--port", "6060"]
