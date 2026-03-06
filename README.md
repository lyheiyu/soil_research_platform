# Soil Monitoring FastAPI Demo

A simple FastAPI backend for the soil monitoring platform demo.

## Features
- Experiment, site, treatment, practice, plot management
- Sampling events and measurements
- Indicator registry
- PostgreSQL-ready SQLAlchemy models
- Simple REST API with Swagger docs

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Docker example

```bash
docker build -t soil-monitoring-api .
docker run --env-file .env -p 8000:8000 soil-monitoring-api
```

## Database

The project includes:
- SQLAlchemy ORM models in `app/models`
- a starter PostgreSQL schema in `sql/schema.sql`

## Suggested deployment on server
- Ubuntu + Python 3.11+
- PostgreSQL 14+
- Uvicorn behind Nginx
- systemd service for process management
