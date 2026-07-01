from fastapi import APIRouter, Request
from api.api_context import ApiContext
from api.schemas.app_settings_schema import AppSettingListResponse

router = APIRouter(prefix="/api/settings")


@router.get("/all")
def get_all(request: Request) -> AppSettingListResponse:
    api_context: ApiContext = request.app.state.api_context
    return api_context.app_settings_service.get_app_settings(api_context.app_settings)
