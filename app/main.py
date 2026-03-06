from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.db import Base, engine, get_db, SessionLocal
from app.models import Experiment, Indicator, Measurement, Plot, Practice, Project, Sample, Treatment
from app.seed import seed_data

app = FastAPI(title='Soil Monitoring Platform')
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_data(db)


def redirect(url: str):
    return RedirectResponse(url=url, status_code=303)


def parse_date(value: str | None):
    if not value:
        return None
    return date.fromisoformat(value)


def parse_decimal(value: str | None):
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise HTTPException(status_code=400, detail=f'Invalid numeric value: {value}') from exc


@app.get('/', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    stats = {
        'projects': db.query(Project).count(),
        'experiments': db.query(Experiment).count(),
        'treatments': db.query(Treatment).count(),
        'plots': db.query(Plot).count(),
        'samples': db.query(Sample).count(),
        'indicators': db.query(Indicator).count(),
        'measurements': db.query(Measurement).count(),
    }
    recent_samples = db.query(Sample).options(joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Sample.plot)).order_by(Sample.id.desc()).limit(5).all()
    return templates.TemplateResponse('dashboard.html', {'request': request, 'stats': stats, 'recent_samples': recent_samples})


@app.get('/health')
def health():
    return {'status': 'ok'}


# Projects
@app.get('/projects', response_class=HTMLResponse)
def list_projects(request: Request, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Project)
    if q:
        query = query.filter(or_(Project.project_code.ilike(f'%{q}%'), Project.title.ilike(f'%{q}%')))
    projects = query.order_by(Project.project_code).all()
    return templates.TemplateResponse('projects/list.html', {'request': request, 'items': projects, 'q': q})


@app.get('/projects/new', response_class=HTMLResponse)
def new_project_form(request: Request):
    return templates.TemplateResponse('projects/form.html', {'request': request, 'item': None})


@app.post('/projects/new')
def create_project(country_code: str = Form(...), round_no: int = Form(...), approval_no: int = Form(...), project_code: str = Form(...), title: str = Form(...), description: str = Form(''), db: Session = Depends(get_db)):
    db.add(Project(country_code=country_code, round_no=round_no, approval_no=approval_no, project_code=project_code, title=title, description=description))
    db.commit()
    return redirect('/projects')


@app.get('/projects/{item_id}/edit', response_class=HTMLResponse)
def edit_project_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    return templates.TemplateResponse('projects/form.html', {'request': request, 'item': item})


@app.post('/projects/{item_id}/edit')
def update_project(item_id: int, country_code: str = Form(...), round_no: int = Form(...), approval_no: int = Form(...), project_code: str = Form(...), title: str = Form(...), description: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    item.country_code = country_code
    item.round_no = round_no
    item.approval_no = approval_no
    item.project_code = project_code
    item.title = title
    item.description = description
    db.commit()
    return redirect('/projects')


@app.post('/projects/{item_id}/delete')
def delete_project(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Project, item_id)
    db.delete(item)
    db.commit()
    return redirect('/projects')


# Experiments
@app.get('/experiments', response_class=HTMLResponse)
def list_experiments(
    request: Request,
    q: str = '',
    project_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Experiment)
        .join(Experiment.project)
        .options(joinedload(Experiment.project))
    )

    if project_id:
        query = query.filter(Experiment.project_id == project_id)

    if q:
        query = query.filter(
            or_(
                Experiment.experiment_code.ilike(f'%{q}%'),
                Experiment.title.ilike(f'%{q}%'),
                Experiment.field_name.ilike(f'%{q}%'),
                Project.project_code.ilike(f'%{q}%')
            )
        )

    items = query.order_by(
        Project.project_code,
        Experiment.experiment_code
    ).all()

    projects = db.query(Project).order_by(Project.project_code).all()

    return templates.TemplateResponse(
        'experiments/list.html',
        {
            'request': request,
            'items': items,
            'projects': projects,
            'selected_project_id': project_id,
            'q': q
        }
    )
@app.get('/experiments/new', response_class=HTMLResponse)
def new_experiment_form(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.project_code).all()
    return templates.TemplateResponse('experiments/form.html', {'request': request, 'item': None, 'projects': projects})


