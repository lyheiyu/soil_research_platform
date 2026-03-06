# Soil Monitoring Platform (Project-aware CRUD demo)

This is a small FastAPI + SQLite platform demo for soil monitoring workflows.

## Main data logic

Project -> Experiment -> Treatment -> Plot -> Sample -> Measurements

Key point:
- `experiment_code` is only unique within a project
- treatments are linked to a project-specific experiment

## Features

- CRUD pages for Projects, Experiments, Treatments, Practices, Plots, Indicators, Samples, Measurements
- Query Center with filters by project, experiment, treatment, and indicator
- SQLite database auto-created on startup
- Seed demo data inserted automatically
- Swagger docs at `/docs`

## Run

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs

## Notes

- Database file: `soil_monitoring.db`
- This is a lightweight server-rendered demo using FastAPI + Jinja2 + SQLite.
