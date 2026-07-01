from dataclasses import dataclass
from api.services.log_service import LogService
from api.services.connection_diagnosis_service import ConnectionDiagnosisService
from api.services.latency_test_service import LatencyTestService
from api.services.latency_test_group_service import LatencyTestGroupService
from api.services.outage_service import OutageService
from api.services.speed_test_service import SpeedTestService
from api.services.app_settings_service import AppSettingsService
from settings.app_settings import AppSettings


@dataclass
class ApiContext:
    latency_test_service: LatencyTestService
    latency_test_group_service: LatencyTestGroupService
    log_service: LogService
    outage_service: OutageService
    connection_diagnosis_service: ConnectionDiagnosisService
    speed_test_result_service: SpeedTestService
    app_settings_service: AppSettingsService
    app_settings: AppSettings
