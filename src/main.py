from runner import Runner
from config_manager import ConfigManager
from app_config import AppConfig
from database_manager import DatabaseManager
from outage_detector import OutageDetector
from app_logger import AppLogger
from models import LatencyTestGroupResult, LogType, OutageDetectorResult
import time

if __name__ == "__main__":
    config: AppConfig = ConfigManager.load_config()

    database_manager = DatabaseManager(config.database_config.path)

    AppLogger.initialize(
        config.log_config.enabled_console_log_levels,
        config.log_config.enabled_database_log_levels,
        database_manager,
    )

    database_manager.initialize_database()
    outage_detector = OutageDetector(3)
    
    AppLogger.info(LogType.SYSTEM, "Initialization completed")
    try:
        while True:       
            test_group: LatencyTestGroupResult = Runner.run_tests()
            group_id: int = database_manager.save_latency_test_group_result(test_group)
            detector_result: OutageDetectorResult = outage_detector.process_group_result(test_group, group_id)
            AppLogger.debug(LogType.SYSTEM, detector_result.connection_state)
            AppLogger.info(LogType.SYSTEM,"End ping test")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program exited")
