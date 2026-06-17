from fastapi import APIRouter, Request
from backend.api.api_context import ApiContext
from backend.database.connection_diagnosis_repository import ConnectionDiagnosisRepository
from backend.models.models import ConnectionDiagnosis
from typing import Any

router = APIRouter(prefix="/api/connection")


@router.get("/latest")
def get_latest(request: Request) -> dict[str, Any]:
    api_context: ApiContext = request.app.state.api_context

    repository: ConnectionDiagnosisRepository = api_context.connection_diagnosis_repository

    connection_diagnosis: ConnectionDiagnosis | None = repository.load_latest()

    if connection_diagnosis is None:
        return {"connection": None}

    return {
        "id": connection_diagnosis.id,
        "date_time": connection_diagnosis.date_time,
        "network_diagnosis_type": connection_diagnosis.network_diagnosis_type,
        "gateway_latency_test_group_id": connection_diagnosis.gateway_latency_test_group_id,
        "server_latency_test_group_id": connection_diagnosis.server_latency_test_group_id,
    }