@app.post('/experiments/new')
def create_experiment(project_id: int = Form(...), experiment_code: str = Form(...), title: str = Form(...), field_name: str = Form(''), start_date: str = Form(''), expected_end_date: str = Form(''), db: Session = Depends(get_db)):
    db.add(Experiment(project_id=project_id, experiment_code=experiment_code, title=title, field_name=field_name, start_date=parse_date(start_date), expected_end_date=parse_date(expected_end_date)))
    db.commit()
    return redirect('/experiments')


@app.get('/experiments/{item_id}/edit', response_class=HTMLResponse)
def edit_experiment_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Experiment, item_id)
    projects = db.query(Project).order_by(Project.project_code).all()
    return templates.TemplateResponse('experiments/form.html', {'request': request, 'item': item, 'projects': projects})


@app.post('/experiments/{item_id}/edit')
def update_experiment(item_id: int, project_id: int = Form(...), experiment_code: str = Form(...), title: str = Form(...), field_name: str = Form(''), start_date: str = Form(''), expected_end_date: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Experiment, item_id)
    item.project_id = project_id
    item.experiment_code = experiment_code
    item.title = title
    item.field_name = field_name
    item.start_date = parse_date(start_date)
    item.expected_end_date = parse_date(expected_end_date)
    db.commit()
    return redirect('/experiments')


@app.post('/experiments/{item_id}/delete')
def delete_experiment(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Experiment, item_id)
    db.delete(item)
    db.commit()
    return redirect('/experiments')


# Treatments
@app.get('/treatments', response_class=HTMLResponse)
# Treatments
@app.get('/treatments', response_class=HTMLResponse)
def list_treatments(
    request: Request,
    q: str = '',
    project_id: int | None = None,
    experiment_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Treatment)
        .join(Treatment.experiment)
        .join(Experiment.project)
        .options(joinedload(Treatment.experiment).joinedload(Experiment.project))
    )

    if project_id:
        query = query.filter(Experiment.project_id == project_id)

    if experiment_id:
        query = query.filter(Treatment.experiment_id == experiment_id)

    if q:
        query = query.filter(
            or_(
                Treatment.treatment_code.ilike(f'%{q}%'),
                Treatment.name.ilike(f'%{q}%'),
                Experiment.experiment_code.ilike(f'%{q}%'),
                Project.project_code.ilike(f'%{q}%')
            )
        )

    items = query.order_by(
        Project.project_code,
        Experiment.experiment_code,
        Treatment.treatment_code
    ).all()

    projects = db.query(Project).order_by(Project.project_code).all()

    experiments = (
        db.query(Experiment)
        .join(Experiment.project)
        .options(joinedload(Experiment.project))
        .order_by(Project.project_code, Experiment.experiment_code)
        .all()
    )

    return templates.TemplateResponse(
        'treatments/list.html',
        {
            'request': request,
            'items': items,
            'projects': projects,
            'experiments': experiments,
            'selected_project_id': project_id,
            'selected_experiment_id': experiment_id,
            'q': q
        }
    )
@app.get('/treatments/new', response_class=HTMLResponse)
def new_treatment_form(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    return templates.TemplateResponse('treatments/form.html', {'request': request, 'item': None, 'experiments': experiments})


@app.post('/treatments/new')
def create_treatment(experiment_id: int = Form(...), treatment_code: str = Form(...), name: str = Form(...), treatment_type: str = Form(''), description: str = Form(''), is_control: bool = Form(False), db: Session = Depends(get_db)):
    db.add(Treatment(experiment_id=experiment_id, treatment_code=treatment_code, name=name, treatment_type=treatment_type, description=description, is_control=is_control))
    db.commit()
    return redirect('/treatments')


@app.get('/treatments/{item_id}/edit', response_class=HTMLResponse)
def edit_treatment_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Treatment, item_id)
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    return templates.TemplateResponse('treatments/form.html', {'request': request, 'item': item, 'experiments': experiments})


