from pydantic import BaseModel
from typing import List
from typing import Optional


class ExceedanceMethodDataModel(BaseModel):
    assessment_data_id: str
    exceedance_description_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class ExceedanceModel(BaseModel):
    id: str
    attainment_id: str
    exceedance_description_id: str
    exceedance_type_id: str
    area_classification_id: str
    adjustment_type_id: str
    reason_id: str
    exceedance_value: float
    has_exceedance: bool

    population_year: Optional[int] = None
    exposed_population: Optional[int] = None
    surface_area: Optional[float] = None
    vegetation_area: Optional[float] = None
    other_reason: Optional[str] = None
    adjustment_source_id: Optional[str] = None
   
    def __getitem__(self, key):
        return super().__getattribute__(key)
