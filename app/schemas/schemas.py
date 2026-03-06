from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from soil_research_platform.app.schemas.common import ORMModel


class ExperimentBase(BaseModel):
    project_id: Optional[str] = None
    experiment_id: Optional[str] = None
    experiment_title: Optional[str] = None
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None


class ExperimentCreate(ExperimentBase):
    experiment_id: str
    experiment_title: str


class ExperimentRead(ExperimentBase, ORMModel):
    experiment_sk: int
    created_at: datetime


class SiteBase(BaseModel):
    experiment_sk: int
    site_id: Optional[str] = None
    field_identifier: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    soil_type_texture: Optional[str] = None
    field_size_ha: Optional[float] = None


class SiteCreate(SiteBase):
    pass


class SiteRead(SiteBase, ORMModel):
    site_sk: int
    created_at: datetime


class TreatmentBase(BaseModel):
    experiment_sk: int
    treatment_code: str
    treatment_name: Optional[str] = None
    treatment_type: Optional[str] = None
    description: Optional[str] = None
    is_control: bool = False


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentRead(TreatmentBase, ORMModel):
    treatment_sk: int
    created_at: datetime


class PracticeBase(BaseModel):
    treatment_sk: int
    practice_type: Optional[str] = None
    practice_name: Optional[str] = None
    practice_value: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class PracticeCreate(PracticeBase):
    pass


class PracticeRead(PracticeBase, ORMModel):
    practice_sk: int
    created_at: datetime


class PlotBase(BaseModel):
    site_sk: int
    treatment_sk: int
    plot_id: Optional[str] = None
    replicate_no: Optional[int] = None
    block_no: Optional[int] = None
    sample_point_id: Optional[str] = None


class PlotCreate(PlotBase):
    pass


class PlotRead(PlotBase, ORMModel):
    plot_sk: int
    created_at: datetime


class SamplingEventBase(BaseModel):
    site_sk: int
    plot_sk: Optional[int] = None
    sample_id: str
    layer_id: Optional[str] = None
    sampling_date: Optional[date] = None
    sampling_timepoint: Optional[str] = None
    author: Optional[str] = None


class SamplingEventCreate(SamplingEventBase):
    pass


class SamplingEventRead(SamplingEventBase, ORMModel):
    sample_sk: int
    created_at: datetime


class IndicatorBase(BaseModel):
    indicator_code: str
    indicator_name: str
    default_unit: Optional[str] = None
    value_type: Optional[str] = None


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorRead(IndicatorBase, ORMModel):
    indicator_sk: int
    created_at: datetime


class MeasurementBase(BaseModel):
    sample_sk: int
    indicator_sk: int
    result_domain: Optional[str] = None
    measured_value_num: Optional[float] = None
    measured_value_text: Optional[str] = None
    unit: Optional[str] = None
    qa_status: Optional[str] = "raw"


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementRead(MeasurementBase, ORMModel):
    measurement_sk: int
    created_at: datetime
