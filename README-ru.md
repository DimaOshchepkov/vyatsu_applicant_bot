# Telegram-бот в поддержку абитуриентов ВятГУ
- [Telegram-бот в поддержку абитуриентов ВятГУ](#telegram-бот-в-поддержку-абитуриентов-вятгу)
  - [Технологии](#технологии)
  - [Особенности](#особенности)
  - [Установка](#установка)
    - [0. Установите docker и docker-compose, если еще не сделали этого](#0-установите-docker-и-docker-compose-если-еще-не-сделали-этого)
    - [1. Клонируйте репозиторий](#1-клонируйте-репозиторий)
    - [2. Создайте .env и .env.vector\_db в корне проекта](#2-создайте-env-и-envvector_db-в-корне-проекта)
    - [3. Скачайте и добавьте в папку vector\_db\_service выбранную модель эмбеддингов](#3-скачайте-и-добавьте-в-папку-vector_db_service-выбранную-модель-эмбеддингов)
    - [4. Сборка приложения](#4-сборка-приложения)
  - [Разработка и использование](#разработка-и-использование)
    - [Структура основного контейнера bot](#структура-основного-контейнера-bot)
    - [Основные компоненты реализации контейнера vector\_db\_service](#основные-компоненты-реализации-контейнера-vector_db_service)
    - [Основные компоненты реализации контейнера arq](#основные-компоненты-реализации-контейнера-arq)
    - [О контейнере migrations](#о-контейнере-migrations)
    - [Дополнительные контейнеры и настройки](#дополнительные-контейнеры-и-настройки)


Данный проект - переработанный и расширенный шаблон бота на базе исходного [репозитория от lubaskinc0de](https://github.com/lubaskinc0de/tactic), реализующего чистую архитектуру для Telegram-бота. Этот репозиторий может служить примером того, как применять принципы чистой архитектуры в реальном проекте на aiogram 3 с дополнительными возможностями: векторным поиском, отложенными задачами и использованием эмбедед моделей.

## Технологии
- aiogram 3
- aiogram-dialog 2
- docker, docker-compose
- postgresql, alembic
- redis
- arq - очередь задач на Redis
- qdrant - векторная база данных
- локальная модель эмбеддингов (например, [sergeyzh/rubert-mini-sts](https://huggingface.co/sergeyzh/rubert-mini-sts))

## Особенности

- Чистая архитектура: код легко поддерживать и масштабировать.

- Бот "помнит" историю диалога между перезапусками благодаря RedisEventIsolation.

- Гибкое описание интерфейсов с aiogram-dialog.

- Автоматическая миграция и инициализация базы из .json файлов.

- Фоновые задачи с arq без блокировки основного потока.

- Быстрый векторный поиск с помощью qdrant.

- Использование собственной модели эмбеддингов (можно заменить на другую).

- Разделение зависимостей на разные requirements-*.txt для улучшения кешироемости.

- Кеширование на уровне пакетов python.

- Использование uv.

## Установка

### 0. Установите docker и docker-compose, если еще не сделали этого

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/DimaOshchepkov/vyatsu_applicant_bot.git
cd vyatsu_applicant_bot
```
### 2. Создайте .env и .env.vector_db в корне проекта

.env
```env
API_TOKEN=<токен вашего Telegram-бота>

POSTGRES_USER=<имя пользователя базы данных>
POSTGRES_PASSWORD=<пароль пользователя базы данных>
POSTGRES_DB=<название базы данных>

DB_HOST=db
DB_PORT=5432
DB_NAME=<название базы данных>
DB_USER=<имя пользователя базы данных>
DB_PASS=<пароль пользователя базы данных>

THRESHOLD=70

REDIS_HOST=bot_redis
REDIS_PORT=6379
```
*THRESHOLD=70 - это порог схожести, который будет использоваться в сервисах распознавания экзаменов и программ обучения.


.env.vector_db
```env
QDRANT_QUESTION_COLLECTION=<название коллекции для вопросов>
QDRANT_PROGRAM_COLLECTION=<название коллекции для программ>

QDRANT_HOST_NAME=qdrant
QDRANT_PORT=6333

EMBEDDED_MODEL=<имя модели, например: sergeyzh/rubert-mini-sts>
HUB_EMBEDDED_MODEL=<путь к локальной модели, например: ./src/vector_db_service/sergeyzh_rubert-mini-sts>
EMBEDDED_SIZE=<размер эмбеддинга, например: 312>

VECTOR_DB_SERVICE_CONTAINER_NAME=vector_db_service
VECTOR_DB_SERVICE_PORT=8000
```

### 3. Скачайте и добавьте в папку vector_db_service выбранную модель эмбеддингов
 Пример ожидаемой структуры директории:

```bash
vector_db_service/
└── sergeyzh_rubert-mini-sts/
    ├── config.json
    ├── pytorch_model.bin
    └── ...
```

### 4. Сборка приложения

```shell
docker-compose up --build
```

Контейнер migration должно автоматически создать и заполнить базу данных на основе json, который был заранее сформирован и лежит в репозитории. Скрипты заполнения лежат в [upload_data](src/tactic/infrastructure/db/migrations/upload_data).

Выключить бота:

```shell
docker-compose down -v
```

## Разработка и использование


### Структура основного контейнера bot
Сервис построен по принципам чистой архитектуры (Clean Architecture) и организован по слоям:

- [domain/](src/tactic/domain) — бизнес-логика:

    - Сущности ([entities](src/tactic/domain/entities)), value objects и т.д..

    - Зависит от минимального количества внешних библиотек.

- [application/](src/tactic/application) — сценарии использования (Use Cases):

    - Интерфейсы [репозиториев](src/tactic/application/common/repositories.py) и [сервисов](src/tactic/application/services) без привязки к конкретной реализации.

    - Оркестрация бизнес-логики в виде [сценариев использования](src/tactic/application/use_cases).

    - Здесь нет деталей реализации.

- [presentation/](src/tactic/presentation) — взаимодействие с внешним миром:

    - [Точка входа в приложение](src/tactic/presentation/bot.py).

    - Обработка событий и [пользовательских сценариев](src/tactic/presentation/telegram).

    - Содержит [интерфейс](src/tactic/presentation/interactor_factory.py) и [реализацию](src/tactic/presentation/ioc.py) interactor factory для внедрения зависимостей.



- [infrastructure/](src/tactic/infrastructure) — реализация зависимостей:

    - Конкретные реализации интерфейсов [репозиториев](src/tactic/infrastructure/repositories) и [сервисов](src/tactic/infrastructure), определенных в application слое.

    - [Реализация сервиса](src/tactic/infrastructure/telegram/telegram_message_sender.py), которая ставит в очередь задачу отправить отложенное сообщение.

    - [Реализация сервиса](src/tactic/infrastructure/notificaton_message_sheduling_service.py), которая ставит события программы обучения в очередь.

    - [Реализация бота](src/tactic/infrastructure/telegram/rate_limited_bot.py) с ограничением отправки сообщений

    - [Мидлвари](src/tactic/infrastructure/middlewares/antiflood_middlewares.py) для предотвращения спама

    - Реализации сервисов распознавания [программ](src/tactic/infrastructure/recognize_program_rapid_wuzzy.py) и [экзаменов](src/tactic/infrastructure/recognize_exam_rapid_wuzzy.py)

    - Используется при настройке контейнеров в IoC.

### Основные компоненты реализации контейнера vector_db_service
Сервис запускает HTTP API (FastAPI) для взаимодействия с Qdrant. Остальные сервисы обращаются к его [api](src/vector_db_service/app/api.py) для получения данных из векторной базы данных. Обратите внимание, что сервис работает на CPU.

- [Скрипт](src/vector_db_service/healthcheck.sh) для проверки работы сервиса

- Скрипты для загрузки программ [обучения](src/vector_db_service/app/load_program_collection.py) и [вопросов](src/vector_db_service/app/load_question_collection.py). Они выполняются каждый раз обновляя данные из реляционной базы данных.


### Основные компоненты реализации контейнера arq
arq используется для выполнения задач в фоне, например - отложенных сообщений. Это позволяет избежать блокировки основного потока Telegram-бота при работе с Redis.

- [Worker](src/tactic/presentation/notification/worker.py)
- [Задача](src/tactic/presentation/notification/send_delayed_message.py) - отправка уведомления по времени

### О контейнере migrations
Этот контейнер создан для автоматизации разворачивания приложения. Он выполняет миграции (alembic) и запускает [скрипты](src/tactic/infrastructure/db/migrations/upload_data) загрузки базы данных.

### Дополнительные контейнеры и настройки
Этот контейнер содержит Redis, Postgres, Qdrant. Настройку всех контейнеров вы можете увидеть в файле [docker-compose.yml](docker-compose.yml). Обратите внимание, что многие директории примонтированы для более удобной разработки.

Для удобства orm модели вынесены в [отдельный файл](src/shared/models.py).

[Тесты](src/tests) запускаются в отдельном контейнере test, который используюет тестовую базу данных test-db для изоляции зависимостей. Это сделано для в рамках улучшения CI\CD, хотя может показаться избыточным.

