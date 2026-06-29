from fastapi import APIRouter, Request
from api.api_context import ApiContext
from database.app_settings_repository import AppSettingsRepository
from settings.app_settings import AppSettings
from typing import Any

router = APIRouter(prefix="/api/settings")


@router.get("/all")
def get_all(request: Request) -> dict[str, Any]:
    api_context: ApiContext = request.app.state.api_context

    app_settings_repository: AppSettingsRepository = api_context.app_settings_repository

    app_settings: AppSettings = app_settings_repository.load()

    return {
        "latency_test_settings": {
            "targets": app_settings.get_latency_test_settings().get_targets(),
            "interval_seconds": app_settings.get_latency_test_settings().get_interval_seconds(),
            "enabled": app_settings.get_latency_test_settings().get_enabled(),
        },
        "outage_check": {
            "enabled": app_settings.get_outage_check_settings().get_enabled(),
            "max_failed_group_test_count": app_settings.get_outage_check_settings().get_max_failed_group_test_count(),
        },
        "gateway_test": {
            "enabled": app_settings.get_gateway_test_settings().get_enabled(),
            "targets": app_settings.get_gateway_test_settings().get_targets(),
            "interval_seconds": app_settings.get_gateway_test_settings().get_interval_seconds(),
        },
        "speed_test": {
            "enabled": app_settings.get_speed_test_settings().get_enabled(),
            "interval_minutes": app_settings.get_speed_test_settings().get_interval_minutes(),
            "run_upload": app_settings.get_speed_test_settings().get_run_upload(),
            "run_download": app_settings.get_speed_test_settings().get_run_download(),
            "tool": app_settings.get_speed_test_settings().get_tool(),
            "max_duration_sec": app_settings.get_speed_test_settings().get_max_duration_sec(),
            "server_id": app_settings.get_speed_test_settings().get_server_id(),
            "only_when_connection_ok": app_settings.get_speed_test_settings().get_only_when_connection_ok(),
        },
    }
