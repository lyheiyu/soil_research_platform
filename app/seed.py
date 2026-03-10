# from datetime import date
#
# from sqlalchemy.orm import Session
#
# from app.models import Experiment, Indicator, Measurement, Plot, Practice, Project, Sample, Treatment
#
#
# def seed_data(db: Session):
#     if db.query(Project).first():
#         return
#
#     p1 = Project(country_code='NL', round_no=1, approval_no=1, project_code='NL-RR1-APP1', title='Netherlands Round 1 Approved Project 1', description='Demo project for Netherlands')
#     p2 = Project(country_code='IE', round_no=1, approval_no=1, project_code='IE-RR1-APP1', title='Ireland Round 1 Approved Project 1', description='Demo project for Ireland')
#     db.add_all([p1, p2])
#     db.flush()
#
#     e1 = Experiment(project_id=p1.id, experiment_code='EXP-001', title='Carbon and pH baseline', field_name='Field Alpha', start_date=date(2026, 1, 12), expected_end_date=date(2026, 7, 1))
#     e2 = Experiment(project_id=p1.id, experiment_code='EXP-002', title='Compost response trial', field_name='Field Beta', start_date=date(2026, 2, 1), expected_end_date=date(2026, 8, 1))
#     e3 = Experiment(project_id=p2.id, experiment_code='EXP-001', title='Irish replicated treatment trial', field_name='Field Gamma', start_date=date(2026, 1, 20), expected_end_date=date(2026, 9, 1))
#     db.add_all([e1, e2, e3])
#     db.flush()
#
#     t1 = Treatment(experiment_id=e1.id, treatment_code='C', name='Control', treatment_type='control', is_control=True)
#     t2 = Treatment(experiment_id=e1.id, treatment_code='T1', name='Reduced tillage', treatment_type='soil_management')
#     t3 = Treatment(experiment_id=e2.id, treatment_code='T2', name='Compost addition', treatment_type='amendment')
#     t4 = Treatment(experiment_id=e3.id, treatment_code='C', name='Control', treatment_type='control', is_control=True)
#     t5 = Treatment(experiment_id=e3.id, treatment_code='T1', name='Cover crop', treatment_type='crop_management')
#     db.add_all([t1, t2, t3, t4, t5])
#     db.flush()
#
#     db.add_all([
#         Practice(treatment_id=t2.id, practice_type='tillage', practice_name='Reduced tillage', practice_value='reduced', unit='', description='Reduced tillage practice'),
#         Practice(treatment_id=t3.id, practice_type='compost', practice_name='Compost application', practice_value='5', unit='t/ha', description='Organic compost applied'),
#         Practice(treatment_id=t5.id, practice_type='cover_crop', practice_name='Winter cover crop', practice_value='ryegrass', unit='', description='Cover crop seeded in autumn'),
#     ])
#
#     pl1 = Plot(experiment_id=e1.id, treatment_id=t1.id, plot_code='C-1', replicate_no=1, block_no=1, sample_point='SP1')
#     pl2 = Plot(experiment_id=e1.id, treatment_id=t2.id, plot_code='T1-1', replicate_no=1, block_no=1, sample_point='SP1')
#     pl3 = Plot(experiment_id=e2.id, treatment_id=t3.id, plot_code='T2-1', replicate_no=1, block_no=1, sample_point='SP1')
#     pl4 = Plot(experiment_id=e3.id, treatment_id=t4.id, plot_code='C-1', replicate_no=1, block_no=1, sample_point='SP1')
#     pl5 = Plot(experiment_id=e3.id, treatment_id=t5.id, plot_code='T1-1', replicate_no=1, block_no=1, sample_point='SP1')
#     db.add_all([pl1, pl2, pl3, pl4, pl5])
#     db.flush()
#
#     i1 = Indicator(indicator_code='SOIL_TEXTURE', indicator_name='Soil texture', default_unit='% sand, silt, clay', value_type='text', category='physical')
#     i2 = Indicator(indicator_code='SOIL_TEMP', indicator_name='Soil temperature', default_unit='°C', value_type='numeric', category='physical')
#     i3 = Indicator(indicator_code='SOIL_MOISTURE', indicator_name='Soil moisture', default_unit='VWC or %', value_type='numeric', category='physical')
#     i4 = Indicator(indicator_code='CRUST_FORM', indicator_name='Crust formation', default_unit='mm / psi', value_type='numeric', category='physical')
#     i5 = Indicator(indicator_code='VISUAL_ASSESS', indicator_name='Visual assessment', default_unit='n/a', value_type='text', category='mixed')
#     db.add_all([i1, i2, i3, i4, i5])
#     db.flush()
#
#     s1 = Sample(experiment_id=e2.id, plot_id=pl3.id, sample_id='NL-EXP2-T2-1-0-30-20260203', layer_id='0-30', sampling_date=date(2026, 2, 3), author='Field Team NL')
#     s2 = Sample(experiment_id=e1.id, plot_id=pl2.id, sample_id='NL-EXP1-T1-1-0-30-20260210', layer_id='0-30', sampling_date=date(2026, 2, 10), author='Field Team NL')
#     db.add_all([s1, s2])
#     db.flush()
#
#     db.add_all([
#         Measurement(sample_id_fk=s1.id, indicator_id=i1.id, measured_value_text='sandy loam', unit=i1.default_unit, qa_status='validated'),
#         Measurement(sample_id_fk=s1.id, indicator_id=i2.id, measured_value_num=12.7, unit=i2.default_unit, qa_status='validated'),
#         Measurement(sample_id_fk=s1.id, indicator_id=i3.id, measured_value_num=28.5, unit='%', qa_status='raw'),
#         Measurement(sample_id_fk=s1.id, indicator_id=i4.id, measured_value_num=3.2, unit='mm', qa_status='raw'),
#         Measurement(sample_id_fk=s1.id, indicator_id=i5.id, measured_value_text='Good physical structure', unit='n/a', qa_status='raw'),
#         Measurement(sample_id_fk=s2.id, indicator_id=i2.id, measured_value_num=10.4, unit=i2.default_unit, qa_status='validated'),
#     ])
#
#     db.commit()
from datetime import date

