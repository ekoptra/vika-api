FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml /app/

RUN pip install --no-cache-dir poetry

COPY . /app

RUN poetry install --no-interaction --no-ansi --no-root

# Create upload directory
RUN mkdir -p uploads/audio

# Expose port
EXPOSE 8000

# Run application
CMD ["tail", "-f", "/dev/null"]
