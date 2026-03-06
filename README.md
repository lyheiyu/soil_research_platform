# Soil Monitoring Platform Demo

A simple FastAPI + SQLite demo for presenting a soil monitoring platform.

## Features
- Dashboard
- Experiments page
- Sites page
- Treatments and practices page
- Sampling events page
- Indicators page
- Measurements page
- Built-in SQLite database with demo seed data

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs

## Database
The SQLite database file is created automatically as:

```text
soil_monitoring.db
```

## Platform logic

```text
Experiment -> Site -> Treatment -> Plot -> Sampling Event -> Measurement
```
