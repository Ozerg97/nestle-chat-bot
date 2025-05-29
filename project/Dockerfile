FROM python:3.11-slim

WORKDIR /project


COPY requirements.txt .env ./


RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ENV PORT=8080


CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
