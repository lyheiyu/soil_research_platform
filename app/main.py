from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .database import Base, engine, get_db, SessionLocal
from .models import Experiment, Indicator, Measurement, Plot, Practice, SamplingEvent, Site, Treatment
from .seed import seed_demo_data

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title='Soil Monitoring Platform Demo', version='1.0.0')
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_demo_data(db)


@app.get('/', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    stats = {
        'experiments': db.query(func.count(Experiment.id)).scalar(),
        'sites': db.query(func.count(Site.id)).scalar(),
        'treatments': db.query(func.count(Treatment.id)).scalar(),
        'plots': db.query(func.count(Plot.id)).scalar(),
        'samples': db.query(func.count(SamplingEvent.id)).scalar(),
        'indicators': db.query(func.count(Indicator.id)).scalar(),
        'measurements': db.query(func.count(Measurement.id)).scalar(),
    }
    recent_samples = db.query(SamplingEvent).order_by(SamplingEvent.id.desc()).limit(5).all()
    return templates.TemplateResponse('dashboard.html', {'request': request, 'stats': stats, 'recent_samples': recent_samples, 'title': 'Dashboard'})


@app.get('/experiments', response_class=HTMLResponse)
def experiments_page(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).options(joinedload(Experiment.sites), joinedload(Experiment.treatments)).all()
    return templates.TemplateResponse('experiments.html', {'request': request, 'experiments': experiments, 'title': 'Experiments'})


@app.get('/sites', response_class=HTMLResponse)
def sites_page(request: Request, db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.experiment), joinedload(Site.plots)).all()
    return templates.TemplateResponse('sites.html', {'request': request, 'sites': sites, 'title': 'Sites'})


@app.get('/treatments', response_class=HTMLResponse)
def treatments_page(request: Request, db: Session = Depends(get_db)):
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment), joinedload(Treatment.practices), joinedload(Treatment.plots)).all()
    return templates.TemplateResponse('treatments.html', {'request': request, 'treatments': treatments, 'title': 'Treatments'})


@app.get('/samples', response_class=HTMLResponse)
def samples_page(request: Request, db: Session = Depends(get_db)):
    samples = db.query(SamplingEvent).options(joinedload(SamplingEvent.site), joinedload(SamplingEvent.plot).joinedload(Plot.treatment)).all()
    return templates.TemplateResponse('samples.html', {'request': request, 'samples': samples, 'title': 'Sampling Events'})


@app.get('/indicators', response_class=HTMLResponse)
def indicators_page(request: Request, db: Session = Depends(get_db)):
    indicators = db.query(Indicator).all()
    return templates.TemplateResponse('indicators.html', {'request': request, 'indicators': indicators, 'title': 'Indicators'})


@app.get('/measurements', response_class=HTMLResponse)
def measurements_page(request: Request, db: Session = Depends(get_db)):
    measurements = (
        db.query(Measurement)
        .options(joinedload(Measurement.sampling_event).joinedload(SamplingEvent.plot).joinedload(Plot.treatment), joinedload(Measurement.indicator))
        .order_by(Measurement.id.desc())
        .all()
    )
    return templates.TemplateResponse('measurements.html', {'request': request, 'measurements': measurements, 'title': 'Measurements'})


@app.get('/health')
def health_check():
    return {'status': 'ok'}
