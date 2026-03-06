from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from soil_research_platform.app.db.session import Base, engine, get_db
from soil_research_platform.app.models import Experiment, Indicator, Measurement, Plot, Practice, SamplingEvent, Site, Treatment
from soil_research_platform.app.schemas import (
    ExperimentCreate,
    ExperimentRead,
    IndicatorCreate,
    IndicatorRead,
    MeasurementCreate,
    MeasurementRead,
    PlotCreate,
    PlotRead,
    PracticeCreate,
    PracticeRead,
    SamplingEventCreate,
    SamplingEventRead,
    SiteCreate,
    SiteRead,
    TreatmentCreate,
    TreatmentRead,
)

router = APIRouter()


@router.post("/setup/create-tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created successfully."}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return {
        "experiments": db.query(Experiment).count(),
        "sites": db.query(Site).count(),
        "treatments": db.query(Treatment).count(),
        "practices": db.query(Practice).count(),
        "plots": db.query(Plot).count(),
        "sampling_events": db.query(SamplingEvent).count(),
        "indicators": db.query(Indicator).count(),
        "measurements": db.query(Measurement).count(),
    }


@router.post("/experiments", response_model=ExperimentRead)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    obj = Experiment(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)):
    return db.query(Experiment).order_by(Experiment.experiment_sk.desc()).all()


@router.post("/sites", response_model=SiteRead)
def create_site(payload: SiteCreate, db: Session = Depends(get_db)):
    if not db.get(Experiment, payload.experiment_sk):
        raise HTTPException(status_code=404, detail="Experiment not found")
    obj = Site(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/sites", response_model=list[SiteRead])
def list_sites(experiment_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Site)
    if experiment_sk is not None:
        query = query.filter(Site.experiment_sk == experiment_sk)
    return query.order_by(Site.site_sk.desc()).all()


@router.post("/treatments", response_model=TreatmentRead)
def create_treatment(payload: TreatmentCreate, db: Session = Depends(get_db)):
    if not db.get(Experiment, payload.experiment_sk):
        raise HTTPException(status_code=404, detail="Experiment not found")
    obj = Treatment(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/treatments", response_model=list[TreatmentRead])
def list_treatments(experiment_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Treatment)
    if experiment_sk is not None:
        query = query.filter(Treatment.experiment_sk == experiment_sk)
    return query.order_by(Treatment.treatment_sk.desc()).all()


@router.post("/practices", response_model=PracticeRead)
def create_practice(payload: PracticeCreate, db: Session = Depends(get_db)):
    if not db.get(Treatment, payload.treatment_sk):
        raise HTTPException(status_code=404, detail="Treatment not found")
    obj = Practice(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/practices", response_model=list[PracticeRead])
def list_practices(treatment_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Practice)
    if treatment_sk is not None:
        query = query.filter(Practice.treatment_sk == treatment_sk)
    return query.order_by(Practice.practice_sk.desc()).all()


@router.post("/plots", response_model=PlotRead)
def create_plot(payload: PlotCreate, db: Session = Depends(get_db)):
    if not db.get(Site, payload.site_sk):
        raise HTTPException(status_code=404, detail="Site not found")
    if not db.get(Treatment, payload.treatment_sk):
        raise HTTPException(status_code=404, detail="Treatment not found")
    obj = Plot(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/plots", response_model=list[PlotRead])
def list_plots(site_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Plot)
    if site_sk is not None:
        query = query.filter(Plot.site_sk == site_sk)
    return query.order_by(Plot.plot_sk.desc()).all()


@router.post("/sampling-events", response_model=SamplingEventRead)
def create_sampling_event(payload: SamplingEventCreate, db: Session = Depends(get_db)):
    if not db.get(Site, payload.site_sk):
        raise HTTPException(status_code=404, detail="Site not found")
    if payload.plot_sk is not None and not db.get(Plot, payload.plot_sk):
        raise HTTPException(status_code=404, detail="Plot not found")
    obj = SamplingEvent(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/sampling-events", response_model=list[SamplingEventRead])
def list_sampling_events(site_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(SamplingEvent)
    if site_sk is not None:
        query = query.filter(SamplingEvent.site_sk == site_sk)
    return query.order_by(SamplingEvent.sample_sk.desc()).all()


@router.post("/indicators", response_model=IndicatorRead)
def create_indicator(payload: IndicatorCreate, db: Session = Depends(get_db)):
    obj = Indicator(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/indicators", response_model=list[IndicatorRead])
def list_indicators(db: Session = Depends(get_db)):
    return db.query(Indicator).order_by(Indicator.indicator_sk.desc()).all()


@router.post("/measurements", response_model=MeasurementRead)
def create_measurement(payload: MeasurementCreate, db: Session = Depends(get_db)):
    if not db.get(SamplingEvent, payload.sample_sk):
        raise HTTPException(status_code=404, detail="Sampling event not found")
    if not db.get(Indicator, payload.indicator_sk):
        raise HTTPException(status_code=404, detail="Indicator not found")
    obj = Measurement(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/measurements", response_model=list[MeasurementRead])
def list_measurements(sample_sk: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Measurement)
    if sample_sk is not None:
        query = query.filter(Measurement.sample_sk == sample_sk)
    return query.order_by(Measurement.measurement_sk.desc()).all()
