# Combined single-image build: React frontend + FastAPI backend
# The backend serves the frontend via FastAPI StaticFiles (SERVE_FRONTEND=true).
#
# Build from the repository root:
#   docker build -f Dockerfile.combined -t data-product-portal .

ARG PLATFORM=linux/amd64

# ---------------------------------------------------------------------------
# Stage 1 – build the React frontend
# ---------------------------------------------------------------------------
FROM --platform=${PLATFORM} node:26-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS frontend-build

WORKDIR /frontend
COPY frontend/ ./
RUN --mount=type=cache,target=/app/node_modules npm ci && npm run build:prd
# Vite outputs to /frontend/dist

ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.13.15-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e AS python-base-image

# ---------------------------------------------------------------------------
# Stage 2 – install Python dependencies (Poetry)
# ---------------------------------------------------------------------------
FROM python-base-image AS python-build

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

COPY backend/requirements-poetry.txt .
RUN pip install -r requirements-poetry.txt --require-hashes

COPY backend/poetry.lock backend/pyproject.toml backend/alembic.ini backend/sample_data.sql /
RUN poetry install --no-root

# ---------------------------------------------------------------------------
# Stage 3 – final runtime image
# ---------------------------------------------------------------------------
FROM python-base-image

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl

# Copy installed Python packages and tools from build stage
COPY --from=python-build /usr/local /usr/local

# Copy backend application
COPY backend/app ./app
COPY backend/templates ./templates
COPY backend/alembic.ini ./alembic.ini
COPY backend/VERSION ./VERSION
COPY backend/sample_data.sql ./sample_data.sql

# Copy compiled frontend assets into the location the backend expects
COPY --from=frontend-build /frontend/dist ./frontend_dist

ENV FASTEMBED_CACHE_PATH=/fastembed
RUN mkdir $FASTEMBED_CACHE_PATH && python -m app.embed

# Enable frontend serving
ENV SERVE_FRONTEND=true
ENV FRONTEND_DIST_DIR=/frontend_dist

EXPOSE 5050

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5050"]
