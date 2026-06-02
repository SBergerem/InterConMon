from runner import Runner
from config_manager import ConfigManager
from database_manager import DatabaseManager
from outage_detector import OutageDetector
from app_logger import AppLogger
import time

if __name__ == "__main__":
    config = ConfigManager.load_config()
    AppLogger.set_log_level(config.log_config.log_level)
    database_manager = DatabaseManager(config.database_config.path)
    database_manager.initialize_database()
    outage_detector = OutageDetector(3)

    try:
        while True:
            print("Start ping test")
            test_group = Runner.run_tests()
            database_manager.save_latency_group(test_group)
            detector_result = outage_detector.process_group_result(test_group)
            print(detector_result)
            print("End ping test")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program exited")
