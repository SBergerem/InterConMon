from app_config import AppConfig
from pathlib import Path
import json

class ConfigManager:
    
    def __init__(self):
        self._file_path = Path("config/settings.json")
        self._ensure_file_exists()
                
    def _ensure_file_exists(self):
        self._file_path.parent.mkdir(parents=True, exist_ok=True)   
        if not self._file_path.exists():
            self.save_config(AppConfig())
                          
                
    def load_config(self):
        self._ensure_file_exists()
        
        app_config = AppConfig()
        
        with open(self._file_path, "r", encoding="utf-8") as file:                  
            app_config.set_config_from_json(json.load(file))
            
        return app_config
    
    def save_config(self, config):
            with open(self._file_path, "w", encoding="utf-8") as file:
                json.dump(config.get_config_as_json(), file, indent=4)