@app.post('/treatments/{item_id}/edit')
def update_treatment(item_id: int, experiment_id: int = Form(...), treatment_code: str = Form(...), name: str = Form(...), treatment_type: str = Form(''), description: str = Form(''), is_control: bool = Form(False), db: Session = Depends(get_db)):
    item = db.get(Treatment, item_id)
    item.experiment_id = experiment_id
    item.treatment_code = treatment_code
    item.name = name
    item.treatment_type = treatment_type
    item.description = description
    item.is_control = is_control
    db.commit()
    return redirect('/treatments')


@app.post('/treatments/{item_id}/delete')
def delete_treatment(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Treatment, item_id)
    db.delete(item)
    db.commit()
    return redirect('/treatments')


# Practices
@app.get('/practices', response_class=HTMLResponse)
def list_practices(request: Request, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Practice).options(joinedload(Practice.treatment).joinedload(Treatment.experiment).joinedload(Experiment.project))
    if q:
        query = query.join(Treatment).join(Experiment).join(Project).filter(or_(Practice.practice_name.ilike(f'%{q}%'), Practice.practice_type.ilike(f'%{q}%'), Treatment.treatment_code.ilike(f'%{q}%'), Project.project_code.ilike(f'%{q}%')))
    items = query.order_by(Practice.id.desc()).all()
    return templates.TemplateResponse('practices/list.html', {'request': request, 'items': items, 'q': q})


@app.get('/practices/new', response_class=HTMLResponse)
def new_practice_form(request: Request, db: Session = Depends(get_db)):
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    return templates.TemplateResponse('practices/form.html', {'request': request, 'item': None, 'treatments': treatments})


@app.post('/practices/new')
def create_practice(treatment_id: int = Form(...), practice_type: str = Form(...), practice_name: str = Form(...), practice_value: str = Form(''), unit: str = Form(''), description: str = Form(''), db: Session = Depends(get_db)):
    db.add(Practice(treatment_id=treatment_id, practice_type=practice_type, practice_name=practice_name, practice_value=practice_value, unit=unit, description=description))
    db.commit()
    return redirect('/practices')


@app.get('/practices/{item_id}/edit', response_class=HTMLResponse)
def edit_practice_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Practice, item_id)
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    return templates.TemplateResponse('practices/form.html', {'request': request, 'item': item, 'treatments': treatments})


@app.post('/practices/{item_id}/edit')
def update_practice(item_id: int, treatment_id: int = Form(...), practice_type: str = Form(...), practice_name: str = Form(...), practice_value: str = Form(''), unit: str = Form(''), description: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Practice, item_id)
    item.treatment_id = treatment_id
    item.practice_type = practice_type
    item.practice_name = practice_name
    item.practice_value = practice_value
    item.unit = unit
    item.description = description
    db.commit()
    return redirect('/practices')


@app.post('/practices/{item_id}/delete')
def delete_practice(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Practice, item_id)
    db.delete(item)
    db.commit()
    return redirect('/practices')


# Plots
@app.get('/plots', response_class=HTMLResponse)
def list_plots(request: Request, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Plot).options(joinedload(Plot.experiment).joinedload(Experiment.project), joinedload(Plot.treatment))
    if q:
        query = query.join(Experiment).join(Project).outerjoin(Treatment).filter(or_(Plot.plot_code.ilike(f'%{q}%'), Experiment.experiment_code.ilike(f'%{q}%'), Project.project_code.ilike(f'%{q}%'), Treatment.treatment_code.ilike(f'%{q}%')))
    items = query.order_by(Plot.id.desc()).all()
    return templates.TemplateResponse('plots/list.html', {'request': request, 'items': items, 'q': q})


