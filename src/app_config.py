from models import LogLevel

class DatabaseConfig:
    def __init__(self):
        self.path = "./data/interconmon.db"

    def get_config_as_json(self):
        return {"path": self.path}

    def set_config_from_json(self, config):
        self.path = config["path"]


class EncryptionConfig:

    def __init__(self):
        self.secret_path = "./config/secret.key"

    def get_config_as_json(self):
        return {"secret_path": self.secret_path}

    def set_config_from_json(self, config):
        self.secret_path = config["secret_path"]


class LogConfig:

    def __init__(self):
        self.log_level = LogLevel.INFO

    def get_config_as_json(self):
        return {"log_level": self.log_level.value}

    def set_config_from_json(self, config):
        self.log_level = LogLevel(config["log_level"])


class AppConfig:

    def __init__(self):
        self.database_config = DatabaseConfig()
        self.encryption_config = EncryptionConfig()
        self.log_config = LogConfig()

    def get_config_as_json(self):
        return {
            "encryption": self.encryption_config.get_config_as_json(),
            "database": self.database_config.get_config_as_json(),
            "logs": self.log_config.get_config_as_json(),
        }

    def set_config_from_json(self, config):
        self.encryption_config.set_config_from_json(config["encryption"])
        self.database_config.set_config_from_json(config["database"])
        self.log_config.set_config_from_json(config["logs"])
