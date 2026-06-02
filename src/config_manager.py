from app_config import AppConfig
from pathlib import Path
import json

class ConfigManager:
    _file_path = None
    
    @classmethod           
    def _ensure_file_exists(cls):
        cls._file_path = Path("config/settings.json")
        cls._file_path.parent.mkdir(parents=True, exist_ok=True)   
        if not cls._file_path.exists():
            cls.save_config(AppConfig())
    
    @classmethod
    def initialize(cls):
        _file_path = Path("config/settings.json")
        cls._ensure_file_exists()
             
                                   
    @classmethod            
    def load_config(cls):
        cls._ensure_file_exists()
        
        app_config = AppConfig()
        
        with open(cls._file_path, "r", encoding="utf-8") as file:                  
            app_config.set_config_from_json(json.load(file))
            
        return app_config
    
    @classmethod
    def save_config(cls, config):
        with open(cls._file_path, "w", encoding="utf-8") as file:
            json.dump(config.get_config_as_json(), file, indent=4)
    
