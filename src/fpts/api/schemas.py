from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)

    model_config = ConfigDict(frozen=True)


class PhenologyPointResponse(BaseModel):
    """
    Phenology metrics for a single location and year.
    This is the shape that our phenology endpoints will return to a client.
    """

    year: int
    location: LocationSchema
    sos_date: Optional[date] = None
    eos_date: Optional[date] = None
    season_length: Optional[int] = None
    is_forest: bool

    model_config = ConfigDict(frozen=True)


class PhenologyYearMetricSchema(BaseModel):
    year: int
    sos_date: Optional[date] = None
    eos_date: Optional[date] = None
    season_length: Optional[int] = None
    is_forest: bool

    model_config = ConfigDict(frozen=True)


class PhenologyTimeseriesResponse(BaseModel):
    product: str
    location: LocationSchema
    start_year: int
    end_year: int
    metrics: list[PhenologyYearMetricSchema]

    model_config = ConfigDict(frozen=True)
