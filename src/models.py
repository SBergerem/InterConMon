from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ConnectionState(Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"


class OutageChangeState(Enum):
    NONE = "none"
    STARTED = "started"
    ENDED = "ended"


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


@dataclass
class LatencyTestResult:
    date_time: datetime
    target: str
    success: bool | None
    latency_ms: float | None
    error_message: str | None


@dataclass
class LatencyTestGroupResult:
    start_time: datetime | None
    end_time: datetime | None
    time_needed_sec: float | None
    any_success: bool | None
    group_success: bool | None
    test_results: list[LatencyTestResult] = field(default_factory=list)
    
    
@dataclass
class OutageDetectorResult:
    connection_state: str
    last_connection_test: datetime
    outage_change_state: str
    outage_start_time: datetime | None
    outage_end_time: datetime | None
    outage_duration_sec: float | None
    outage_started_group_id: int | None
    outage_ended_group_id: int | None
    
    
@dataclass
class LogEntry:
    date_time: datetime
    log_level: LogLevel
    log_type: LogType
    log_message: str
    related_object_type: str | None
    related_object_id: int | None
    details_json: str | None
    