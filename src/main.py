from runner import Runner
from config_manager import ConfigManager
from app_start_config import AppStartConfig
from database_manager import DatabaseManager
from outage_detector import OutageDetector
from app_logger import AppLogger
from models import LogType, OutageChangeState 
import time

if __name__ == "__main__":
    config: AppStartConfig = ConfigManager.load_config()

    database_manager = DatabaseManager(config.database_config.path)

    AppLogger.initialize(
        config.log_config.enabled_console_log_levels,
        config.log_config.enabled_database_log_levels,
        database_manager,
    )

    database_manager.initialize_database()
    outage_detector = OutageDetector(3)
    
    AppLogger.info(LogType.SYSTEM, "Initialization completed", "main")
    try:
        while True:       
            test_group = Runner.run_tests()
            group_id = database_manager.save_latency_test_group_result(test_group)
            detector_result = outage_detector.process_group_result(test_group, group_id)
            if detector_result.outage_change_state == OutageChangeState.STARTED.value:
                AppLogger.info(LogType.SYSTEM, "Outage started", "main")
            if detector_result.outage_change_state == OutageChangeState.ENDED.value:
                outage_detection_result_id = database_manager.save_outage(detector_result)
                AppLogger.info(LogType.SYSTEM, "Outage ended", "main", related_object_type="OutageDetectorResult", related_object_id=outage_detection_result_id)

            AppLogger.debug(LogType.SYSTEM, detector_result.connection_state, "main")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program exited")
