from runner import Runner 
from config_manager import ConfigManager
from app_config import AppConfig


if __name__ == "__main__":
    config_manager = ConfigManager()
    config = config_manager.load_config()

    runner = Runner()
    runner.run_tests()
    