from settings.app_start_config import AppStartConfig
from pathlib import Path
import json
from utils.app_logger import AppLogger
from models.models import LogType


class AppStartConfigManager:
    _file_path = Path("config/app_start_settings.json")

    @classmethod
    def _ensure_file_exists(cls) -> None:
        cls._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not cls._file_path.exists():
            cls.save_config(AppStartConfig())

    @classmethod
    def initialize(cls) -> None:
        cls._ensure_file_exists()

    @classmethod
    def load_config(cls) -> AppStartConfig:
        cls._ensure_file_exists()

        app_config = AppStartConfig()

        with open(cls._file_path, "r", encoding="utf-8") as file:
            app_config.set_config_from_dict(json.load(file))

        AppLogger.info(LogType.CONFIG, "App start config loaded", "AppStartConfigManager", "load_config")

        return app_config

    @classmethod
    def save_config(cls, config: AppStartConfig) -> None:
        with open(cls._file_path, "w", encoding="utf-8") as file:
            json.dump(config.get_config_as_dict(), file, indent=4)

        AppLogger.info(LogType.CONFIG, "App start config saved", "AppStartConfigManager", "save_config")
