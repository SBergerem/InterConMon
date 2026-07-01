from fastapi import APIRouter, Request, Query
from api.api_context import ApiContext
from api.schemas.log_schema import LogListResponse
from models.models import LogType, LogLevel

router = APIRouter(prefix="/api/logs")


@router.get("/latest", response_model=LogListResponse)
def get_latest(
    request: Request,
    limit: int = Query(default=100, ge=1, le=1000),
    log_types: list[LogType] | None = Query(default=None),
    log_levels: list[LogLevel] | None = Query(default=None),
) -> LogListResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.log_service.get_latest_logs(limit, log_types, log_levels)
