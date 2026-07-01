from fastapi import APIRouter, Request, Query
from api.api_context import ApiContext
from api.schemas.outage_schema import OutageListResponse

router = APIRouter(prefix="/api/outages")


@router.get("/latest")
def get_latest(request: Request, limit: int = Query(default=100, ge=1, le=1000)) -> OutageListResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.outage_service.get_latest_outages(limit)
