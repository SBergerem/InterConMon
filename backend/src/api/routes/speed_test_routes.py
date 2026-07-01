from fastapi import APIRouter, Request, Query
from api.api_context import ApiContext
from api.schemas.speed_test_schema import SpeedTestListResponse

router = APIRouter(prefix="/api/speedtests")


@router.get("/latest")
def get_latest(request: Request, limit: int = Query(default=100, ge=1, le=1000)) -> SpeedTestListResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.speed_test_result_service.get_latest_speed_tests(limit)
