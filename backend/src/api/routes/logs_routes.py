from fastapi import APIRouter, Request, Query
from api.api_context import ApiContext
from backend.src.api.schemas.log_schema import LatestLogsResponse
from models.models import LogType, LogLevel

router = APIRouter(prefix="/api/logs")


@router.get("/latest", response_model=LatestLogsResponse)
def get_latest(
    request: Request,
    limit: int = Query(default=100, ge=1, le=1000),
    log_types: list[LogType] | None = Query(default=None),
    log_levels: list[LogLevel] | None = Query(default=None),
) -> LatestLogsResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.log_service.get_latest_logs(limit, log_types, log_levels)
