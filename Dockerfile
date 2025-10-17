FROM python:3.13.5-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app

COPY ./scripts /app/scripts

COPY ./requirements.txt ./alembic.ini /app/

COPY ./app /app/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

# CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]