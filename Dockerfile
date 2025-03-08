FROM python:3.11.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    VIRTUAL_ENV="/venv"

ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python - \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lamba

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root --no-ansi

FROM python:3.11.11-slim AS worker

COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /lamba

COPY . .

CMD ["celery", "-A", "app", "worker", "-B", "--loglevel=info", "--pidfile=./beat.pid"]
