from fastapi import APIRouter, Request
from api.api_context import ApiContext
from api.schemas.connection_diagnosis_schema import LatestConnectionDiagnosisResponse

router = APIRouter(prefix="/api/connection")


@router.get("/latest", response_model=LatestConnectionDiagnosisResponse)
def get_latest(request: Request) -> LatestConnectionDiagnosisResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.connection_diagnosis_service.get_latest_connection_diagnosis()