@app.get('/plots/new', response_class=HTMLResponse)
def new_plot_form(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    return templates.TemplateResponse('plots/form.html', {'request': request, 'item': None, 'experiments': experiments, 'treatments': treatments})


@app.post('/plots/new')
def create_plot(experiment_id: int = Form(...), treatment_id: int | None = Form(None), plot_code: str = Form(...), replicate_no: int | None = Form(None), block_no: int | None = Form(None), sample_point: str = Form(''), db: Session = Depends(get_db)):
    db.add(Plot(experiment_id=experiment_id, treatment_id=treatment_id, plot_code=plot_code, replicate_no=replicate_no, block_no=block_no, sample_point=sample_point))
    db.commit()
    return redirect('/plots')


@app.get('/plots/{item_id}/edit', response_class=HTMLResponse)
def edit_plot_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Plot, item_id)
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    return templates.TemplateResponse('plots/form.html', {'request': request, 'item': item, 'experiments': experiments, 'treatments': treatments})


@app.post('/plots/{item_id}/edit')
def update_plot(item_id: int, experiment_id: int = Form(...), treatment_id: int | None = Form(None), plot_code: str = Form(...), replicate_no: int | None = Form(None), block_no: int | None = Form(None), sample_point: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Plot, item_id)
    item.experiment_id = experiment_id
    item.treatment_id = treatment_id
    item.plot_code = plot_code
    item.replicate_no = replicate_no
    item.block_no = block_no
    item.sample_point = sample_point
    db.commit()
    return redirect('/plots')


@app.post('/plots/{item_id}/delete')
def delete_plot(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Plot, item_id)
    db.delete(item)
    db.commit()
    return redirect('/plots')


# Indicators
@app.get('/indicators', response_class=HTMLResponse)
def list_indicators(request: Request, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Indicator)
    if q:
        query = query.filter(or_(Indicator.indicator_code.ilike(f'%{q}%'), Indicator.indicator_name.ilike(f'%{q}%'), Indicator.category.ilike(f'%{q}%')))
    items = query.order_by(Indicator.indicator_code).all()
    return templates.TemplateResponse('indicators/list.html', {'request': request, 'items': items, 'q': q})


@app.get('/indicators/new', response_class=HTMLResponse)
def new_indicator_form(request: Request):
    return templates.TemplateResponse('indicators/form.html', {'request': request, 'item': None})


@app.post('/indicators/new')
def create_indicator(indicator_code: str = Form(...), indicator_name: str = Form(...), default_unit: str = Form(''), value_type: str = Form(...), category: str = Form(''), description: str = Form(''), db: Session = Depends(get_db)):
    db.add(Indicator(indicator_code=indicator_code, indicator_name=indicator_name, default_unit=default_unit, value_type=value_type, category=category, description=description))
    db.commit()
    return redirect('/indicators')


@app.get('/indicators/{item_id}/edit', response_class=HTMLResponse)
def edit_indicator_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Indicator, item_id)
    return templates.TemplateResponse('indicators/form.html', {'request': request, 'item': item})


@app.post('/indicators/{item_id}/edit')
def update_indicator(item_id: int, indicator_code: str = Form(...), indicator_name: str = Form(...), default_unit: str = Form(''), value_type: str = Form(...), category: str = Form(''), description: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Indicator, item_id)
    item.indicator_code = indicator_code
    item.indicator_name = indicator_name
    item.default_unit = default_unit
    item.value_type = value_type
    item.category = category
    item.description = description
    db.commit()
    return redirect('/indicators')


@app.post('/indicators/{item_id}/delete')
def delete_indicator(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Indicator, item_id)
    db.delete(item)
    db.commit()
    return redirect('/indicators')


# Samples
@app.get('/samples', response_class=HTMLResponse)
def list_samples(request: Request, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Sample).options(joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Sample.plot))
    if q:
        query = query.join(Experiment).join(Project).outerjoin(Plot).filter(or_(Sample.sample_id.ilike(f'%{q}%'), Sample.layer_id.ilike(f'%{q}%'), Project.project_code.ilike(f'%{q}%'), Experiment.experiment_code.ilike(f'%{q}%'), Plot.plot_code.ilike(f'%{q}%')))
    items = query.order_by(Sample.id.desc()).all()
    return templates.TemplateResponse('samples/list.html', {'request': request, 'items': items, 'q': q})


