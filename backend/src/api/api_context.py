from dataclasses import dataclass
from api.services.log_service import LogService
from api.services.connection_diagnosis_service import ConnectionDiagnosisService
from api.services.latency_test_service import LatencyTestService


@dataclass
class ApiContext:
    latency_test_service: LatencyTestService
    latency_test_group_repository: LatencyTestGroupRepository
    log_service: LogService
    outage_repository: OutageRepository
    connection_diagnosis_service: ConnectionDiagnosisService
    speed_test_result_repository: SpeedTestResultRepository
    app_settings_repository: AppSettingsRepository
    app_settings: AppSettings
