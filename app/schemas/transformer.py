
from pydantic import BaseModel, ConfigDict, Field


class Transformer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    name: str
    feeder_code: str = Field(alias="feederCode")
    capacity_kva: float = Field(alias="capacityKva", gt=0)


class TransformerListResponse(BaseModel):
    items: list[Transformer]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(alias="pageSize", ge=1)