@app.get('/samples/new', response_class=HTMLResponse)
def new_sample_form(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    plots = db.query(Plot).options(joinedload(Plot.experiment).joinedload(Experiment.project)).order_by(Plot.plot_code).all()
    return templates.TemplateResponse('samples/form.html', {'request': request, 'item': None, 'experiments': experiments, 'plots': plots})


@app.post('/samples/new')
def create_sample(experiment_id: int = Form(...), plot_id: int | None = Form(None), sample_id: str = Form(...), layer_id: str = Form(''), sampling_date: str = Form(''), author: str = Form(''), db: Session = Depends(get_db)):
    db.add(Sample(experiment_id=experiment_id, plot_id=plot_id, sample_id=sample_id, layer_id=layer_id, sampling_date=parse_date(sampling_date), author=author))
    db.commit()
    return redirect('/samples')


@app.get('/samples/{item_id}/edit', response_class=HTMLResponse)
def edit_sample_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Sample, item_id)
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    plots = db.query(Plot).options(joinedload(Plot.experiment).joinedload(Experiment.project)).order_by(Plot.plot_code).all()
    return templates.TemplateResponse('samples/form.html', {'request': request, 'item': item, 'experiments': experiments, 'plots': plots})


@app.post('/samples/{item_id}/edit')
def update_sample(item_id: int, experiment_id: int = Form(...), plot_id: int | None = Form(None), sample_id: str = Form(...), layer_id: str = Form(''), sampling_date: str = Form(''), author: str = Form(''), db: Session = Depends(get_db)):
    item = db.get(Sample, item_id)
    item.experiment_id = experiment_id
    item.plot_id = plot_id
    item.sample_id = sample_id
    item.layer_id = layer_id
    item.sampling_date = parse_date(sampling_date)
    item.author = author
    db.commit()
    return redirect('/samples')


@app.post('/samples/{item_id}/delete')
def delete_sample(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Sample, item_id)
    db.delete(item)
    db.commit()
    return redirect('/samples')


# Measurements
@app.get('/measurements', response_class=HTMLResponse)
def list_measurements(request: Request, q: str = '', project_id: int | None = None, experiment_id: int | None = None, treatment_id: int | None = None, indicator_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Measurement).options(joinedload(Measurement.sample).joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Measurement.sample).joinedload(Sample.plot).joinedload(Plot.treatment), joinedload(Measurement.indicator))
    if project_id:
        query = query.join(Sample).join(Experiment).filter(Experiment.project_id == project_id)
    if experiment_id:
        query = query.join(Sample, Measurement.sample).filter(Sample.experiment_id == experiment_id)
    if treatment_id:
        query = query.join(Sample, Measurement.sample).join(Plot, Sample.plot).filter(Plot.treatment_id == treatment_id)
    if indicator_id:
        query = query.filter(Measurement.indicator_id == indicator_id)
    if q:
        query = query.join(Indicator).join(Sample, Measurement.sample).join(Experiment).join(Project).outerjoin(Plot).filter(or_(Project.project_code.ilike(f'%{q}%'), Experiment.experiment_code.ilike(f'%{q}%'), Sample.sample_id.ilike(f'%{q}%'), Plot.plot_code.ilike(f'%{q}%'), Indicator.indicator_name.ilike(f'%{q}%')))
    items = query.order_by(Measurement.id.desc()).all()
    projects = db.query(Project).order_by(Project.project_code).all()
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    indicators = db.query(Indicator).order_by(Indicator.indicator_code).all()
    return templates.TemplateResponse('measurements/list.html', {'request': request, 'items': items, 'projects': projects, 'experiments': experiments, 'treatments': treatments, 'indicators': indicators, 'selected_project_id': project_id, 'selected_experiment_id': experiment_id, 'selected_treatment_id': treatment_id, 'selected_indicator_id': indicator_id, 'q': q})


@app.get('/measurements/new', response_class=HTMLResponse)
def new_measurement_form(request: Request, db: Session = Depends(get_db)):
    samples = db.query(Sample).options(joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Sample.plot)).order_by(Sample.sample_id).all()
    indicators = db.query(Indicator).order_by(Indicator.indicator_code).all()
    return templates.TemplateResponse('measurements/form.html', {'request': request, 'item': None, 'samples': samples, 'indicators': indicators})


