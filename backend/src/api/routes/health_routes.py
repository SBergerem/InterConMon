from fastapi import APIRouter
from api.schemas.health_schema import HealthCheckHealthResponse, HealthResponse

router = APIRouter()


@router.get("/api/health_check", response_model=HealthCheckHealthResponse)
def health_check() -> HealthCheckHealthResponse:
    try:
        return HealthCheckHealthResponse(item=HealthResponse(status=True, app_name="InterConMon"))
    except:
        return HealthCheckHealthResponse(item=None)
