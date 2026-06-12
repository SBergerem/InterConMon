from dataclasses import dataclass, field
from enum import Enum


class TestTargetType(Enum):
    UNKNOWN = "unknown"
    SERVER = "server"
    GATEWAY = "gateway"


class ReachabilityState(Enum):
    UNKNOWN = "unknown"
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"


class OutageChangeState(Enum):
    NONE = "none"
    STARTED = "started"
    ENDED = "ended"


class NetworkDiagnosisType(Enum):
    UNKNOWN = "unknown"
    NO_EXTERNAL_CONNECTION = "no_external_connection"
    EXTERNAL_CONNECTION = "external_connection"
    NO_GATEWAY_CONNECTION = "no_gateway_connection"
    INTERNAL_NETWORK_ERROR = "internal_network_error"


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


class SpeedTestTool(Enum):
    UNKNOWN = "unknown"
    LIBRESPEED_CLI = "librespeed_cli"
    OOKLA_CLI = "ookla_cli"
    PYTHON_SPEEDTEST_CLI = "python_speedtest_cli"
    CLOUDFLARE_CLI = "cloudflare_cli"
    FAST_CLI = "fast_cli"


@dataclass
class BaseModel:
    id: int

    def set_id(self, id: int) -> None:
        self.id = id


@dataclass
class LatencyTest(BaseModel):
    group_id: int
    date_time: str
    target: str
    test_target_type: TestTargetType
    success: bool
    latency_ms: float | None
    error_message: str | None


@dataclass
class LatencyTestGroup(BaseModel):
    start_time: str
    end_time: str
    time_needed_sec: float
    any_success: bool
    group_success: bool
    test_target_type: TestTargetType
    tests: list[LatencyTest] = field(default_factory=lambda: list[LatencyTest]())

    def set_id(self, id: int) -> None:
        for test in self.tests:
            test.group_id = id

        super().set_id(id)


@dataclass
class Outage(BaseModel):
    reachability_state: ReachabilityState
    last_connection_test: str
    change_state: OutageChangeState
    test_target_type: TestTargetType
    start_time: str | None
    end_time: str | None
    duration_sec: float | None
    started_group_id: int | None
    started_group: LatencyTestGroup | None
    ended_group_id: int | None
    ended_group: LatencyTestGroup | None


@dataclass
class ConnectionDiagnosis(BaseModel):
    date_time: str
    network_diagnosis_type: NetworkDiagnosisType
    gateway_latency_test_group_id: int
    gateway_latency_test_group: LatencyTestGroup | None
    server_latency_test_group_id: int
    server_latency_test_group: LatencyTestGroup | None


@dataclass
class SpeedTestResult(BaseModel):
    date_time: str
    success: bool
    download_mbps: float | None
    upload_mbps: float | None
    ping_ms: float | None
    jitter_ms: float | None
    server_name: str | None
    server_location: str | None
    server_id: int | None
    server_url: str | None
    isp: str | None
    external_ip: str | None
    error_message: str | None
    duration_sec: float | None
    tool: SpeedTestTool


@dataclass
class LogEntry(BaseModel):
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
