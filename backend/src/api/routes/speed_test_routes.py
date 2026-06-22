from fastapi import APIRouter, Request
from backend.src.api.api_context import ApiContext
from backend.src.database.speed_test_result_repository import SpeedTestResultRepository
from backend.src.models.models import SpeedTestResult
from typing import Any

router = APIRouter(prefix="/api/speedtests")


@router.get("/latest")
def get_latest(request: Request) -> dict[str, Any]:
    api_context: ApiContext = request.app.state.api_context

    speed_test_repository: SpeedTestResultRepository = api_context.speed_test_result_repository

    latest_speed_test: SpeedTestResult | None = speed_test_repository.load_latest()

    if latest_speed_test is None:
        return {"speedtest": None}

    return {
        "id": latest_speed_test.id,
        "date_time": latest_speed_test.date_time,
        "success": latest_speed_test.success,
        "download_mbps": latest_speed_test.download_mbps,
        "upload_mbps": latest_speed_test.upload_mbps,
        "ping_ms": latest_speed_test.ping_ms,
        "jitter_ms": latest_speed_test.jitter_ms,
        "server_name": latest_speed_test.server_name,
        "server_location": latest_speed_test.server_location,
        "server_id": latest_speed_test.server_id,
        "server_url": latest_speed_test.server_url,
        "isp": latest_speed_test.isp,
        "external_ip": latest_speed_test.external_ip,
        "error_message": latest_speed_test.error_message,
        "duration_sec": latest_speed_test.duration_sec,
        "tool": latest_speed_test.tool,
    }
