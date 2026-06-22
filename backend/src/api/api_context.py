from dataclasses import dataclass
from backend.src.settings.app_settings import AppSettings
from backend.src.database.speed_test_result_repository import SpeedTestResultRepository
from backend.src.database.log_entry_repository import LogEntryRepository
from backend.src.database.latency_test_repository import LatencyTestRepository
from backend.src.database.latency_test_group_repository import LatencyTestGroupRepository
from backend.src.database.app_settings_repository import AppSettingsRepository
from backend.src.database.outage_repository import OutageRepository
from backend.src.database.connection_diagnosis_repository import ConnectionDiagnosisRepository


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
