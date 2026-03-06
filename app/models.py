from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Experiment(Base):
    __tablename__ = 'experiments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(100), nullable=False)
    experiment_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    expected_end_date: Mapped[date | None] = mapped_column(Date)

    sites: Mapped[list['Site']] = relationship('Site', back_populates='experiment', cascade='all, delete-orphan')
    treatments: Mapped[list['Treatment']] = relationship('Treatment', back_populates='experiment', cascade='all, delete-orphan')


class Site(Base):
    __tablename__ = 'sites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey('experiments.id'), nullable=False)
    site_code: Mapped[str] = mapped_column(String(100), nullable=False)
    field_identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    gps_lat: Mapped[float | None] = mapped_column(Float)
    gps_lon: Mapped[float | None] = mapped_column(Float)
    soil_type_texture: Mapped[str | None] = mapped_column(String(100))
    field_size_ha: Mapped[float | None] = mapped_column(Float)

    experiment: Mapped['Experiment'] = relationship('Experiment', back_populates='sites')
    plots: Mapped[list['Plot']] = relationship('Plot', back_populates='site', cascade='all, delete-orphan')
    sampling_events: Mapped[list['SamplingEvent']] = relationship('SamplingEvent', back_populates='site', cascade='all, delete-orphan')


class Treatment(Base):
    __tablename__ = 'treatments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey('experiments.id'), nullable=False)
    treatment_code: Mapped[str] = mapped_column(String(50), nullable=False)
    treatment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    treatment_type: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    is_control: Mapped[bool] = mapped_column(Boolean, default=False)

    experiment: Mapped['Experiment'] = relationship('Experiment', back_populates='treatments')
    practices: Mapped[list['Practice']] = relationship('Practice', back_populates='treatment', cascade='all, delete-orphan')
    plots: Mapped[list['Plot']] = relationship('Plot', back_populates='treatment', cascade='all, delete-orphan')


class Practice(Base):
    __tablename__ = 'practices'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    treatment_id: Mapped[int] = mapped_column(ForeignKey('treatments.id'), nullable=False)
    practice_type: Mapped[str] = mapped_column(String(100), nullable=False)
    practice_name: Mapped[str] = mapped_column(String(255), nullable=False)
    practice_value: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)

    treatment: Mapped['Treatment'] = relationship('Treatment', back_populates='practices')


class Plot(Base):
    __tablename__ = 'plots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    site_id: Mapped[int] = mapped_column(ForeignKey('sites.id'), nullable=False)
    treatment_id: Mapped[int] = mapped_column(ForeignKey('treatments.id'), nullable=False)
    plot_code: Mapped[str] = mapped_column(String(100), nullable=False)
    replicate_no: Mapped[int | None] = mapped_column(Integer)
    block_no: Mapped[int | None] = mapped_column(Integer)
    sample_point_id: Mapped[str | None] = mapped_column(String(100))

    site: Mapped['Site'] = relationship('Site', back_populates='plots')
    treatment: Mapped['Treatment'] = relationship('Treatment', back_populates='plots')
    sampling_events: Mapped[list['SamplingEvent']] = relationship('SamplingEvent', back_populates='plot')


class SamplingEvent(Base):
    __tablename__ = 'sampling_events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    site_id: Mapped[int] = mapped_column(ForeignKey('sites.id'), nullable=False)
    plot_id: Mapped[int | None] = mapped_column(ForeignKey('plots.id'))
    sample_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    layer_id: Mapped[str | None] = mapped_column(String(100))
    sampling_date: Mapped[date | None] = mapped_column(Date)
    sampling_timepoint: Mapped[str | None] = mapped_column(String(100))
    author: Mapped[str | None] = mapped_column(String(100))

    site: Mapped['Site'] = relationship('Site', back_populates='sampling_events')
    plot: Mapped['Plot'] = relationship('Plot', back_populates='sampling_events')
    measurements: Mapped[list['Measurement']] = relationship('Measurement', back_populates='sampling_event', cascade='all, delete-orphan')


class Indicator(Base):
    __tablename__ = 'indicators'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    indicator_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    indicator_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    default_unit: Mapped[str | None] = mapped_column(String(50))
    value_type: Mapped[str] = mapped_column(String(50), nullable=False)

    measurements: Mapped[list['Measurement']] = relationship('Measurement', back_populates='indicator')


class Measurement(Base):
    __tablename__ = 'measurements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sampling_event_id: Mapped[int] = mapped_column(ForeignKey('sampling_events.id'), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey('indicators.id'), nullable=False)
    result_domain: Mapped[str | None] = mapped_column(String(100))
    measured_value_num: Mapped[float | None] = mapped_column(Float)
    measured_value_text: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(50))
    qa_status: Mapped[str | None] = mapped_column(String(50), default='raw')

    sampling_event: Mapped['SamplingEvent'] = relationship('SamplingEvent', back_populates='measurements')
    indicator: Mapped['Indicator'] = relationship('Indicator', back_populates='measurements')
