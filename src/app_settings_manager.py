from models import LogType
import json
from app_logger import AppLogger
from app_settings_models import AppSettings
from database_manager import DatabaseManager

class AppSettingsManager:

    def __init__(self, database_manager: DatabaseManager) -> None:
        self.app_settings: AppSettings = AppSettings()
        self._database_manager: DatabaseManager = database_manager

    def set_settings(self) -> None:
        settings: list[tuple[str, str]] = self._database_manager.load_settings()
        
        for settings_name, settings_json in settings:
            try:
                match settings_name:
                    case "latency_test_settings_targets":
                        self.app_settings.latency_test_settings.targets = json.loads(
                            settings_json
                        )["targets"]

                    case "latency_test_settings_interval_seconds":
                        self.app_settings.latency_test_settings.interval_seconds = (
                            json.loads(settings_json)["interval"]
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
                raise ex

    def get_settings(self) -> None:
        try:
            settings: list[tuple[str, object]] = [
                (
                    "latency_test_settings_targets",
                    {"targets": self.app_settings.latency_test_settings.targets},
                ),
                (
                    "latency_test_settings_interval_seconds",
                    {
                        "interval": self.app_settings.latency_test_settings.interval_seconds
                    },
                ),
            ]
            
            self._database_manager.save_settings(settings)
        except Exception as ex:
            AppLogger.error(
                LogType.SETTINGS, str(ex), "AppSettingsManager", "get_settings"
            )
            raise ex
