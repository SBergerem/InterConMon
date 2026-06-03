from models import LogLevel
from typing import cast


class DatabaseConfig:
    def __init__(self):
        self.path: str = "./data/interconmon.db"

    def get_config_as_json(self) -> dict[str, object]:        
        return {"path": self.path}

    def set_config_from_json(self, config: dict[str, object]) -> None:
        if not isinstance(config["path"], str):
            raise ValueError("Database path must be a string")
        
        self.path = str(config["path"])


class EncryptionConfig:

    def __init__(self):
        self.secret_path = "./config/secret.key"

    def get_config_as_json(self) -> dict[str, object]:
        return {"secret_path": self.secret_path}

    def set_config_from_json(self, config: dict[str, object]) -> None:
        self.secret_path = config["secret_path"]


class LogConfig:

    def __init__(self):
        self.enabled_console_log_levels = [
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]
        self.enabled_database_log_levels = [
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]

    def get_config_as_json(self) -> dict[str, list[str]]:
        return {
            "enabled_console_log_levels": [
                level.value for level in self.enabled_console_log_levels
            ],
            "enabled_database_log_levels": [
                level.value for level in self.enabled_database_log_levels
            ],
        }

    def set_config_from_json(self, config: dict[str, object]) -> None:
        console_levels = console_levels = cast(
            list[str], config["enabled_console_log_levels"]
        )
        database_levels = cast(list[str], config["enabled_database_log_levels"])

        self.enabled_console_log_levels = [
            LogLevel(level_text) for level_text in console_levels
        ]
        self.enabled_database_log_levels = [
            LogLevel(level_text) for level_text in database_levels
        ]


class AppStartConfig:

    def __init__(self):
        self.database_config = DatabaseConfig()
        self.encryption_config = EncryptionConfig()
        self.log_config = LogConfig()

    def get_config_as_json(self) -> dict[str, object]:
        return {
            "encryption": self.encryption_config.get_config_as_json(),
            "database": self.database_config.get_config_as_json(),
            "logs": self.log_config.get_config_as_json(),
        }

    def set_config_from_json(self, config: dict[str, dict[str, object]]) -> None:
        self.encryption_config.set_config_from_json(config["encryption"])
        self.database_config.set_config_from_json(config["database"])
        self.log_config.set_config_from_json(config["logs"])
