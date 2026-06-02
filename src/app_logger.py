from enum import Enum
from models import LogEntry

class LogType(Enum):
    UNKNOWN = "unknown"    
    SYSTEM = "system"
    DATABASE = "database"
    OUTAGE = "outage"
    CONFIG = "config"
    WEB = "web"
    EXPORT = "export"
    SECURITY = "security"
    
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
class AppLogger:
    _current_log_level = LogLevel.INFO
    
    def __init__(self):
        pass
    
    @classmethod
    def set_log_level(log_level):
        _current_log_level = log_level
    
    @classmethod
    def debug(log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def info(log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def warning(log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def error(log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def critical(log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass