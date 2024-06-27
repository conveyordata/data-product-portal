[![FastAPI][FastAPI]][FastAPI-url]
[![Python][Python]][Python-url]
[![Postgres][Postgres]][Postgres-url]
[![Docker][Docker]][Docker-url]


# Backend Getting Started

## Prerequisites

### Python
- Install [Python 3.12](https://www.python.org/downloads) on your machine.

### Poetry
- Install [Poetry](https://python-poetry.org/docs/#installation) on your machine.
- Make sure it is available on your PATH.

### Configuration (.env file)

Both for local execution and local development, you need to specify some configuration arguments.
All configuration values for this project are read from a `.env` file in the root folder.
Please look at [example.env](../example.env) to see which values are mandatory and which can be omitted.
Then copy and paste the content of `example.env` to `.env` you created and replace values where necessary.

#### Minimal `.env` file
A minimal example of a `.env` file can be found below. This is enough to get things started.
```
POSTGRESQL_PASSWORD=vy/*&4%osdivdadkr238ry7t2123
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_DATABASE=data-product-portal
POSTGRESQL_SERVER=localhost

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5050,http://localhost:8080
AWS_DEFAULT_REGION=eu-west-1
LOGGING_DIRECTORY=./tmp/logs
```

### Docker (only when you want to use Docker for local execution)
- Install [Docker](https://docs.docker.com/get-docker/) on your machine.

## Installation

In order to install all project dependencies using poetry, open the 'backend' directory as a workspace in you favorite IDE and execute the command below.
  ```sh
  poetry install
  ```

## Local Execution

In order to just run the backend locally, you can choose between the 2 options below.

### Using Python

- To start a local server, simply execute the command below. This will start a backend server on port 5050.
  ```sh
  poetry run python -m app.local_startup
  ```

### Using Docker
- Ensure your Docker service is running.
- Build the Docker image by executing the command below.
  ```sh
  docker build . -t data-product-portal-backend
  ```
- Run the Docker container by executing the command below.
  ```sh
  docker run --name data-product-portal-backend-container --env-file ../.env -p 3000:8080  data-product-portal-backend
  ```

## Local Development

### Virtual environment
To effectively develop you need to activate a virtual environment. This allows you to run a python interpreter with the same dependencies installed as your package requires.
- To activate a virtual environment, execute the command below.
  ```sh
  poetry shell
  ```

### Including the virtual environment in your IDE
- Execute the command below to display the location of your virtual environment.
  ```sh
  poetry env info --path
  ```
- You can use this location to pass in your IDE to be able to run the source code from your IDE and to resolve all imports.


### Run in dev mode

Before running the project in development mode, make sure you have the database up and
running [as described here](#Database-initialization).

In order to run the project in development mode, after initializing the database, execute the command below.
  ```sh
  python -m app.local_startup
  ```

## Data
A small CLI tool is delivered to enable database setup / migrations.
The CLI tool fetches database configuration from the `.env` file in the root of the project. Make sure your database connection variables are set
up correctly.
Execute `python -m app.db_tool --help` from the `backend` folder to receive the help text from this tool.

### Database
- The easiest way of setting up your database is to run `docker compose up postgresql` in the root of the project, this will create a Postgres database that your local development server will connect to.

### Database initialization
#### Structure
In order to initialize your database with the correct structure, execute the command below from the backend folder.
 ```sh
  python -m app.db_tool init
  ```

#### Sample Data
If you want to seed your database with sample data, you can optionally pass in the path to a .sql file that will populate the tables.

Below you can see the command you need to execute if you want to use the dummy sample data available in this repository.
 ```sh
  python -m app.db_tool init "sample_data.sql"
  ```
If you want to use your custom data, you should create a .sql file similar to the [sample_data.sql](sample_data.sql) file and reference that one in teh command above.

#### Force Database recreation
If you want to completely destroy and recreate the database when performing the commands listed below, you should specify the '--force' option.
  ```sh
  python -m app.db_tool init --force "sample_data.sql"
  ```

### Database migrations
Whenever you develop functionality that would include a database structure change, you will need to [create an alembic migration script](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) for it.

In order to apply this migration using the database CLI tool you need to execute the command below.
  ```sh
  python -m app.db_tool migrate
  ```

## Testing
### Integration testing
- Ensure your Docker service is running.
- Get the test database up and running by executing the command below.

  ```sh
  docker compose --file test-compose.yaml up
  ```

- Run the tests by executing the command below.

  ```sh
  poetry run pytest -v
  ```

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
