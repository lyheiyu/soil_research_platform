from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(10), nullable=False)
    round_no = Column(Integer, nullable=False)
    approval_no = Column(Integer, nullable=False)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    experiments = relationship('Experiment', back_populates='project', cascade='all, delete-orphan')


class Experiment(Base):
    __tablename__ = 'experiments'
    __table_args__ = (UniqueConstraint('project_id', 'experiment_code', name='uq_project_experiment_code'),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    experiment_code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    field_name = Column(String(255))
    start_date = Column(Date)
    expected_end_date = Column(Date)

    project = relationship('Project', back_populates='experiments')
    treatments = relationship('Treatment', back_populates='experiment', cascade='all, delete-orphan')
    plots = relationship('Plot', back_populates='experiment', cascade='all, delete-orphan')
    samples = relationship('Sample', back_populates='experiment', cascade='all, delete-orphan')


class Treatment(Base):
    __tablename__ = 'treatments'
    __table_args__ = (UniqueConstraint('experiment_id', 'treatment_code', name='uq_experiment_treatment_code'),)

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False, index=True)
    treatment_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    treatment_type = Column(String(100))
    description = Column(Text)
    is_control = Column(Boolean, default=False)

    experiment = relationship('Experiment', back_populates='treatments')
    practices = relationship('Practice', back_populates='treatment', cascade='all, delete-orphan')
    plots = relationship('Plot', back_populates='treatment')


class Practice(Base):
    __tablename__ = 'practices'
    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey('treatments.id', ondelete='CASCADE'), nullable=False, index=True)
    practice_type = Column(String(100), nullable=False)
    practice_name = Column(String(255), nullable=False)
    practice_value = Column(String(255))
    unit = Column(String(50))
    description = Column(Text)

    treatment = relationship('Treatment', back_populates='practices')


# class Plot(Base):
#     __tablename__ = 'plots'
#     __table_args__ = (UniqueConstraint('experiment_id', 'plot_code', name='uq_experiment_plot_code'),)
#
#     id = Column(Integer, primary_key=True, index=True)
#     experiment_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False, index=True)
#     treatment_id = Column(Integer, ForeignKey('treatments.id', ondelete='SET NULL'), nullable=True, index=True)
#     plot_code = Column(String(50), nullable=False)
#     replicate_no = Column(Integer)
#     block_no = Column(Integer)
#     sample_point = Column(String(100))
#
#     experiment = relationship('Experiment', back_populates='plots')
#     treatment = relationship('Treatment', back_populates='plots')
#     samples = relationship('Sample', back_populates='plot')
class Plot(Base):
    __tablename__ = 'plots'
    __table_args__ = (UniqueConstraint('experiment_id', 'plot_code', name='uq_experiment_plot_code'),)

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False, index=True)
    treatment_id = Column(Integer, ForeignKey('treatments.id', ondelete='SET NULL'), nullable=True, index=True)
    plot_code = Column(String(50), nullable=False)
    replicate_no = Column(Integer)
    sample_point = Column(String(100))
    gps_lat = Column(Float)
    gps_lon = Column(Float)

    experiment = relationship('Experiment', back_populates='plots')
    treatment = relationship('Treatment', back_populates='plots')
    samples = relationship('Sample', back_populates='plot')

class Indicator(Base):
    __tablename__ = 'indicators'
    id = Column(Integer, primary_key=True, index=True)
    indicator_code = Column(String(100), unique=True, nullable=False, index=True)
    indicator_name = Column(String(255), nullable=False)
    default_unit = Column(String(50))
    value_type = Column(String(50), nullable=False)
    category = Column(String(100))
    description = Column(Text)

    measurements = relationship('Measurement', back_populates='indicator')

#
# class Sample(Base):
#     __tablename__ = 'samples'
#     __table_args__ = (UniqueConstraint('experiment_id', 'sample_id', name='uq_experiment_sample_id'),)
#
#     id = Column(Integer, primary_key=True, index=True)
#     experiment_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False, index=True)
#     plot_id = Column(Integer, ForeignKey('plots.id', ondelete='SET NULL'), nullable=True, index=True)
#     sample_id = Column(String(100), nullable=False)
#     layer_id = Column(String(50))
#     sampling_date = Column(Date)
#     author = Column(String(255))
#
#     experiment = relationship('Experiment', back_populates='samples')
#     plot = relationship('Plot', back_populates='samples')
#     measurements = relationship('Measurement', back_populates='sample', cascade='all, delete-orphan')
class Sample(Base):
    __tablename__ = 'samples'
    __table_args__ = (UniqueConstraint('experiment_id', 'sample_id', name='uq_experiment_sample_id'),)

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'), nullable=False, index=True)
    plot_id = Column(Integer, ForeignKey('plots.id', ondelete='SET NULL'), nullable=True, index=True)
    sample_id = Column(String(100), nullable=False)

    sampling_timepoint = Column(String(10))   # T0 / T1 / T2
    layer_id = Column(String(50))
    depth_from_cm = Column(Integer)
    depth_to_cm = Column(Integer)

    sampling_date = Column(Date)
    author = Column(String(255))

    clouds = Column(String(50))
    temperature_band = Column(String(50))
    rainfall_condition = Column(String(100))

    experiment = relationship('Experiment', back_populates='samples')
    plot = relationship('Plot', back_populates='samples')
    measurements = relationship('Measurement', back_populates='sample', cascade='all, delete-orphan')

class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True, index=True)
    sample_id_fk = Column(Integer, ForeignKey('samples.id', ondelete='CASCADE'), nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey('indicators.id', ondelete='RESTRICT'), nullable=False, index=True)
    measured_value_num = Column(Numeric(18, 6))
    measured_value_text = Column(Text)
    unit = Column(String(50))
    qa_status = Column(String(50), default='raw')

    sample = relationship('Sample', back_populates='measurements')
    indicator = relationship('Indicator', back_populates='measurements')
