from models import LogLevel
from typing import cast


class DatabaseConfig:
    def __init__(self) -> None:
        self.path = "./data/interconmon.db"

    def get_config_as_json(self) -> dict[str, str]:
        return {"path": self.path}

    def set_config_from_json(self, config: dict[str, str]) -> None:
        self.path = config["path"]


class EncryptionConfig:

    def __init__(self) -> None:
        self.secret_path = "./config/secret.key"

    def get_config_as_json(self) -> dict[str, str]:
        return {"secret_path": self.secret_path}

    def set_config_from_json(self, config: dict[str, str]) -> None:
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

    def get_config_as_json(self) -> dict[str, object]:
        return {
            "enabled_console_log_levels": [
                level.value for level in self.enabled_console_log_levels
            ],
            "enabled_database_log_levels": [
                level.value for level in self.enabled_database_log_levels
            ],
        }

    def set_config_from_json(self, config: dict[str, object]) -> None:
        console_levels: list[str] = cast(
            list[str], config["enabled_console_log_levels"]
        )
        database_levels: list[str] = cast(
            list[str], config["enabled_database_log_levels"]
        )

        self.enabled_console_log_levels = [
            LogLevel(level_text) for level_text in console_levels
        ]

        self.enabled_database_log_levels = [
            LogLevel(level_text) for level_text in database_levels
        ]


class AppConfig:

    def __init__(self) -> None:
        self.database_config = DatabaseConfig()
        self.encryption_config = EncryptionConfig()
        self.log_config = LogConfig()

    def get_config_as_json(self) -> dict[str, object]:
        return {
            "encryption": self.encryption_config.get_config_as_json(),
            "database": self.database_config.get_config_as_json(),
            "logs": self.log_config.get_config_as_json(),
        }

    def set_config_from_json(self, config: dict[str, object]) -> None:
        self.encryption_config.set_config_from_json(cast(dict[str, str], config["encryption"]))
        self.database_config.set_config_from_json(cast(dict[str, str], config["database"]))
        self.log_config.set_config_from_json(cast(dict[str, object], config["logs"]))
