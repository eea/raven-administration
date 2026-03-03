from pydantic import BaseModel, conlist
from typing import List, Union, Optional
from datetime import datetime


class StatisticsModel(BaseModel):
    year: Optional[int] = None  # Legacy field for backward compatibility
    years: Optional[Union[List[int], int]] = None  # New field supporting multiple years
    pollutant: str
    aggregation_process: str

    def __getitem__(self, key):
        return super().__getattribute__(key)

    @property
    def year_list(self) -> List[int]:
        """Return years as a list, supporting both legacy 'year' and new 'years' fields"""
        if self.years is not None:
            if isinstance(self.years, list):
                return self.years
            return [self.years]
        elif self.year is not None:
            return [self.year]
        return []
