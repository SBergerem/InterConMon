class DatabaseConfig:
    def __init__(self):
        self.host = ""
        self.port = 0
        self.name = ""
        self.user = ""
        self.password_encrypted = ""
        
    def get_config_as_json(self):
        return {
            "host": self.host,
            "port": self.port,
            "name": self.name,
            "user": self.user,
            "password_encrypted": self.password_encrypted 
        }
        
    def set_config_from_json(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.name = config["name"]
        self.user = config["user"]
        self.password_encrypted = config["password_encrypted"] 


class EncryptionConfig:

    def __init__(self):
        self.secret_path = "./config/secret.key"
        
    def get_config_as_json(self):
        return {
            "secret_path": self.secret_path
        }
    
    def set_config_from_json(self, config):
        self.secret_path = config["secret_path"]


class AppConfig:
   
    def __init__(self):
        self.database_config = DatabaseConfig()
        self.encryption_config = EncryptionConfig()
        
    def get_config_as_json(self):
        return {
            "encryption": self.encryption_config.get_config_as_json(),
            "database": self.database_config.get_config_as_json()
        }
        
    def set_config_from_json(self, config):
        self.encryption_config.set_config_from_json(config["encryption"])
        self.database_config.set_config_from_json(config["database"])
        