from sqlalchemy.orm import Session

from app.models import Experiment, Indicator, Measurement, Plot, Practice, Project, Sample, Treatment


def seed_data(db: Session):
    if db.query(Project).first():
        return

    p1 = Project(
        country_code='NL',
        round_no=1,
        approval_no=1,
        project_code='NL-RR1-APP1',
        title='Netherlands Round 1 Approved Project 1',
        description='Demo project for Netherlands'
    )
    p2 = Project(
        country_code='IE',
        round_no=1,
        approval_no=1,
        project_code='IE-RR1-APP1',
        title='Ireland Round 1 Approved Project 1',
        description='Demo project for Ireland'
    )
    db.add_all([p1, p2])
    db.flush()

    e1 = Experiment(
        project_id=p1.id,
        experiment_code='EXP-001',
        title='Carbon and pH baseline',
        field_name='Field Alpha',
        start_date=date(2026, 1, 12),
        expected_end_date=date(2026, 7, 1)
    )
    e2 = Experiment(
        project_id=p1.id,
        experiment_code='EXP-002',
        title='Compost response trial',
        field_name='Field Beta',
        start_date=date(2026, 2, 1),
        expected_end_date=date(2026, 8, 1)
    )
    e3 = Experiment(
        project_id=p2.id,
        experiment_code='EXP-001',
        title='Irish replicated treatment trial',
        field_name='Field Gamma',
        start_date=date(2026, 1, 20),
        expected_end_date=date(2026, 9, 1)
    )
    db.add_all([e1, e2, e3])
    db.flush()

    t1 = Treatment(
        experiment_id=e1.id,
        treatment_code='C',
        name='Control',
        treatment_type='control',
        is_control=True
    )
    t2 = Treatment(
        experiment_id=e1.id,
        treatment_code='T1',
        name='Reduced tillage',
        treatment_type='soil_management'
    )
    t3 = Treatment(
        experiment_id=e2.id,
        treatment_code='T2',
        name='Compost addition',
        treatment_type='amendment'
    )
    t4 = Treatment(
        experiment_id=e3.id,
        treatment_code='C',
        name='Control',
        treatment_type='control',
        is_control=True
    )
    t5 = Treatment(
        experiment_id=e3.id,
        treatment_code='T1',
        name='Cover crop',
        treatment_type='crop_management'
    )
    db.add_all([t1, t2, t3, t4, t5])
    db.flush()

    db.add_all([
        Practice(
            treatment_id=t2.id,
            practice_type='tillage',
            practice_name='Reduced tillage',
            practice_value='reduced',
            unit='',
            description='Reduced tillage practice'
        ),
        Practice(
            treatment_id=t3.id,
            practice_type='compost',
            practice_name='Compost application',
            practice_value='5',
            unit='t/ha',
            description='Organic compost applied'
        ),
        Practice(
            treatment_id=t5.id,
            practice_type='cover_crop',
            practice_name='Winter cover crop',
            practice_value='ryegrass',
            unit='',
            description='Cover crop seeded in autumn'
        ),
    ])

    pl1 = Plot(
        experiment_id=e1.id,
        treatment_id=t1.id,
        plot_code='C-1',
        replicate_no=1,
        sample_point='SP1',
        gps_lat=52.5201,
        gps_lon=5.7501
    )
    pl2 = Plot(
        experiment_id=e1.id,
        treatment_id=t2.id,
        plot_code='T1-1',
        replicate_no=1,
        sample_point='SP1',
        gps_lat=52.5202,
        gps_lon=5.7502
    )
    pl3 = Plot(
        experiment_id=e2.id,
        treatment_id=t3.id,
        plot_code='T2-1',
        replicate_no=1,
        sample_point='SP1',
        gps_lat=52.6201,
        gps_lon=5.8501
    )
    pl4 = Plot(
        experiment_id=e3.id,
        treatment_id=t4.id,
        plot_code='C-1',
        replicate_no=1,
        sample_point='SP1',
        gps_lat=53.4201,
        gps_lon=-7.9401
    )
    pl5 = Plot(
        experiment_id=e3.id,
        treatment_id=t5.id,
        plot_code='T1-1',
        replicate_no=1,
        sample_point='SP1',
        gps_lat=53.4202,
        gps_lon=-7.9402
    )
    db.add_all([pl1, pl2, pl3, pl4, pl5])
    db.flush()

    i1 = Indicator(
        indicator_code='SOIL_TEXTURE',
        indicator_name='Soil texture',
        default_unit='% sand, silt, clay',
        value_type='text',
        category='physical'
    )
    i2 = Indicator(
        indicator_code='SOIL_TEMP',
        indicator_name='Soil temperature',
        default_unit='°C',
        value_type='numeric',
        category='physical'
    )
    i3 = Indicator(
        indicator_code='SOIL_MOISTURE',
        indicator_name='Soil moisture',
        default_unit='VWC or %',
        value_type='numeric',
        category='physical'
    )
    i4 = Indicator(
        indicator_code='CRUST_FORM',
        indicator_name='Crust formation',
        default_unit='mm / psi',
        value_type='numeric',
        category='physical'
    )
    i5 = Indicator(
        indicator_code='VISUAL_ASSESS',
        indicator_name='Visual assessment',
        default_unit='n/a',
        value_type='text',
        category='mixed'
    )
    db.add_all([i1, i2, i3, i4, i5])
    db.flush()

    s1 = Sample(
        experiment_id=e2.id,
        plot_id=pl3.id,
        sample_id='NL-EXP2-T2-1-0-30-20260203',
        sampling_timepoint='T0',
        layer_id='0-30',
        depth_from_cm=0,
        depth_to_cm=30,
        sampling_date=date(2026, 2, 3),
        author='Field Team NL',
        clouds='partly_clouded',
        temperature_band='10-20',
        rainfall_condition='rain in last week'
    )
    s2 = Sample(
        experiment_id=e1.id,
        plot_id=pl2.id,
        sample_id='NL-EXP1-T1-1-0-30-20260210',
        sampling_timepoint='T1',
        layer_id='0-30',
        depth_from_cm=0,
        depth_to_cm=30,
        sampling_date=date(2026, 2, 10),
        author='Field Team NL',
        clouds='sunny',
        temperature_band='10-20',
        rainfall_condition='no rain'
    )
    db.add_all([s1, s2])
    db.flush()

    db.add_all([
        Measurement(
            sample_id_fk=s1.id,
            indicator_id=i1.id,
            measured_value_text='sandy loam',
            unit=i1.default_unit,
            qa_status='validated'
        ),
        Measurement(
            sample_id_fk=s1.id,
            indicator_id=i2.id,
            measured_value_num=12.7,
            unit=i2.default_unit,
            qa_status='validated'
        ),
        Measurement(
            sample_id_fk=s1.id,
            indicator_id=i3.id,
            measured_value_num=28.5,
            unit='%',
            qa_status='raw'
        ),
        Measurement(
            sample_id_fk=s1.id,
            indicator_id=i4.id,
            measured_value_num=3.2,
            unit='mm',
            qa_status='raw'
        ),
        Measurement(
            sample_id_fk=s1.id,
            indicator_id=i5.id,
            measured_value_text='Good physical structure',
            unit='n/a',
            qa_status='raw'
        ),
        Measurement(
            sample_id_fk=s2.id,
            indicator_id=i2.id,
            measured_value_num=10.4,
            unit=i2.default_unit,
            qa_status='validated'
        ),
    ])

    db.commit()