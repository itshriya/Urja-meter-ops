
from typing import Any

from pydantic import BaseModel


class MeterGeoData(BaseModel):
    latitude: str
    longitude: str


class MeterGeoResponse(BaseModel):
    data: MeterGeoData


class MeterEnergyResponse(BaseModel):
    data: list[dict[str, Any]]
