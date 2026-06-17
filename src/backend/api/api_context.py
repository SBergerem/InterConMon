from dataclasses import dataclass
from backend.settings.app_settings import AppSettings
from backend.database.speed_test_result_repository import SpeedTestResultRepository
from backend.database.log_entry_repository import LogEntryRepository
from backend.database.latency_test_repository import LatencyTestRepository
from backend.database.latency_test_group_repository import LatencyTestGroupRepository
from backend.database.app_settings_repository import AppSettingsRepository
from backend.database.outage_repository import OutageRepository
from backend.database.connection_diagnosis_repository import ConnectionDiagnosisRepository


@dataclass
class ApiContext:
    latency_test_repository: LatencyTestRepository
    latency_test_group_repository: LatencyTestGroupRepository
    log_entry_repository: LogEntryRepository
    outage_repository: OutageRepository
    connection_diagnosis_repository: ConnectionDiagnosisRepository
    speed_test_result_repository: SpeedTestResultRepository
    app_settings_repository: AppSettingsRepository
    app_settings: AppSettings
