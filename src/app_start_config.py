from models import LogLevel, LogType
from typing import cast
from app_logger import AppLogger


class DatabaseConfig:
    def __init__(self) -> None:
        self.path: str = "./data/interconmon.db"

    def get_config_as_dict(self) -> dict[str, object]:
        return {"path": self.path}

    def set_config_from_dict(self, config: dict[str, object]) -> None:
        if not isinstance(config["path"], str):
            raise ValueError("Database path must be a string")

        self.path = str(config["path"])


class EncryptionConfig:

    def __init__(self) -> None:
        self.secret_path: str = "./config/secret.key"

    def get_config_as_dict(self) -> dict[str, str]:
        return {"secret_path": self.secret_path}

    def set_config_from_dict(self, config: dict[str, str]) -> None:
        self.secret_path = config["secret_path"]


class LogConfig:

    def __init__(self) -> None:
        self.enabled_console_log_levels: list[LogLevel] = [
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]
        self.enabled_database_log_levels: list[LogLevel] = [
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]

    def _parse_log_levels(self, level_texts: list[str]) -> list[LogLevel]:
        result: list[LogLevel] = []

        for level_text in level_texts:
            try:
                result.append(LogLevel(str(level_text)))
            except ValueError:
                AppLogger.info(
                    LogType.SYSTEM,
                    f"{level_text} is not a LogLevel. Skipping..",
                    "LogConfig",
                    "_parse_log_levels",
                    skip_database=True,
                )

        return result

    def get_config_as_dict(self) -> dict[str, list[str]]:
        return {
            "enabled_console_log_levels": [level.value for level in self.enabled_console_log_levels],
            "enabled_database_log_levels": [level.value for level in self.enabled_database_log_levels],
        }

    def set_config_from_dict(self, config: dict[str, object]) -> None:
        console_levels: list[str] = cast(list[str], config["enabled_console_log_levels"])
        database_levels: list[str] = cast(list[str], config["enabled_database_log_levels"])

        self.enabled_console_log_levels = self._parse_log_levels(console_levels)
        self.enabled_database_log_levels = self._parse_log_levels(database_levels)


class AppStartConfig:

    def __init__(self) -> None:
        self.database_config = DatabaseConfig()
        self.encryption_config = EncryptionConfig()
        self.log_config = LogConfig()

    def get_config_as_dict(self) -> dict[str, object]:
        return {
            "encryption": self.encryption_config.get_config_as_dict(),
            "database": self.database_config.get_config_as_dict(),
            "logs": self.log_config.get_config_as_dict(),
        }

    def set_config_from_dict(self, config: dict[str, dict[str, object]]) -> None:
        self.encryption_config.set_config_from_dict(cast(dict[str, str], config["encryption"]))
        self.database_config.set_config_from_dict(config["database"])
        self.log_config.set_config_from_dict(config["logs"])
