# Telegram bot to support VyatSU applicants

[README-ru.md](README-ru.md)
- [Telegram bot to support VyatSU applicants](#telegram-bot-to-support-vyatsu-applicants)
  - [Technologies](#technologies)
  - [Features](#features)
  - [Installation](#installation)
    - [0. Install docker and docker-compose if you haven't already](#0-install-docker-and-docker-compose-if-you-havent-already)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Create .env and .env.vector\_db in the project root](#2-create-env-and-envvector_db-in-the-project-root)
    - [3. Download and add the selected embedding model to the vector\_db\_service folder](#3-download-and-add-the-selected-embedding-model-to-the-vector_db_service-folder)
    - [4. Building the application](#4-building-the-application)
  - [Development and usage](#development-and-usage)
    - [Structure of the main bot container](#structure-of-the-main-bot-container)
    - [Main components of the vector\_db\_service container implementation](#main-components-of-the-vector_db_service-container-implementation)
    - [Main components of the arq container implementation](#main-components-of-the-arq-container-implementation)
    - [About the migrations container](#about-the-migrations-container)
    - [Additional containers and settings](#additional-containers-and-settings)


This project is a redesigned and expanded bot template based on the original [repository from lubaskinc0de](https://github.com/lubaskinc0de/tactic), implementing a clean architecture for a Telegram bot. This repository can serve as an example of how to apply the principles of clean architecture in a real project on aiogram 3 with additional features: vector search, deferred tasks and the use of embedded models.

## Technologies
- aiogram 3
- aiogram-dialog 2
- docker, docker-compose
- postgresql, alembic
- redis
- arq - Redis task queue
- qdrant - vector database
- local embedding model (e.g. [sergeyzh/rubert-mini-sts](https://huggingface.co/sergeyzh/rubert-mini-sts))

## Features

- Clean architecture: the code is easy to maintain and scale.

- The bot "remembers the history of the dialog between restarts thanks to RedisStorage.

- Flexible description of interfaces with aiogram-dialog.

- Automatic migration and initialization of the database from .json files.

- Background tasks with arq without blocking the main thread.

- Fast vector search with qdrant.

- Using your own embedding model (can be replaced with another one).

- Splitting dependencies into different requirements-*.txt to improve cacheability.

- Caching at the python package level.

- Using uv.

## Installation

### 0. Install docker and docker-compose if you haven't already

### 1. Clone the repository
```bash
git clone https://github.com/DimaOshchepkov/vyatsu_applicant_bot.git
cd vyatsu_applicant_bot
```
### 2. Create .env and .env.vector_db in the project root

.env
```env
API_TOKEN=<your Telegram bot token>

POSTGRES_USER=<database username>
POSTGRES_PASSWORD=<database user password>
POSTGRES_DB=<database name>

DB_HOST=db
DB_PORT=5432
DB_NAME=<database name>
DB_USER=<database username data>
DB_PASS=<database user password>

THRESHOLD=70

REDIS_HOST=bot_redis
REDIS_PORT=6379
```
*THRESHOLD=70 is the similarity threshold that will be used in the exam and training program recognition services.

.evn.vector_db
```env
QDRANT_QUESTION_COLLECTION=<question collection name>
QDRANT_PROGRAM_COLLECTION=<program collection name>

QDRANT_HOST_NAME=qdrant
QDRANT_PORT=6333

EMBEDDED_MODEL=<model name, for example: sergeyzh/rubert-mini-sts>
HUB_EMBEDDED_MODEL=<local model path, for example: ./src/vector_db_service/sergeyzh_rubert-mini-sts>
EMBEDDED_SIZE=<embedding size, for example: 312>

VECTOR_DB_SERVICE_CONTAINER_NAME=vector_db_service
VECTOR_DB_SERVICE_PORT=8000
```

### 3. Download and add the selected embedding model to the vector_db_service folder
Example of the expected directory structure:

```bash
vector_db_service/
└── sergeyzh_rubert-mini-sts/
├── config.json
├── pytorch_model.bin
└── ...
```

### 4. Building the application

```shell
docker-compose up --build
```

The migration container should automatically create and populate the database based on the json that was previously generated and is in the repository. The populating scripts are in [upload_data](src/tactic/infrastructure/db/migrations/upload_data).

Turn off the bot:

```shell
docker-compose down -v
```

## Development and usage

### Structure of the main bot container
The service is built according to the principles of clean architecture (Clean Architecture) and is organized into layers:

- [domain/](src/tactic/domain) — business logic:

- Entities ([entities](src/tactic/domain/entities)), value objects, etc.

- Depends on the minimum number of external libraries.

- [application/](src/tactic/application) — use cases:

- Interfaces of [repositories](src/tactic/application/common/repositories.py) and [services](src/tactic/application/services) without binding to a specific implementation.

- Orchestration of business logic in the form of [use cases](src/tactic/application/use_cases).

- No implementation details here.

- [presentation/](src/tactic/presentation) — interaction with the outside world:

- [Entry point to the application](src/tactic/presentation/bot.py).

- Handling events and [user scenarios](src/tactic/presentation/telegram).

- Contains an [interface](src/tactic/presentation/interactor_factory.py) and [implementation](src/tactic/presentation/ioc.py) of the interactor factory for dependency injection.

- [infrastructure/](src/tactic/infrastructure) — implementation of dependencies:

- Concrete implementations of the [repositories](src/tactic/infrastructure/repositories) and [services](src/tactic/infrastructure) interfaces defined in the application layer.

- [Service implementation](src/tactic/infrastructure/telegram/telegram_message_sender.py), which queues the task of sending a delayed message.

- [Service implementation](src/tactic/infrastructure/notificaton_message_sheduling_service.py), which queues the training program events.

- [Bot implementation](src/tactic/infrastructure/telegram/rate_limited_bot.py) with message sending limit

- [Middleware](src/tactic/infrastructure/middlewares/antiflood_middlewares.py) to prevent spam

- Implementations of [program](src/tactic/infrastructure/recognize_program_rapid_wuzzy.py) and [exam](src/tactic/infrastructure/recognize_exam_rapid_wuzzy.py) recognition services

- Used when configuring containers in IoC.

### Main components of the vector_db_service container implementation
The service launches an HTTP API (FastAPI) to interact with Qdrant. Other services access its [api](src/vector_db_service/app/api.py) to get data from the vector database. Please note that the service runs on CPU.

- [Script](src/vector_db_service/healthcheck.sh) for checking the service

- Scripts for loading [training](src/vector_db_service/app/load_program_collection.py) and [questions](src/vector_db_service/app/load_question_collection.py) programs. They are executed each time updating data from the relational database.

### Main components of the arq container implementation
arq is used to perform tasks in the background, such as deferred messages. This avoids blocking the main thread of the Telegram bot when working with Redis.

- [Worker](src/tactic/presentation/notification/worker.py)
- [Task](src/tactic/presentation/notification/send_delayed_message.py) - sending a timed notification

### About the migrations container
This container is designed to automate application deployment. It runs migrations (alembic) and runs [scripts](src/tactic/infrastructure/db/migrations/upload_data) for loading the database.

### Additional containers and settings
This container contains Redis, Postgres, Qdarant. You can see the settings for all containers in the [docker-compose.yml](docker-compose.yml) file. Note that many directories are mounted for more convenient development.

For convenience, orm models are moved to a [separate file](src/shared/models.py).

[Tests](src/tests) are run in a separate container test, which uses a test database test-db to isolate dependencies. This is done as part of improving CI\CD, although it may seem redundant.