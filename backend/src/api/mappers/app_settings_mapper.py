from settings.app_settings import AppSettings
from api.schemas.app_settings_schema import AppSettingResponse, AppSettingCategoryResponse, AppSettingListResponse


class AppSettingsMapper:

    @classmethod
    def map_app_settings_to_response(cls, settings: AppSettings | None) -> AppSettingListResponse:
        if settings is None:
            return AppSettingListResponse(items=[])
        else:
            result = AppSettingListResponse(items=[])

            category = AppSettingCategoryResponse(category_name="latency_test_settings", category_settings=[])
            category.category_settings.append(
                AppSettingResponse(
                    original_name="latency_test_settings.enabled",
                    display_name="enabled",
                    value=settings.get_latency_test_settings().get_enabled(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="latency_test_settings.targets",
                    display_name="targets",
                    value=settings.get_latency_test_settings().get_targets(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="latency_test_settings.interval_seconds",
                    display_name="interval_seconds",
                    value=settings.get_latency_test_settings().get_interval_seconds(),
                )
            )
            result.items.append(category)

            category = AppSettingCategoryResponse(category_name="outage_check", category_settings=[])
            category.category_settings.append(
                AppSettingResponse(
                    original_name="outage_check.enabled",
                    display_name="enabled",
                    value=settings.get_outage_check_settings().get_enabled(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="outage_check.max_failed_group_test_count",
                    display_name="max_failed_group_test_count",
                    value=settings.get_outage_check_settings().get_max_failed_group_test_count(),
                )
            )
            result.items.append(category)

            category = AppSettingCategoryResponse(category_name="gateway_test", category_settings=[])
            category.category_settings.append(
                AppSettingResponse(
                    original_name="gateway_test.enabled",
                    display_name="enabled",
                    value=settings.get_gateway_test_settings().get_enabled(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="gateway_test.targets",
                    display_name="targets",
                    value=settings.get_gateway_test_settings().get_targets(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="gateway_test.interval_seconds",
                    display_name="interval_seconds",
                    value=settings.get_gateway_test_settings().get_interval_seconds(),
                )
            )
            result.items.append(category)

            category = AppSettingCategoryResponse(category_name="speed_test", category_settings=[])
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.enabled",
                    display_name="enabled",
                    value=settings.get_speed_test_settings().get_enabled(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.interval_minutes",
                    display_name="interval_minutes",
                    value=settings.get_speed_test_settings().get_interval_minutes(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.run_upload",
                    display_name="run_upload",
                    value=settings.get_speed_test_settings().get_run_upload(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.run_download",
                    display_name="run_download",
                    value=settings.get_speed_test_settings().get_run_download(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.tool",
                    display_name="tool",
                    value=settings.get_speed_test_settings().get_tool(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.max_duration_sec",
                    display_name="max_duration_sec",
                    value=settings.get_speed_test_settings().get_max_duration_sec(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.server_id",
                    display_name="server_id",
                    value=settings.get_speed_test_settings().get_server_id(),
                )
            )
            category.category_settings.append(
                AppSettingResponse(
                    original_name="speed_test.only_when_connection_ok",
                    display_name="only_when_connection_ok",
                    value=settings.get_speed_test_settings().get_only_when_connection_ok(),
                )
            )
            result.items.append(category)

            return result