@app.post('/measurements/new')
def create_measurement(sample_id_fk: int = Form(...), indicator_id: int = Form(...), measured_value_num: str = Form(''), measured_value_text: str = Form(''), unit: str = Form(''), qa_status: str = Form('raw'), db: Session = Depends(get_db)):
    db.add(Measurement(sample_id_fk=sample_id_fk, indicator_id=indicator_id, measured_value_num=parse_decimal(measured_value_num), measured_value_text=measured_value_text or None, unit=unit, qa_status=qa_status))
    db.commit()
    return redirect('/measurements')


@app.get('/measurements/{item_id}/edit', response_class=HTMLResponse)
def edit_measurement_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Measurement, item_id)
    samples = db.query(Sample).options(joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Sample.plot)).order_by(Sample.sample_id).all()
    indicators = db.query(Indicator).order_by(Indicator.indicator_code).all()
    return templates.TemplateResponse('measurements/form.html', {'request': request, 'item': item, 'samples': samples, 'indicators': indicators})


@app.post('/measurements/{item_id}/edit')
def update_measurement(item_id: int, sample_id_fk: int = Form(...), indicator_id: int = Form(...), measured_value_num: str = Form(''), measured_value_text: str = Form(''), unit: str = Form(''), qa_status: str = Form('raw'), db: Session = Depends(get_db)):
    item = db.get(Measurement, item_id)
    item.sample_id_fk = sample_id_fk
    item.indicator_id = indicator_id
    item.measured_value_num = parse_decimal(measured_value_num)
    item.measured_value_text = measured_value_text or None
    item.unit = unit
    item.qa_status = qa_status
    db.commit()
    return redirect('/measurements')


@app.post('/measurements/{item_id}/delete')
def delete_measurement(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Measurement, item_id)
    db.delete(item)
    db.commit()
    return redirect('/measurements')


@app.get('/query', response_class=HTMLResponse)
def query_center(request: Request, project_id: int | None = None, experiment_id: int | None = None, treatment_id: int | None = None, indicator_id: int | None = None, q: str = '', db: Session = Depends(get_db)):
    query = db.query(Measurement).options(joinedload(Measurement.sample).joinedload(Sample.experiment).joinedload(Experiment.project), joinedload(Measurement.sample).joinedload(Sample.plot).joinedload(Plot.treatment), joinedload(Measurement.indicator))
    if project_id:
        query = query.join(Sample).join(Experiment).filter(Experiment.project_id == project_id)
    if experiment_id:
        query = query.join(Sample, Measurement.sample).filter(Sample.experiment_id == experiment_id)
    if treatment_id:
        query = query.join(Sample, Measurement.sample).join(Plot, Sample.plot).filter(Plot.treatment_id == treatment_id)
    if indicator_id:
        query = query.filter(Measurement.indicator_id == indicator_id)
    if q:
        query = query.join(Indicator).join(Sample, Measurement.sample).join(Experiment).join(Project).outerjoin(Plot).filter(or_(q == '' , Project.project_code.ilike(f'%{q}%'), Experiment.experiment_code.ilike(f'%{q}%'), Sample.sample_id.ilike(f'%{q}%'), Plot.plot_code.ilike(f'%{q}%'), Indicator.indicator_name.ilike(f'%{q}%')))
    rows = query.order_by(Measurement.id.desc()).limit(200).all()
    projects = db.query(Project).order_by(Project.project_code).all()
    experiments = db.query(Experiment).options(joinedload(Experiment.project)).order_by(Experiment.experiment_code).all()
    treatments = db.query(Treatment).options(joinedload(Treatment.experiment).joinedload(Experiment.project)).order_by(Treatment.treatment_code).all()
    indicators = db.query(Indicator).order_by(Indicator.indicator_code).all()
    return templates.TemplateResponse('query.html', {'request': request, 'rows': rows, 'projects': projects, 'experiments': experiments, 'treatments': treatments, 'indicators': indicators, 'selected_project_id': project_id, 'selected_experiment_id': experiment_id, 'selected_treatment_id': treatment_id, 'selected_indicator_id': indicator_id, 'q': q})
