from database.app_settings_repository import AppSettingsRepository
from api.mappers.app_settings_mapper import AppSettingsMapper
from api.schemas.app_settings_schema import AppSettingListResponse
from settings.app_settings import AppSettings


class AppSettingsService:

    def __init__(self, repository: AppSettingsRepository) -> None:
        self._repository: AppSettingsRepository = repository

    def get_app_settings(self, app_settings: AppSettings) -> AppSettingListResponse:
        return AppSettingsMapper.map_app_settings_to_response(app_settings)
