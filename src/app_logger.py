from models import LogEntry, LogLevel, LogType
    
class AppLogger:
    _current_log_level = LogLevel.INFO
    
    def __init__(self):
        pass
    
    @classmethod
    def set_log_level(cls, log_level):
        cls._current_log_level = log_level
    
    @classmethod
    def debug(cls, log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def info(cls, log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def warning(cls, log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def error(cls, log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass
    
    @classmethod
    def critical(cls, log_type, message, related_object_type=None, related_object_id=None, details_json=None):
        pass