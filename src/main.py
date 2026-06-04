from runner import Runner
from config_manager import ConfigManager
from app_start_config import AppStartConfig
from database_manager import DatabaseManager
from outage_detector import OutageDetector
from app_logger import AppLogger
from models import (
    LatencyTestGroupResult,
    LogType,
    OutageChangeState,
    OutageDetectorResult,
)
from app_settings_manager import AppSettingsManager
import time

if __name__ == "__main__":
    settings_manager: AppSettingsManager | None = None
    
    try:
        config: AppStartConfig = ConfigManager.load_config()

        database_manager = DatabaseManager(config.database_config.path)
        database_manager.initialize_database()

        AppLogger.initialize(
            config.log_config.enabled_console_log_levels,
            config.log_config.enabled_database_log_levels,
            database_manager,
        )


        settings_manager = AppSettingsManager(database_manager)
        settings_manager.load_settings()
        outage_detector = OutageDetector(
            settings_manager.app_settings.latency_test_settings.interval_seconds
        )

        AppLogger.info(LogType.SYSTEM, "Initialization completed", "main", "main")

        Runner.prepare(settings_manager.app_settings.latency_test_settings.targets)

        while True:
            test_group: LatencyTestGroupResult | None = Runner.run_tests()

            if test_group is None:
                time.sleep(1)
                continue

            group_id: int = database_manager.save_latency_test_group_result(test_group)
            detector_result: OutageDetectorResult = (
                outage_detector.process_group_result(test_group, group_id)
            )
            if detector_result.outage_change_state == OutageChangeState.STARTED.value:
                AppLogger.info(LogType.SYSTEM, "Outage started", "main", "main")
            if detector_result.outage_change_state == OutageChangeState.ENDED.value:
                outage_detection_result_id: int = database_manager.save_outage(
                    detector_result
                )
                AppLogger.info(
                    LogType.SYSTEM,
                    "Outage ended",
                    "main",
                    "main",
                    related_object_type="OutageDetectorResult",
                    related_object_id=outage_detection_result_id,
                )

            AppLogger.debug(
                LogType.SYSTEM, detector_result.connection_state, "main", "main"
            )
            time.sleep(1)
    except KeyboardInterrupt:
        if settings_manager is not None:
            settings_manager.save_settings()
            print("Program exited")

    except Exception as ex:
        AppLogger.critical(LogType.SYSTEM, str(ex), "main", "main")
