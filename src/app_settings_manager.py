from models import LogType
import json
from app_logger import AppLogger
from app_settings_models import AppSettings
from database_manager import DatabaseManager
from threading import Lock


class AppSettingsManager:

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._lock_app_settings: Lock = Lock()

        self._app_settings: AppSettings = AppSettings()
        self._database_manager: DatabaseManager = database_manager

    def get_app_settings(self) -> AppSettings:
        with self._lock_app_settings:
            return self._app_settings

    def load_settings(self) -> None:
        settings: list[tuple[str, str]] = self._database_manager.load_settings()

        for settings_name, settings_json in settings:
            try:
                match settings_name:
                    case "latency_test_settings_targets":
                        self.get_app_settings().get_latency_test_settings().set_targets(
                            json.loads(settings_json)["targets"]
                        )

                    case "latency_test_settings_interval_seconds":
                        self.get_app_settings().get_latency_test_settings().set_interval_seconds(
                            json.loads(settings_json)["interval"]
                        )
                    case "latency_test_settings_max_failed_group_test_count":
                        self.get_app_settings().get_latency_test_settings().set_max_failed_group_test_count(
                            json.loads(settings_json)["count"]
                        )

                    case _:
                        pass
            except Exception as ex:
                AppLogger.error(
                    LogType.SETTINGS,
                    str(ex),
                    "AppSettingsManager",
                    "set_settings",
                    details={"settings": settings_json},
                )
                raise

    def save_settings(self) -> None:
        try:
            settings: list[tuple[str, object]] = [
                (
                    "latency_test_settings_targets",
                    {"targets": self.get_app_settings().get_latency_test_settings().get_targets()},
                ),
                (
                    "latency_test_settings_interval_seconds",
                    {"interval": self.get_app_settings().get_latency_test_settings().get_interval_seconds()},
                ),
                (
                    "latency_test_settings_max_failed_group_test_count",
                    {"count": self.get_app_settings().get_latency_test_settings().get_max_failed_group_test_count()},
                ),
            ]

            self._database_manager.save_settings(settings)
        except Exception as ex:
            AppLogger.error(LogType.SETTINGS, str(ex), "AppSettingsManager", "get_settings")
            raise
