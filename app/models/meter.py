
from pydantic import BaseModel


class Meter(BaseModel):
    meterId: str
    serialNo: str
    make: str
    phaseType: str
    installStatus: str
    dtCode: str

class MeterSearchResponse(BaseModel):
    data: list[Meter]
    total: int
    page: int
    pageSize: int
