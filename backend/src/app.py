from fastapi import FastAPI

from scanning.runner import Runner
from settings.app_start_config_manager import AppStartConfigManager
from settings.app_start_config import AppStartConfig
from database.database_manager import DatabaseManager
from utils.app_logger import AppLogger
from models.models import LogLevel, LogType
from settings.app_settings import AppSettings
from database.app_settings_repository import AppSettingsRepository
from database.database_initializer_repository import DatabaseInitializerRepository
from database.speed_test_result_repository import SpeedTestResultRepository
from database.latency_test_repository import LatencyTestRepository
from database.latency_test_group_repository import LatencyTestGroupRepository
from database.connection_diagnosis_repository import ConnectionDiagnosisRepository
from database.log_entry_repository import LogEntryRepository
from database.outage_repository import OutageRepository
from sqlite3 import Cursor
from api.api_app import create_app
from api.api_context import ApiContext
import uvicorn


class App:

    def _log_database_statement(
        self, class_name: str, function_name: str, outer_cursor: Cursor, details: dict[str, object] | None = None
    ) -> None:
        AppLogger.detailed_debug(
            LogType.DATABASE,
            "Executing SQL Statement",
            class_name,
            function_name,
            details=details,
            outer_cursor=outer_cursor,
        )

    def __init__(self) -> None:
        AppLogger.pre_initialize()

        AppLogger.info(LogType.SYSTEM, "Starting Initialization", "App", "__init__")
        self._app_start_config: AppStartConfig = AppStartConfigManager.load_config()
        self._database_manager = DatabaseManager(self._app_start_config.database_config.path)
        self._database_manager.set_logging_callback(self._log_database_statement)
        self._database_initializer_repository: DatabaseInitializerRepository = DatabaseInitializerRepository(self._database_manager)
        self._database_initializer_repository.initialize_database()

        enabled_console_log_levels: list[LogLevel] = self._app_start_config.log_config.enabled_console_log_levels
        enabled_database_log_levels: list[LogLevel] = self._app_start_config.log_config.enabled_database_log_levels
        AppLogger.initialize(enabled_console_log_levels, enabled_database_log_levels, self._database_manager)

        self._latency_test_repository: LatencyTestRepository = LatencyTestRepository(self._database_manager)
        self._latency_test_group_repository: LatencyTestGroupRepository = LatencyTestGroupRepository(self._database_manager)
        self._outage_repository: OutageRepository = OutageRepository(self._database_manager)
        self._connection_diagnosis_repository: ConnectionDiagnosisRepository = ConnectionDiagnosisRepository(self._database_manager)
        self._speed_test_result_repository: SpeedTestResultRepository = SpeedTestResultRepository(self._database_manager)
        self._app_settings_repository = AppSettingsRepository(self._database_manager)
        self._log_entry_repository = LogEntryRepository(self._database_manager)

        self._app_settings: AppSettings = self._app_settings_repository.load()

        self._runner = Runner(
            self._database_manager,
            self._latency_test_repository,
            self._latency_test_group_repository,
            self._outage_repository,
            self._connection_diagnosis_repository,
            self._speed_test_result_repository,
            self._app_settings,
        )

        self._api_context = ApiContext(
            self._latency_test_repository,
            self._latency_test_group_repository,
            self._log_entry_repository,
            self._outage_repository,
            self._connection_diagnosis_repository,
            self._speed_test_result_repository,
            self._app_settings_repository,
            self._app_settings,
        )
        self._api_app: FastAPI = create_app(self._api_context)

        AppLogger.info(LogType.SYSTEM, "Initialization complete", "App", "__init__")

    def start(self) -> None:
        try:
            self._runner.run()
            uvicorn.run(self._api_app, host="127.0.0.1", port=8000)
        except Exception as ex:
            AppLogger.critical(LogType.SYSTEM, str(ex), "App", "start_app")
        finally:
            self._runner.stop()
            self._app_settings_repository.save(self._app_settings)
            AppLogger.info(LogType.SYSTEM, "Program exited", "App", "start")
