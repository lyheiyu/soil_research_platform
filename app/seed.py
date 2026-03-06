from datetime import date
from sqlalchemy.orm import Session

from .models import Experiment, Indicator, Measurement, Plot, Practice, SamplingEvent, Site, Treatment


def seed_demo_data(db: Session) -> None:
    if db.query(Experiment).first():
        return

    exp = Experiment(
        project_id='SOILCRATES-WP4',
        experiment_code='EXP-001',
        title='Soil Health Trial 2026',
        start_date=date(2026, 1, 12),
        expected_end_date=date(2026, 12, 31),
    )
    db.add(exp)
    db.flush()

    site = Site(
        experiment_id=exp.id,
        site_code='SITE-ATH-01',
        field_identifier='Athlone Field A',
        gps_lat=53.4239,
        gps_lon=-7.9407,
        soil_type_texture='Loam',
        field_size_ha=4.8,
    )
    db.add(site)
    db.flush()

    control = Treatment(
        experiment_id=exp.id,
        treatment_code='C',
        treatment_name='Control Plot',
        treatment_type='Control',
        description='Baseline management without intervention',
        is_control=True,
    )
    t1 = Treatment(
        experiment_id=exp.id,
        treatment_code='T1',
        treatment_name='Reduced Tillage',
        treatment_type='Soil Management',
        description='Reduced tillage treatment for comparison',
        is_control=False,
    )
    t2 = Treatment(
        experiment_id=exp.id,
        treatment_code='T2',
        treatment_name='Compost Addition',
        treatment_type='Organic Amendment',
        description='Compost added before planting',
        is_control=False,
    )
    db.add_all([control, t1, t2])
    db.flush()

    db.add_all([
        Practice(treatment_id=control.id, practice_type='Management', practice_name='Standard practice', practice_value='baseline', description='No additional treatment'),
        Practice(treatment_id=t1.id, practice_type='Tillage', practice_name='Reduced tillage', practice_value='shallow', unit='cm', description='Reduced soil disturbance'),
        Practice(treatment_id=t2.id, practice_type='Amendment', practice_name='Compost application', practice_value='5', unit='t/ha', description='Organic compost addition'),
    ])

    plots = [
        Plot(site_id=site.id, treatment_id=control.id, plot_code='P1', replicate_no=1, block_no=1, sample_point_id='SP-C-01'),
        Plot(site_id=site.id, treatment_id=control.id, plot_code='P2', replicate_no=2, block_no=1, sample_point_id='SP-C-02'),
        Plot(site_id=site.id, treatment_id=t1.id, plot_code='P3', replicate_no=1, block_no=1, sample_point_id='SP-T1-01'),
        Plot(site_id=site.id, treatment_id=t1.id, plot_code='P4', replicate_no=2, block_no=1, sample_point_id='SP-T1-02'),
        Plot(site_id=site.id, treatment_id=t2.id, plot_code='P5', replicate_no=1, block_no=1, sample_point_id='SP-T2-01'),
        Plot(site_id=site.id, treatment_id=t2.id, plot_code='P6', replicate_no=2, block_no=1, sample_point_id='SP-T2-02'),
    ]
    db.add_all(plots)
    db.flush()

    indicators = [
        Indicator(indicator_code='PH', indicator_name='Soil pH', category='Chemical', default_unit='pH', value_type='numeric'),
        Indicator(indicator_code='SOC', indicator_name='Soil Organic Carbon', category='Chemical', default_unit='g/kg', value_type='numeric'),
        Indicator(indicator_code='TN', indicator_name='Total Nitrogen', category='Chemical', default_unit='g/kg', value_type='numeric'),
        Indicator(indicator_code='BD', indicator_name='Bulk Density', category='Physical', default_unit='g/cm3', value_type='numeric'),
    ]
    db.add_all(indicators)
    db.flush()

    samples = [
        SamplingEvent(site_id=site.id, plot_id=plots[0].id, sample_id='S-ATH-001', layer_id='0-10 cm', sampling_date=date(2026, 2, 14), sampling_timepoint='T0', author='Field Team A'),
        SamplingEvent(site_id=site.id, plot_id=plots[2].id, sample_id='S-ATH-002', layer_id='0-10 cm', sampling_date=date(2026, 2, 14), sampling_timepoint='T0', author='Field Team A'),
        SamplingEvent(site_id=site.id, plot_id=plots[4].id, sample_id='S-ATH-003', layer_id='0-10 cm', sampling_date=date(2026, 2, 14), sampling_timepoint='T0', author='Field Team A'),
    ]
    db.add_all(samples)
    db.flush()

    ind_map = {i.indicator_code: i.id for i in indicators}
    db.add_all([
        Measurement(sampling_event_id=samples[0].id, indicator_id=ind_map['PH'], result_domain='scientific', measured_value_num=6.40, unit='pH', qa_status='checked'),
        Measurement(sampling_event_id=samples[0].id, indicator_id=ind_map['SOC'], result_domain='scientific', measured_value_num=21.8, unit='g/kg', qa_status='checked'),
        Measurement(sampling_event_id=samples[1].id, indicator_id=ind_map['PH'], result_domain='scientific', measured_value_num=6.55, unit='pH', qa_status='checked'),
        Measurement(sampling_event_id=samples[1].id, indicator_id=ind_map['SOC'], result_domain='scientific', measured_value_num=24.1, unit='g/kg', qa_status='checked'),
        Measurement(sampling_event_id=samples[2].id, indicator_id=ind_map['PH'], result_domain='scientific', measured_value_num=6.72, unit='pH', qa_status='checked'),
        Measurement(sampling_event_id=samples[2].id, indicator_id=ind_map['SOC'], result_domain='scientific', measured_value_num=26.4, unit='g/kg', qa_status='checked'),
        Measurement(sampling_event_id=samples[2].id, indicator_id=ind_map['TN'], result_domain='scientific', measured_value_num=1.91, unit='g/kg', qa_status='checked'),
        Measurement(sampling_event_id=samples[1].id, indicator_id=ind_map['BD'], result_domain='field', measured_value_num=1.28, unit='g/cm3', qa_status='raw'),
    ])

    db.commit()
