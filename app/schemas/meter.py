
from pydantic import BaseModel, ConfigDict


class Meter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    meter_number: str
    serial_number: str
    make: str
    phase: str
    status: str
    transformer_code: str | None = None
