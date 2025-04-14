---
title: Backend
description: How to set up and run the backend locally
slug: backend
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# 🚀 Backend Getting Started Guide

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

---

## 🧰 Prerequisites

### ✅ Python

- Install [Python 3.12](https://www.python.org/downloads).

### ✅ Poetry

- Install [Poetry](https://python-poetry.org/docs/#installation).
- Ensure it's available on your system path.

### ✅ Configuration (`.env` file)

All config values are read from a `.env` file in the `backend/` folder.

- Copy `example.env` ➝ `.env`
- Replace placeholder values where needed

#### Minimal Example

```env
POSTGRES_PASSWORD=abc123
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_DB=data-product-portal
POSTGRES_SERVER=localhost

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5050,http://localhost:8080
AWS_DEFAULT_REGION=eu-west-1
LOGGING_DIRECTORY=./tmp/logs
HOST=http://localhost:3000/
```

### ✅ Docker (Optional for Local Execution)

- Install [Docker](https://docs.docker.com/get-docker/)

---

## 📦 Installation

Navigate to the `backend/` directory and run:

```sh
poetry install
```

This installs all project dependencies.

---

## ▶️ Local Execution Options

<Tabs>
<TabItem value="python" label="Using Python" default>

Run the backend server on port **5050**:

```sh
poetry run python -m app.local_startup
```

</TabItem>

<TabItem value="docker" label="Using Docker">

1. Build the Docker image:

```sh
docker build . -t data-product-portal-backend
```

2. Run the container:

```sh
docker run --name data-product-portal-backend-container --env-file .env -p 3000:8080 data-product-portal-backend
```

</TabItem>
</Tabs>

---

## 🧪 Local Development Setup

### 🎯 Activate Virtual Environment

```sh
poetry shell
```

### 🔍 Use venv in Your IDE

Get the venv path:

```sh
poetry env info --path
```

Use this path in your IDE’s Python interpreter settings to enable import resolution and code execution.

### ⚙️ Run in Dev Mode

Ensure the database is up and running (see below), then:

```sh
python -m app.local_startup
```

---

## 🗃️ Data & Database Setup

A CLI tool is included to handle database setup and migrations.

All config is read from `.env`.

Run this to view help:

```sh
python -m app.db_tool --help
```

---

### 🐘 Starting the Database

Use Docker Compose:

```sh
docker compose up postgresql
```

This launches a local Postgres instance.

---

### 🏗️ Initialize Database Structure

```sh
python -m app.db_tool init
```

---

### 🌱 Seed with Sample Data

To populate the DB with dummy data:

```sh
python -m app.db_tool init "sample_data.sql"
```

Or use your own SQL file:

```sh
python -m app.db_tool init "path/to/your_data.sql"
```

### 💣 Force Reinitialization

Completely wipe and recreate the DB:

```sh
python -m app.db_tool init --force "sample_data.sql"
```

---

### 📜 Database Migrations

Create a migration:

```sh
alembic revision -m "your message"
```

Apply migrations:

```sh
python -m app.db_tool migrate
```

---

## 🧪 Testing

### ✅ Integration Testing

1. Install test dependencies:

```sh
poetry install --with test
```

2. Start the test DB:

```sh
docker compose --file test-compose.yaml up
```

3. Run tests:

```sh
poetry run pytest -v
```

---

Have questions or need help? Open an [issue](https://github.com/conveyordata/data-product-portal/issues) or start a [discussion](https://github.com/conveyordata/data-product-portal/discussions).
