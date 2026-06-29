from pydantic import BaseModel
from models.models import NetworkDiagnosisType


class ConnectionDiagnosisResponse(BaseModel):
    id: int
    date_time: str
    network_diagnosis_type: NetworkDiagnosisType
    gateway_latency_test_group_id: int
    server_latency_test_group_id: int


class LatestConnectionDiagnosisResponse(BaseModel):
    item: ConnectionDiagnosisResponse | None
