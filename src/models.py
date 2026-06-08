from dataclasses import dataclass, field
from enum import Enum


class TestTargetType(Enum):
    UNKNOWN = "unknown"
    SERVER = "server"
    GATEWAY = "gateway"


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
    SCAN = "scan"
    GENERAL = "general"
    SYSTEM = "system"
    DATABASE = "database"
    OUTAGE = "outage"
    CONFIG = "config"
    SETTINGS = "settings"
    WEB = "web"
    EXPORT = "export"
    SECURITY = "security"


class LogLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    DEBUG = "debug"
    EXTENDED_DEBUG = "extended_debug"
    DETAILED_DEBUG = "detailed_debug"


@dataclass
class LatencyTest:
    id: int
    group_id: int
    date_time: str
    target: str
    test_target_type: str
    success: bool
    latency_ms: float | None
    error_message: str | None

    def set_latency_test_id(self, latency_test_id: int) -> None:
        self.id = latency_test_id


@dataclass
class LatencyTestGroup:
    id: int
    start_time: str
    end_time: str
    time_needed_sec: float
    any_success: bool
    group_success: bool
    test_target_type: str
    tests: list[LatencyTest] = field(default_factory=lambda: list[LatencyTest]())

    def set_group_id(self, group_id: int) -> None:
        self.id = group_id
        for tests in self.tests:
            tests.group_id = group_id


@dataclass
class OutageDetection:
    id: int
    connection_state: str
    last_connection_test: str
    change_state: str
    test_target_type: str
    start_time: str | None
    end_time: str | None
    duration_sec: float | None
    started_group_id: int | None
    ended_group_id: int | None

    def set_outage_id(self, outage_id: int) -> None:
        self.id = outage_id


@dataclass
class LogEntry:
    id: int
    date_time: str
    log_level: str
    log_type: str
    log_message: str
    class_name: str
    function_name: str
    related_object_type: str | None
    related_object_id: int | None
    details_json: str | None


@dataclass
class Setting:
    settings_name: str
    settings_json: str
