[![FastAPI][FastAPI]][FastAPI-url]
[![Python][Python]][Python-url]
[![Postgres][Postgres]][Postgres-url]
[![Docker][Docker]][Docker-url]


# Backend Getting Started

## Prerequisites

### Python

- Install [Python 3.13](https://www.python.org/downloads) on your machine.

### UV

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) on your machine.
- Make sure it is available on your PATH.

### Configuration (.env file)

Both for local execution and local development, you need to specify some configuration arguments.

You can use the following `'env` file to get started:

```dotenv
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

## Running the project

### Installation

In order to install all project dependencies using uv,
open the 'backend' directory as a workspace in your favorite IDE and execute the command below.

```sh
uv sync
```

### Starting required services

Required services can be started using docker compose:

```bash
docker compose up -d postgresql mailhog
```

### Populating the database

In order to initialize your database with the correct structure, execute the command below from the backend folder.

```sh
uv run python -m app.db_tool init "sample_data.sql"
```

This populates the database with sample data from [sample_data.sql](sample_data.sql) .
If you want to use your custom data, you should create a .sql file similar to
the [sample_data.sql](sample_data.sql) file and reference that one in the command above.

### Running the backend

In order to run the project in development mode, after initializing the database, execute the command below.

```sh
uv run python -m app.local_startup
```

:tada:

The backend is now running on port 5050.

## Enabling the MCP server
The MCP server can work (locally or remotely) via Claude Desktop.
Install Claude Desktop and run `poetry run fastmcp install claude-desktop app/remote_proxy.py -e $(pwd) --env-file ./.env --env DISABLED_AWS='true'` in the `backend` folder. Make sure the `HOST` in your .env file is either referring to your localhost backend or the remote deployed backend.

## Development utilities

### Data

A small CLI tool is delivered to enable database setup / migrations.
The CLI tool fetches database configuration from the `.env` file in the current folder.
Make sure your database connection variables are set up correctly.
Execute `python -m app.db_tool --help` from the `backend` folder to receive the help text from this tool.

#### Force Database recreation

If you want to completely destroy and recreate the database when performing the commands listed below,
you should specify the '--force' option.

```sh
uv run python -m app.db_tool init --force "sample_data.sql"
```

### Database migrations

Whenever you develop functionality that would include a database structure change,
you will need to [create an alembic migration script](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) for it.
This comes down to running `alembic revision -m "{your message}"` in the `/backend` directory.

In order to apply this migration using the database CLI tool you need to execute the command below.

```sh
uv run python -m app.db_tool migrate
```

## Testing

### Integration testing

To run the integration tests, execute the following commands:

```sh
docker compose --file test-compose.yaml up
uv run pytest -v
```

It will install test dependencies, boot up the test database and run the tests.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

[FastAPI-url]: https://fastapi.tiangolo.com

[Docker]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white

[Docker-url]: https://www.docker.com

[Postgres]:https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white

[Postgres-url]:https://www.postgresql.org

[Python]:https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[Python-url]:https://www.python.org
