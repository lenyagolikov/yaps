# Export application env vars
include deploy/.env.test
export

PROJECT_NAME := yaps
PROJECT_SRC := yaps
VERSION := 0.1

IMAGE_NAME := yaps
APP_CONTAINER_NAME := $(PROJECT_NAME)
DB_CONTAINER_NAME := pg
ELASTIC_CONTAINER_NAME := elastic

DOCKER := env docker
PYTHON := env python3
COMPOSE := env docker-compose

TEST_DATA_SRC := tests/tests_data
TEST_DATA := $(TEST_DATA_SRC)/yaps.sql.gz
TEST_DATA_ES := $(TEST_DATA_SRC)/products.csv

MIGRATE_FILES_ES := $(shell find $(ES_DUMP_FILES) -maxdepth 1 -type f -name "*.csv" -print0 | xargs -d " ")

help:
	@echo "Run:"
	@echo "make run-dev                    - Run app in dev mode"
	@echo "make run-prod                   - Run app in prod mode"
	@echo "make venv                       - Create python venv"
	@echo
	@echo "Code style:"
	@echo "make lint                       - Run pylint and flake8 for checking code style"
	@echo "make cs                         - Fix code style with black"
	@echo
	@echo "Tests:"
	@echo "make test                       - Run tests with coverage"
	@echo "make test2                      - Run tests with coverage version 2"
	@echo "make tests-coverage-report      - Run tests and print coverage report"
	@echo "make tests-html-coverage-report - Run tests and show html coverage report"
	@echo
	@echo "Config:"
	@echo "make show-config                - Show project env vars"
	@echo "make show-prod-config           - Show project prod env vars"
	@echo
	@echo "Docker:"
	@echo "make docker-build               - Build app with docker-compose"
	@echo "make docker-run                 - Run app with docker-compose"
	@echo "make docker-start               - Start stopped app with docker-compose"
	@echo "make docker-stop                - Stop docker-compose with app"
	@exit 0


run-dev: start-db start-elastic migrate
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

run-prod: docker-run

migrate-es:
	$(PYTHON) -m yaps.es init
	$(PYTHON) -m yaps.es import $(MIGRATE_FILES_ES)

venv:
	$(PYTHON) -m venv venv
	$(PYTHON) -m pip install -r requirements.dev.txt


show-config:
	cat deploy/.env

show-prod-config:
	cat deploy/.env.prod


pylint:
	$(PYTHON) -m pylint $(PROJECT_SRC)

flake8:
	$(PYTHON) -m flake8 $(PROJECT_SRC)

lint: pylint flake8


cs:
	$(PYTHON) -m black $(PROJECT_SRC)


docker-build:
	sudo $(COMPOSE) build

docker-run:
	sudo $(COMPOSE) down
	sudo $(COMPOSE) build
	sudo $(COMPOSE) up -d

docker-stop:
	sudo $(COMPOSE) stop

docker-start:
	sudo $(COMPOSE) start || sudo $(COMPOSE) up -d


start-db:
	sudo $(DOCKER) start $(DB_CONTAINER_NAME) || sudo $(DOCKER) run -d --name $(DB_CONTAINER_NAME) -p 5432:5432 -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) postgres:13.0

create-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "CREATE DATABASE $(TEST_POSTGRES_DB)" $(POSTGRES_DB)
	zcat $(TEST_DATA) | sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) $(TEST_POSTGRES_DB)

create-test-es:
	$(PYTHON) -m yaps.es import $(TEST_DATA_ES)

drop-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "DROP DATABASE $(TEST_POSTGRES_DB)" $(POSTGRES_DB)

drop-test-es:
	curl -XDELETE $(ES_HOSTS)/products

start-elastic:
	sudo sysctl -w vm.max_map_count=262144
	sudo $(DOCKER) start $(ELASTIC_CONTAINER_NAME) || sudo $(DOCKER) run -d -e "discovery.type=single-node" -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" --name $(ELASTIC_CONTAINER_NAME) -p 9200:9200 docker.elastic.co/elasticsearch/elasticsearch:7.15.2
	sleep 30
	$(PYTHON) -m yaps.es init

stop-elastic:
	sudo $(DOCKER) stop $(ELASTIC_CONTAINER_NAME)

stop-db:
	sudo $(DOCKER) stop $(DB_CONTAINER_NAME)

tests-coverage-report: test
	$(PYTHON) -m coverage report

tests-html-coverage-report: test
	$(PYTHON) -m coverage html
	$(PYTHON) -m webbrowser htmlcov/index.html

run-tests:
	$(PYTHON) -m pytest -vv --cov=$(PROJECT_SRC) --cov-report=term-missing tests

migrate:
	sleep 3
	$(PYTHON) -m alembic upgrade head

test: start-db start-elastic create-test-db create-test-es run-tests drop-test-db drop-test-es stop-db stop-elastic

test2: start-db start-elastic run-tests

start-db-ci:
	$(DOCKER) start $(DB_CONTAINER_NAME) || $(DOCKER) run -d --name $(DB_CONTAINER_NAME) -p 5432:5432 -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) postgres:13.0
	sleep 6

start-elastic-ci:
	$(DOCKER) start $(ELASTIC_CONTAINER_NAME) || $(DOCKER) run -e "discovery.type=single-node" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" --name $(ELASTIC_CONTAINER_NAME) -p 9200:9200 -d docker.elastic.co/elasticsearch/elasticsearch:7.15.2
	sleep 120
	$(PYTHON) -m yaps.es init || $(DOCKER) logs $(ELASTIC_CONTAINER_NAME)
    curl "localhost:9200"

create-test-db-ci:
	$(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "CREATE DATABASE $(TEST_POSTGRES_DB)" $(POSTGRES_DB)
	zcat $(TEST_DATA) | $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) $(TEST_POSTGRES_DB)
	zcat $(TEST_OFFERS) | $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) $(TEST_POSTGRES_DB)

drop-test-db-ci:
	$(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "DROP DATABASE $(TEST_POSTGRES_DB)" $(POSTGRES_DB)


test-ci: start-db-ci start-elastic-ci create-test-db-ci create-test-es run-tests drop-test-db-ci drop-test-es

run_fill_db: start_fill_db
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

just_run:
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

start_fill_db:
	$(DOCKER) rm --force $(DB_CONTAINER_NAME)
	$(DOCKER) run -d --name $(DB_CONTAINER_NAME) -p 5432:5432 -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) postgres:13.0
	sleep 10
	zcat $(TEST_DATA) | psql -U $(POSTGRES_USER) -h 127.0.0.1 $(POSTGRES_DB)

run_fill_db_in_docker:
	$(DOCKER) run -d --name $(DB_CONTAINER_NAME) -p 5432:5432 -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) postgres:13.0
	sleep 10
	zcat $(TEST_DATA) | sudo env docker exec -i pg psql -U $(POSTGRES_USER) $(POSTGRES_DB)
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

run-dev-v2: run_fill_db_in_docker migrate
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

db-dump:
	sudo $(DOCKER) exec $(DB_CONTAINER_NAME) pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) | gzip > tests/tests_data/$(POSTGRES_DB).sql.gz
