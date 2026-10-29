
from pydantic import BaseModel


class Transformer(BaseModel):
    code: str
    name: str
    feederCode: str
    capacityKva: float


class TransformerSearchResponse(BaseModel):
    data: list[Transformer]
