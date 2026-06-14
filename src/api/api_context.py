from dataclasses import dataclass
from app_settings import AppSettings
from database.speed_test_result_repository import SpeedTestResultRepository
from database.log_entry_repository import LogEntryRepository
from database.latency_test_repository import LatencyTestRepository
from database.latency_test_group_repository import LatencyTestGroupRepository
from database.app_settings_repository import AppSettingsRepository
from database.outage_repository import OutageRepository
from database.connection_diagnosis_repository import ConnectionDiagnosisRepository


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
