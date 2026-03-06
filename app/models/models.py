from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soil_research_platform.app.db.session import Base


class Experiment(Base):
    __tablename__ = "dim_experiments"

    experiment_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[str]] = mapped_column(Text)
    experiment_id: Mapped[Optional[str]] = mapped_column(Text)
    experiment_title: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    expected_end_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sites: Mapped[list["Site"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    treatments: Mapped[list["Treatment"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "dim_sites"
    __table_args__ = (UniqueConstraint("experiment_sk", "site_id", name="uq_exp_site_id"),)

    site_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    experiment_sk: Mapped[int] = mapped_column(ForeignKey("dim_experiments.experiment_sk", ondelete="CASCADE"), nullable=False)
    site_id: Mapped[Optional[str]] = mapped_column(Text)
    field_identifier: Mapped[Optional[str]] = mapped_column(Text)
    gps_lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    gps_lon: Mapped[Optional[float]] = mapped_column(Numeric(9, 6))
    soil_type_texture: Mapped[Optional[str]] = mapped_column(Text)
    field_size_ha: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment: Mapped[Experiment] = relationship(back_populates="sites")
    plots: Mapped[list["Plot"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    sampling_events: Mapped[list["SamplingEvent"]] = relationship(back_populates="site", cascade="all, delete-orphan")


class Treatment(Base):
    __tablename__ = "dim_treatments"
    __table_args__ = (UniqueConstraint("experiment_sk", "treatment_code", name="uq_exp_treatment_code"),)

    treatment_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    experiment_sk: Mapped[int] = mapped_column(ForeignKey("dim_experiments.experiment_sk", ondelete="CASCADE"), nullable=False)
    treatment_code: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_name: Mapped[Optional[str]] = mapped_column(Text)
    treatment_type: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_control: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment: Mapped[Experiment] = relationship(back_populates="treatments")
    practices: Mapped[list["Practice"]] = relationship(back_populates="treatment", cascade="all, delete-orphan")
    plots: Mapped[list["Plot"]] = relationship(back_populates="treatment")


class Practice(Base):
    __tablename__ = "dim_practices"

    practice_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    treatment_sk: Mapped[int] = mapped_column(ForeignKey("dim_treatments.treatment_sk", ondelete="CASCADE"), nullable=False)
    practice_type: Mapped[Optional[str]] = mapped_column(Text)
    practice_name: Mapped[Optional[str]] = mapped_column(Text)
    practice_value: Mapped[Optional[str]] = mapped_column(Text)
    unit: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    treatment: Mapped[Treatment] = relationship(back_populates="practices")


class Plot(Base):
    __tablename__ = "dim_plots"
    __table_args__ = (UniqueConstraint("site_sk", "plot_id", name="uq_site_plot_id"),)

    plot_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_sk: Mapped[int] = mapped_column(ForeignKey("dim_sites.site_sk", ondelete="CASCADE"), nullable=False)
    treatment_sk: Mapped[int] = mapped_column(ForeignKey("dim_treatments.treatment_sk", ondelete="RESTRICT"), nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(Text)
    replicate_no: Mapped[Optional[int]] = mapped_column(Integer)
    block_no: Mapped[Optional[int]] = mapped_column(Integer)
    sample_point_id: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    site: Mapped[Site] = relationship(back_populates="plots")
    treatment: Mapped[Treatment] = relationship(back_populates="plots")
    sampling_events: Mapped[list["SamplingEvent"]] = relationship(back_populates="plot")


class Indicator(Base):
    __tablename__ = "dim_indicators"

    indicator_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    indicator_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    indicator_name: Mapped[str] = mapped_column(Text, nullable=False)
    default_unit: Mapped[Optional[str]] = mapped_column(Text)
    value_type: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    measurements: Mapped[list["Measurement"]] = relationship(back_populates="indicator")


class SamplingEvent(Base):
    __tablename__ = "dim_sampling_events"

    sample_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_sk: Mapped[int] = mapped_column(ForeignKey("dim_sites.site_sk", ondelete="CASCADE"), nullable=False)
    plot_sk: Mapped[Optional[int]] = mapped_column(ForeignKey("dim_plots.plot_sk", ondelete="SET NULL"))
    sample_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    layer_id: Mapped[Optional[str]] = mapped_column(Text)
    sampling_date: Mapped[Optional[date]] = mapped_column(Date)
    sampling_timepoint: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    site: Mapped[Site] = relationship(back_populates="sampling_events")
    plot: Mapped[Optional[Plot]] = relationship(back_populates="sampling_events")
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="sampling_event", cascade="all, delete-orphan")


class Measurement(Base):
    __tablename__ = "fact_measurements"

    measurement_sk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sample_sk: Mapped[int] = mapped_column(ForeignKey("dim_sampling_events.sample_sk", ondelete="CASCADE"), nullable=False)
    indicator_sk: Mapped[int] = mapped_column(ForeignKey("dim_indicators.indicator_sk", ondelete="RESTRICT"), nullable=False)
    result_domain: Mapped[Optional[str]] = mapped_column(Text)
    measured_value_num: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    measured_value_text: Mapped[Optional[str]] = mapped_column(Text)
    unit: Mapped[Optional[str]] = mapped_column(String)
    qa_status: Mapped[Optional[str]] = mapped_column(String, default="raw")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sampling_event: Mapped[SamplingEvent] = relationship(back_populates="measurements")
    indicator: Mapped[Indicator] = relationship(back_populates="measurements")
