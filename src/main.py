from runner import Runner 
from config_manager import ConfigManager
from database_manager import DatabaseManager
import time

if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.load_config()
    database_manager = DatabaseManager(config.database_config.path)
    database_manager.initialize_database()
    runner = Runner()
           
    try:
        while True:
            test_group = runner.run_tests()
            database_manager.save_latency_group(test_group)
            print("ping_test")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Program exited")