
from app.models.meter import Meter, MeterSearchResponse


sample_meter = {
    "meterId": "J100000",
    "serialNo": "SE33962",
    "make": "HPL",
    "phaseType": "single",
    "installStatus": "Decommissioned",
    "dtCode": "DT-001",
}

meter = Meter(**sample_meter)

print("Validated meter:", meter.model_dump())

sample_response = {
    "data": [sample_meter],
    "total": 1,
    "page": 1,
    "pageSize": 20,
}

result = MeterSearchResponse(**sample_response)

print("Validated count:", len(result.data))
print("Page:", result.page)
