# FPL Stat Aggregator

This is an aggregation tool that gathers data from the English Premier League Fantasy [site](https://fantasy.premierleague.com/statistics), parses it into relevant fields that make up the stats, and stores it in a database.

## Toolset

1. [Python](https://www.python.org/) - Written as a Python script
2. [Playwright](https://playwright.dev/python/docs/intro) - Used to scrape the data
3. [MongoDB](https://www.mongodb.com/) - NoSQL data store
4. [Docker](https://www.docker.com/) - Application containerization
5. [GCP Cloud Run](https://cloud.google.com/run?hl=en) - Running the containerized application in the cloud

## Getting started

The aggregator application is written in Python. I'll be the first to admit that I'm not an experienced Python developer, but I did my best to follow what I know to be standard practices in regard to the structure of the app.

For development, I use a Python virtual environment or `venv` to promote a consistent and isolated environment. While this isn't a requirement for develop, I'd recommend at least [learning about it](https://docs.python.org/3/library/venv.html). The app also utilizes a `requirements.txt` file to track dependency versions.

The toolset section above is referring to the tools/dependencies for production. The requirements for development include Python and a Mongo database (the Mongo instance can be local or in a cloud-hosted cluster like MongoDB Atlas). Steps to run the app either locally or in Docker are listed below.

The application also relies on a handful of environment variables related to MongoDB and the gunicorn web server. If you are running this locally you'll need to have these variables available in the context the app is running in. For this, I use a `.env` file locally which can also be passed into a Docker container.

```shell
CONNECTION_STRING=your_connection_string
MONGO_COLLECTION=collection_name
ENVIRONMENT=local
PORT=8080
```

## Running the app

The app can be run locally with or without a Docker container. Running in the Docker container may be more streamlined and provide a closer experience to what will be ran in production.

### Running in Docker

1. Build the Docker image:

```shell
# Run command in the src/aggregator directory
docker build -t fpl-stat-aggregator:latest -f ./Dockerfile .
```

2. Run a Docker container from the image:

```shell
docker run -p 8080:8080 --env-file .env fpl-stat-aggregator:latest
```

3. Make a cURL request to the running app:

```shell
curl -X POST http://localhost:8080/
```

### Running without Docker

1. Install the required dependencies:

```shell
pip install -r requirements.txt
```

2. Run the application:

```shell
gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app
```

This should result in some info logs:

```
[INFO] Starting gunicorn 20.1.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: gthread
[INFO] Booting worker with pid: some_pid
```

3. Make a cURL request to start data aggregation:

```shell
curl -X POST http://localhost:8080/
```
