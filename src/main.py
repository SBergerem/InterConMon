from runner import Runner 
from config_manager import ConfigManager
from database_manager import DatabaseManager

if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.load_config()
    database_manager = DatabaseManager(config.database_config.path)
    database_manager.initialize_database()
    
    runner = Runner()
    test_group = runner.run_tests()
    database_manager.save_latency_group(test_group)
    