from models.models import LogLevel, LogType
from typing import cast
from utils.app_logger import AppLogger


class DatabaseConfig:
    def __init__(self) -> None:
        self.path: str = "./data/interconmon.db"

    def get_config_as_dict(self) -> dict[str, object]:
        return {"path": self.path}

    def set_config_from_dict(self, config: dict[str, object]) -> None:
        if not isinstance(config["path"], str):
            raise ValueError("Database path must be a string")

        self.path = str(config.get("path", "./data/interconmon.db"))


class EncryptionConfig:

    def __init__(self) -> None:
        self.secret_path: str = "./config/secret.key"

    def get_config_as_dict(self) -> dict[str, str]:
        return {"secret_path": self.secret_path}

    def set_config_from_dict(self, config: dict[str, str]) -> None:
        self.secret_path = config.get("secret_path", "./config/secret.key")


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
        log_level: list[LogLevel] = []

        for level_text in level_texts:
            try:
                log_level.append(LogLevel(str(level_text)))
            except ValueError:
                AppLogger.info(
                    LogType.SYSTEM,
                    f"{level_text} is not a LogLevel. Skipping..",
                    "LogConfig",
                    "_parse_log_levels",
                    skip_database=True,
                )

        return log_level

    def get_config_as_dict(self) -> dict[str, list[str]]:
        return {
            "enabled_console_log_levels": [level.value for level in self.enabled_console_log_levels],
            "enabled_database_log_levels": [level.value for level in self.enabled_database_log_levels],
        }

    def set_config_from_dict(self, config: dict[str, object]) -> None:
        console_levels: list[str] | None = cast(list[str] | None, config.get("enabled_console_log_levels", None))
        database_levels: list[str] | None = cast(list[str] | None, config.get("enabled_database_log_levels", None))

        if console_levels is not None:
            parsed_console_levels: list[LogLevel] = self._parse_log_levels(console_levels)
        else:
            parsed_console_levels = [
                LogLevel.INFO,
                LogLevel.WARNING,
                LogLevel.ERROR,
                LogLevel.CRITICAL,
            ]

        if database_levels is not None:
            parsed_database_levels: list[LogLevel] = self._parse_log_levels(database_levels)
        else:
            parsed_database_levels = [
                LogLevel.INFO,
                LogLevel.WARNING,
                LogLevel.ERROR,
                LogLevel.CRITICAL,
            ]

        self.enabled_console_log_levels = parsed_console_levels
        self.enabled_database_log_levels = parsed_database_levels


class ApiConfig:

    def __init__(self) -> None:
        self.host: str = "127.0.0.1"
        self.port: int = 8000
        self.cors_allowed_origins: list[str] = ["http://127.0.0.1:5173"]

    def get_config_as_dict(self) -> dict[str, object]:
        return {"host": self.host, "port": self.port, "cors_allowed_origins": self.cors_allowed_origins}

    def set_config_from_dict(self, config: dict[str, object]) -> None:
        self.host = cast(str, config.get("host", "127.0.0.1"))
        self.port = cast(int, config.get("port", 8000))
        self.cors_allowed_origins = cast(list[str], config.get("cors_allowed_origins", ["http://127.0.0.1:5173"]))


class AppStartConfig:

    def __init__(self) -> None:
        self.database_config: DatabaseConfig = DatabaseConfig()
        self.encryption_config: EncryptionConfig = EncryptionConfig()
        self.log_config: LogConfig = LogConfig()
        self.api_config: ApiConfig = ApiConfig()

    def get_config_as_dict(self) -> dict[str, object]:
        return {
            "encryption": self.encryption_config.get_config_as_dict(),
            "database": self.database_config.get_config_as_dict(),
            "logs": self.log_config.get_config_as_dict(),
            "api": self.api_config.get_config_as_dict(),
        }

    def set_config_from_dict(self, config: dict[str, dict[str, object]]) -> None:
        self.encryption_config.set_config_from_dict(cast(dict[str, str], config.get("encryption", {})))
        self.database_config.set_config_from_dict(config.get("database", {}))
        self.log_config.set_config_from_dict(config.get("logs", {}))
        self.api_config.set_config_from_dict(config.get("api", {}))
