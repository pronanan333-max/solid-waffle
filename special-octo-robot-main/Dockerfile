FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# Collect static files (requires settings that don't require DB access at build time)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "social.wsgi:application", "--bind", "0.0.0.0:8000"]
