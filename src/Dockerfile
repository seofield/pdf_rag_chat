FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y curl git build-essential g++ \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean


ENV PATH="/root/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=false

COPY ./src /app

RUN poetry lock --no-update && poetry install

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port","8000", "--reload"]